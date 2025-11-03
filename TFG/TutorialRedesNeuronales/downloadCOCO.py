#Solo hay que instalar fiftyone
import fiftyone as fo
import fiftyone.zoo as foz
from fiftyone import ViewField as F

import shutil

import os
import sys
from pathlib import Path

import yaml


def download_dataset(classes_selected: list, images_per_class):
    # Define dataset directories
    FiftyoneDataset_dir = 'datasets/FiftyoneDataset'  # "D:\projects\TFG\yolov5\datasets\FiftyoneDataset"
    export_dir = 'datasets/YOLOv5Dataset'  # "D:\projects\TFG\yolov5\datasets\YOLOv5Dataset_1" || ROOT / 'datasets/YOLOv5Dataset_1'

    # Delete already existing datasets with the same directory names if they exist
    if os.path.exists(FiftyoneDataset_dir):
        shutil.rmtree(FiftyoneDataset_dir)
    if os.path.exists(export_dir):
        shutil.rmtree(export_dir)

    # Load dataset in Fiftyone format
    name = "open-images-v7"
    splits = ["train", "validation"]
    label_types = ["detections"]
    classes = classes_selected  # classes_selected=["Tin can", "Apple", "Pear"]
    max_samples = len(classes_selected)*images_per_class

    dataset = foz.load_zoo_dataset(
        name,
        #dataset_dir=FiftyoneDataset_dir,
        splits=splits,
        label_types=label_types,
        classes=classes,
        shuffle=True,
        max_samples=max_samples,
    )

    # Export dataset in Fiftyone format to YOLOv5 format
    view = dataset.filter_labels("ground_truth", F("label").is_in(classes))
    label_field = "ground_truth"

    for split in splits:
        split_view = view.match_tags(split)
        if split == "validation":
            split = "val"
        split_view.export(
            export_dir=export_dir,
            dataset_type=fo.types.YOLOv5Dataset,
            label_field=label_field,
            split=split,
            classes=classes,
        )

    # Remove the dataset in Fiftyone format, we don't need it, we only need dataset in YOLOv5 format
    # shutil.rmtree(FiftyoneDataset_dir)

    # Generate the dataset.yaml
    generate_yaml(classes_selected, export_dir)

    # Convert the dataset to a Zip folder
    shutil.make_archive(export_dir, 'zip', 'datasets/', 'YOLOv5Dataset')

    return export_dir+'/dataset.yaml'

def generate_yaml(classes_selected, dataset_dir):
    with open(dataset_dir+'/dataset.yaml', 'w') as file:
        file.write('names:\n')
        for i, object in enumerate(classes_selected):
            file.write(' '+str(i)+': '+str(object)+'\n')
        file.write('path: ../YOLOv5Dataset\n')
        file.write('train: ./images/train/\n')
        file.write('val: ./images/val/\n')


if __name__ == '__main__':
    # Setting parameters
    objects_selected = ["Bird","Horse"]
    images_per_class = 2000

    # Downloading the dataset
    download_dataset(classes_selected=objects_selected, images_per_class=images_per_class)
