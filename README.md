# image_dataset

After clone the repo, pls go into the `image_dataset` folder. <br>
Run `python3 generate_tar_datasets.py` to generate tar data files. <br>
To train using dataset, run `python3 ./train.py -r ./images_dataset_ds -ds`. <br> 
To train using datapipe, run `python3 ./train.py -r ./images_dataset_tar -dp -n 10`.

TODO:
1. The iterable datapipe has no way to tell how many labels within the datapipe, so need to specify explicitly at the moment.
2. The iterable datapipe is not able to do a full shuffle, we do have a shuffle datapipe, but not full shuffle. This test script does not have a shuffle layer when
   using datapipe, you can do a manually shuffle by extracting all tar.gz into one place and re-tar them all together. I will add the shuffle layer back once we
   decide how to do iterable datapipe's shuffle.
