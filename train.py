from __future__ import print_function, division

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import torchvision
from torchvision import datasets, models, transforms
import time
import os
import copy


import argparse
import json
import torch.utils.data.datapipes as dp
from torch.utils.data.datapipes.utils.decoder import (
    basichandlers as decoder_basichandlers,
    imagehandler as decoder_imagehandler)

def train_model(model, criterion, optimizer, scheduler, dataloaders, dataset_sizes, device, num_epochs=25):
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        count = 0
        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for inputs, labels in dataloaders[phase]:
                count = count + 1
                inputs = inputs.to(device)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model


def get_transform_api():
    data_transforms = {
        'train': transforms.Compose([
             transforms.RandomResizedCrop(224),
             transforms.RandomHorizontalFlip(),
             transforms.ToTensor(),
             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
             transforms.Resize(256),
             transforms.CenterCrop(224),
             transforms.ToTensor(),
             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }
    return data_transforms


def prepare_datapipe(data_dir):
    from torch.utils.data import IterDataPipe
    class TransferDatapipe(IterDataPipe):
        def __init__(self, datapipe, phase, length = -1):
            super().__init__()
            self.datapipe = datapipe
            self.length = length
            self.transform = get_transform_api()[phase]
            self.classes = []
            self.class_ids = {}
            self.curr_id = -1

        def __iter__(self):
            for item in self.datapipe:
                label = item[1][1]['category_id']
                if label not in self.class_ids:
                    self.classes.append(label)
                    self.curr_id = self.curr_id + 1
                    self.class_ids[label] = self.curr_id
                yield (self.transform(item[0][1]), self.class_ids[label])


        def __len__(self):
            if self.length == -1:
                raise NotImplementedError
            return self.length

    datapipe1_t = dp.iter.ListDirFiles(data_dir, 'train*.tar.gz')
    datapipe2_t = dp.iter.LoadFilesFromDisk(datapipe1_t)
    datapipe3_t = dp.iter.ReadFilesFromTar(datapipe2_t)
    count = 0
    for x in datapipe3_t:
        count = count + 1
    datapipe4_t = dp.iter.RoutedDecoder(datapipe3_t, handlers=[decoder_imagehandler('pilrgb'), decoder_basichandlers])
    datapipe5_t = dp.iter.GroupByKey(datapipe4_t, group_size=2)
    datapipe6_t = TransferDatapipe(datapipe5_t, 'train', int(count/2))

    datapipe1_v = dp.iter.ListDirFiles(data_dir, 'val*.tar.gz')
    datapipe2_v = dp.iter.LoadFilesFromDisk(datapipe1_v)
    datapipe3_v = dp.iter.ReadFilesFromTar(datapipe2_v)
    count = 0
    for x in datapipe3_v:
        count = count + 1
    datapipe4_v = dp.iter.RoutedDecoder(datapipe3_v, handlers=[decoder_imagehandler('pilrgb'), decoder_basichandlers])
    datapipe5_v = dp.iter.GroupByKey(datapipe4_v, group_size=2)
    datapipe6_v = TransferDatapipe(datapipe5_v, 'val', int(count/2))

    return {'train': datapipe6_t, 'val': datapipe6_v}


def prepare_dataset(data_dir):
    data_transforms = get_transform_api()
    image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x]) for x in ['train', 'val']}
    return image_datasets


def main(args):

    root = args.root
    if args.dataset:
        image_datasets = prepare_dataset(root)
        num_of_classes = len(image_datasets['train'].classes)
        dl_shuffle = True
    else:
        image_datasets = prepare_datapipe(root)
        num_of_classes = args.num_of_labels
        assert num_of_classes
        dl_shuffle = False

    dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=1, shuffle=dl_shuffle, num_workers=1) for x in ['train', 'val']}
    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
    class_names = image_datasets['train'].classes

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model_ft = models.resnet18(pretrained=True)
    num_ftrs = model_ft.fc.in_features
    model_ft.fc = nn.Linear(num_ftrs, num_of_classes)
    model_ft = model_ft.to(device)
    criterion = nn.CrossEntropyLoss()
    # Observe that all parameters are being optimized
    optimizer_ft = optim.SGD(model_ft.parameters(), lr=0.001, momentum=0.9)
    # Decay LR by a factor of 0.1 every 7 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)

    model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler, dataloaders, dataset_sizes, device, num_epochs=5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Datapipe Benchmark Script")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-ds", "--dataset", action="store_true", help="use dataset for training if set")
    group.add_argument("-dp", "--datapipe", action="store_true", help="use datapipe for training if set")
    parser.add_argument("-r", "--root", required=True, help="root dir of images")
    parser.add_argument("-n", "--num_of_labels", type=int, help="must set if using datapipe")

    main(parser.parse_args())
