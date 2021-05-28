from __future__ import print_function

import os
import numpy
import h5py
import sys
import argparse
import vigra
import supervisely_lib as sly
from PIL import Image
from matplotlib import image
from ilastik import app
from ilastik.applets.dataExport.dataExportApplet import DataExportApplet
from ilastik.workflows.pixelClassification import PixelClassificationWorkflow
from ilastik.applets.dataSelection.opDataSelection import PreloadedArrayDatasetInfo
from ilastik.applets.pixelClassification.opPixelClassification import OpArgmaxChannel
from lazyflow.graph import Graph
from lazyflow.utility import PathComponents
from lazyflow.roi import roiToSlice, roiFromShape
from lazyflow.classifiers import ParallelVigraRfLazyflowClassifierFactory
from lazyflow.operators.ioOperators import OpInputDataReader, OpFormattedDataExport
from supervisely_lib.io.fs import get_file_name


def generate_trained_project_file(project_output_path, raw_data_dir, label_data_dir, label_names, label_colors, num_trees_total):
    ilastik_args = app.parse_args([])
    ilastik_args.new_project = project_output_path
    ilastik_args.headless = True
    ilastik_args.workflow = "Pixel Classification"

    shell = app.main(ilastik_args)
    data_selection_applet = shell.workflow.dataSelectionApplet

    raw_data_paths = sorted([os.path.join(raw_data_dir, raw_img_path) for raw_img_path in os.listdir(raw_data_dir)])
    label_data_paths = sorted([os.path.join(label_data_dir, label_img_path) for label_img_path in os.listdir(label_data_dir)])
    assert len(raw_data_paths) == len(label_data_paths), "Number of label images must match number of raw images."

    data_selection_args, _ = data_selection_applet.parse_known_cmdline_args([], role_names=["Raw Data", "Prediction Mask"])
    data_selection_args.raw_data = raw_data_paths
    data_selection_args.preconvert_stacks = True
    data_selection_applet.configure_operator_with_parsed_args(data_selection_args)

    ScalesList = [0.3, 0.7, 1, 1.6, 3.5, 5.0, 10.0]
    FeatureIds = [
        "GaussianSmoothing",
        "LaplacianOfGaussian",
        "GaussianGradientMagnitude",
        "DifferenceOfGaussians",
        "StructureTensorEigenvalues",
        "HessianOfGaussianEigenvalues",
    ]
    selections = numpy.zeros((len(FeatureIds), len(ScalesList)), dtype=bool)

    def set_feature(feature_id, scale):
        selections[FeatureIds.index(feature_id), ScalesList.index(scale)] = True

    set_feature("GaussianSmoothing", 0.3)
    set_feature("GaussianSmoothing", 1.0)
    set_feature("GaussianGradientMagnitude", 1.0)

    opFeatures = shell.workflow.featureSelectionApplet.topLevelOperator
    opFeatures.Scales.setValue(ScalesList)
    opFeatures.FeatureIds.setValue(FeatureIds)
    opFeatures.SelectionMatrix.setValue(selections)

    classifier_factory = ParallelVigraRfLazyflowClassifierFactory(num_trees_total)
    opPixelClassification = shell.workflow.pcApplet.topLevelOperator
    if classifier_factory is not None:
        opPixelClassification.ClassifierFactory.setValue(classifier_factory)

    cwd = os.getcwd()
    max_label_class = 0
    for lane, label_data_path in enumerate(label_data_paths):
        graph = Graph()
        opReader = OpInputDataReader(graph=graph)
        try:
            opReader.WorkingDirectory.setValue(cwd)
            opReader.FilePath.setValue(label_data_path)

            print("Reading label volume: {}".format(label_data_path))
            label_volume = opReader.Output[:].wait()
        finally:
            opReader.cleanUp()

        raw_shape = opPixelClassification.InputImages[lane].meta.shape
        if label_volume.ndim != len(raw_shape):
            assert label_volume.ndim == len(raw_shape) - 1
            label_volume = label_volume[..., None]

        max_label_class = max(max_label_class, label_volume.max())
        print("Applying label volume to lane #{}".format(lane))
        entire_volume_slicing = roiToSlice(*roiFromShape(label_volume.shape))
        opPixelClassification.LabelInputs[lane][entire_volume_slicing] = label_volume

    assert max_label_class > 1, "Not enough label classes were found in your label data."
    opPixelClassification.LabelNames.setValue(label_names)
    opPixelClassification.LabelColors.setValue(label_colors)
    opPixelClassification.FreezePredictions.setValue(False)
    _ = opPixelClassification.Classifier.value

    shell.projectManager.saveProject(force_all_save=False)


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


def change_grayscale_colors(input_img_path, ann, new_gray_colors):
    im = Image.open(input_img_path)
    npImage = numpy.array(Image.open(input_img_path))

    LUT = numpy.zeros(256, dtype=numpy.uint8)
    for idx, label_col in range(ann.labels):
        LUT[idx] = new_gray_colors[idx]

    pixels = LUT[npImage]
    result = Image.fromarray(pixels)
    result.save(input_img_path)


def bw_to_color(bw_img_paths, grayscale_colors, pred_label_colors):
    for bw_img_path in bw_img_paths:
        img = Image.open(bw_img_path)
        img = img.convert('RGB')
        pixels = img.load()
        assert len(grayscale_colors) == len(pred_label_colors)
        for grayscale, color in zip(grayscale_colors, pred_label_colors):
            for w in range(img.size[0]):
                for h in range(img.size[1]):
                    if pixels[w, h] == tuple(grayscale):
                        pixels[w, h] = tuple(color)
        img.save(bw_img_path)
    # Clean up dir
    #for file in os.listdir(os.path.dirname(bw_img_paths[0])):
    #    if not file.endswith(".png"):
    #        sly.fs.silent_remove(os.path.join(os.path.dirname(os.path.dirname(bw_img_paths[0])), file))
    return bw_img_paths


def draw_predicitons(api, test_img_ids, project_id, project_meta, test_anns, prediction_img_paths, prediction_labels, prediction_colors):
    predictions = []
    for test_img, test_ann in zip(prediction_img_paths, test_anns):
        if test_img.endswith(".png"):
            segmentation_img = sly.image.read(test_img)
            colored_img = segmentation_img.astype(numpy.uint8)
            for class_name, class_color in zip(prediction_labels, prediction_colors):
                mask = numpy.all(colored_img == class_color, axis=2)  # exact match (3-channel img & rgb color)
                bitmap = sly.Bitmap(data=mask)
                obj_class = sly.ObjClass(name=class_name, geometry_type=sly.Bitmap, color=class_color)
                test_ann = test_ann.add_label(sly.Label(bitmap, obj_class))
                if obj_class not in project_meta.obj_classes:
                    project_meta = project_meta.add_obj_class(obj_class)
                    api.project.update_meta(project_id, project_meta.to_json())

                colored_img[mask] = (0, 0, 0)
            if numpy.sum(colored_img) > 0:
                sly.logger.warn('Not all objects or classes are captured from source segmentation.')
            predictions.append(test_ann)

    api.annotation.upload_anns(test_img_ids, predictions)
