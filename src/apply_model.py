from __future__ import print_function

import os
import numpy
import h5py
import sys
import argparse
import vigra
from PIL import Image
from matplotlib import image
from ilastik import app
from ilastik.applets.dataExport.dataExportApplet import DataExportApplet
from ilastik.workflows.pixelClassification import PixelClassificationWorkflow
from ilastik.applets.dataSelection.opDataSelection import PreloadedArrayDatasetInfo
from ilastik.applets.pixelClassification.opPixelClassification import OpArgmaxChannel
from lazyflow.graph import Graph
from lazyflow.utility import PathComponents
from lazyflow.operators.ioOperators import OpInputDataReader, OpFormattedDataExport
from supervisely_lib.io.fs import get_file_name


def predict_image(path_to_trained_project, test_img_dir, predictions_dir, segmentation=True):
    args = app.parse_args([])
    args.headless = True
    args.project = path_to_trained_project

    shell = app.main(args)
    assert isinstance(shell.workflow, PixelClassificationWorkflow)

    opPixelClassification = shell.workflow.pcApplet.topLevelOperator
    assert len(opPixelClassification.InputImages) > 0
    assert opPixelClassification.Classifier.ready()

    test_data_paths = sorted([os.path.join(test_img_dir, test_img_path) for test_img_path in os.listdir(test_img_dir)])
    prediction_paths = []
    for img in test_data_paths:
        img_name = get_file_name(img)+'.h5'
        input_data = image.imread(img)
        input_data = vigra.taggedView(input_data, "yxc")
        role_data_dict = [{"Raw Data": PreloadedArrayDatasetInfo(preloaded_array=input_data)}]
        predictions = shell.workflow.batchProcessingApplet.run_export(role_data_dict, export_to_array=True)
        prediction_path = os.path.join(predictions_dir, img_name)
        prediction_paths.append(prediction_path)
        internal_ds_name = 'segmentation'
        h5f = h5py.File(prediction_path, 'w')
        h5f.create_dataset(internal_ds_name, data=predictions)

    if segmentation:
        parser = DataExportApplet.make_cmdline_parser(argparse.ArgumentParser())
        parser.add_argument("--prediction_image_paths", help="Paths to prediction files.")
        parsed_args = parser.parse_args()
        parsed_args.prediction_image_paths = prediction_paths
        print(parsed_args.prediction_image_paths)
        for index, prediction_paths in enumerate(parsed_args.prediction_image_paths):
            path_comp = PathComponents(prediction_paths, os.getcwd())
            if not parsed_args.output_internal_path:
                parsed_args.output_internal_path = "segmentation"
            if path_comp.extension in PathComponents.HDF5_EXTS and path_comp.internalDatasetName == internal_ds_name:
                with h5py.File(path_comp.externalPath, "r") as f:
                    all_internal_paths = all_dataset_internal_paths(f)

                if len(all_internal_paths) == 1:
                    path_comp.internalPath = all_internal_paths[0]
                    parsed_args.prediction_image_paths[index] = path_comp.totalPath()
                elif len(all_internal_paths) == 0:
                    sys.stderr.write("Could not find any datasets in your input file:\n{}\n".format(prediction_paths))
                    sys.exit(1)
                else:
                    sys.stderr.write(
                        "Found more than one dataset in your input file:\n"
                        "{}\n".format(prediction_path)
                        + "Please specify the dataset name, e.g. /path/to/myfile.h5/internal/dataset_name\n"
                    )
                    sys.exit(1)
            predicted_images_bw = convert_predictions_to_segmentation(parsed_args.prediction_image_paths, parsed_args)
    return predicted_images_bw


def convert_predictions_to_segmentation(input_paths, parsed_export_args):
    graph = Graph()
    opReader = OpInputDataReader(graph=graph)
    opReader.WorkingDirectory.setValue(os.getcwd())

    opArgmaxChannel = OpArgmaxChannel(graph=graph)
    opArgmaxChannel.Input.connect(opReader.Output)

    opExport = OpFormattedDataExport(graph=graph)
    opExport.Input.connect(opArgmaxChannel.Output)

    DataExportApplet._configure_operator_with_parsed_args(parsed_export_args, opExport)
    last_progress = [-1]
    def print_progress(progress_percent):
        if progress_percent != last_progress[0]:
            last_progress[0] = progress_percent
            sys.stdout.write(" {}".format(progress_percent))

    opExport.progressSignal.subscribe(print_progress)
    predicted_images = []
    for input_path in input_paths:
        opReader.FilePath.setValue(input_path)
        input_pathcomp = PathComponents(input_path)
        opExport.OutputFilenameFormat.setValue(str(input_pathcomp.externalPath))

        output_path = opExport.ExportPath.value
        output_pathcomp = PathComponents(output_path)
        output_pathcomp.filenameBase = os.path.splitext(output_pathcomp.filenameBase)[0] + "_prediction"
        opExport.OutputFilenameFormat.setValue(str(output_pathcomp.externalPath))

        print("Exporting results to : {}".format(opExport.ExportPath.value))
        sys.stdout.write("Progress:")
        # Begin export
        opExport.run_export()
        predicted_image = convert_h5_seg_to_png_mask(str(output_pathcomp.externalPath))
        predicted_images.append(predicted_image)
        sys.stdout.write("\n")

    return predicted_images


def all_dataset_internal_paths(f):
    allkeys = []
    f.visit(allkeys.append)
    dataset_keys = [key for key in allkeys if isinstance(f[key], h5py.Dataset)]
    return dataset_keys


def convert_h5_seg_to_png_mask(path_to_h5_seg):
    hdf = h5py.File(path_to_h5_seg, 'r')
    dset = hdf["segmentation"][0]
    dset = dset.squeeze(2)
    im = Image.fromarray(dset.astype(numpy.uint8), 'L')
    path_to_h5_seg = os.path.splitext(path_to_h5_seg)[0] + ".png"
    im.save(path_to_h5_seg, format="png")
    return path_to_h5_seg


if __name__ == '__main__':
    prediction_parser = argparse.ArgumentParser(description="Output predictions for test images")
    prediction_parser.add_argument("--classifier_path",     default="", type=str, help="path to classifier")
    prediction_parser.add_argument("--test_images_dir",     default="", type=str, help="path to test images directory")
    prediction_parser.add_argument("--save_predictions_to", default="", type=str, help="output path to prediction images directory")

    pred_args = prediction_parser.parse_args()
    predicted_images_bw = predict_image(pred_args.classifier_path, pred_args.test_images_dir, pred_args.save_predictions_to)
