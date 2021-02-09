from imagefolder import ImageFolder


im = ImageFolder([
    './images_dataset_ds/train/011k07',
    './images_dataset_ds/train/015x4r',
    './images_dataset_ds/train/01bqk0',
    './images_dataset_ds/train/01jfm_',
    './images_dataset_ds/train/01s105'])

im.to_tar('./images_dataset_tar/train_images_1.tar.gz')

im = ImageFolder([
    './images_dataset_ds/val/011k07',
    './images_dataset_ds/val/015x4r',
    './images_dataset_ds/val/01bqk0',
    './images_dataset_ds/val/01jfm_',
    './images_dataset_ds/val/01s105'])

im.to_tar('./images_dataset_tar/val_images_1.tar.gz')

im = ImageFolder([
    './images_dataset_ds/train/021sj1',
    './images_dataset_ds/train/02d9qx',
    './images_dataset_ds/train/02s195',
    './images_dataset_ds/train/034c16',
    './images_dataset_ds/train/03l9g'])

im.to_tar('./images_dataset_tar/train_images_2.tar.gz')

im = ImageFolder([
    './images_dataset_ds/val/021sj1',
    './images_dataset_ds/val/02d9qx',
    './images_dataset_ds/val/02s195',
    './images_dataset_ds/val/034c16',
    './images_dataset_ds/val/03l9g'])

im.to_tar('./images_dataset_tar/val_images_2.tar.gz')
