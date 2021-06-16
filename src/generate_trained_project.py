from __future__ import print_function

import os
import numpy
import argparse
from ilastik import app
from lazyflow.graph import Graph
from lazyflow.roi import roiToSlice, roiFromShape
from lazyflow.classifiers import ParallelVigraRfLazyflowClassifierFactory
from lazyflow.operators.ioOperators import OpInputDataReader


def generate_trained_project_file(project_output_path, raw_data_dir, label_data_dir, label_names, label_colors,
                                  num_trees_total):
    # if not project_output_path or not raw_data_dir or not label_data_dir or not label_names or not label_colors:
    #    raise Exception("One or more of the required arguments are None")

    ilastik_args = app.parse_args([])
    print('project_output_path =', project_output_path)
    ilastik_args.new_project = project_output_path
    ilastik_args.headless = True
    ilastik_args.workflow = "Pixel Classification"

    shell = app.main(ilastik_args)
    data_selection_applet = shell.workflow.dataSelectionApplet

    raw_data_paths = sorted([os.path.join(raw_data_dir, raw_img_path) for raw_img_path in os.listdir(raw_data_dir)])
    label_data_paths = sorted(
        [os.path.join(label_data_dir, label_img_path) for label_img_path in os.listdir(label_data_dir)])
    assert len(raw_data_paths) == len(label_data_paths), "Number of label images must match number of raw images."

    data_selection_args, _ = data_selection_applet.parse_known_cmdline_args([],
                                                                            role_names=["Raw Data", "Prediction Mask"])
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


parser = argparse.ArgumentParser(description="ilastik trained project file")
# Output result:
# parser.add_argument("--save_ilp_to", default="", type=str, help="output path to ilastik project")
# Input data:
# parser.add_argument("--train_images_dir", default="", type=str, help="path to train images directory")
# parser.add_argument("--machine_masks_dir", default="", type=str, help="path to machine masks directory")
parser.add_argument("--label_names", default=[], type=str, help="class names in Supervisely project")
# parser.add_argument("--label_colors", default=[], type=list, help="class colors in Supervisely project")
# # Train settings:
# parser.add_argument("--num_tress_total", default=100, type=int, help="total number of trees")

args = parser.parse_args()
# generate_trained_project_file(args.save_ilp_to,
#                               args.train_images_dir,
#                               args.machine_masks_dir,
#                               args.label_names,
#                               args.label_colors,
#                               args.num_tress_total)
import json
# Given string
print("Given string", args.label_names)
print(type(args.label_names))
# String to list
res = json.loads(args.label_names)

print(res)
# /home/dmitry/storage/prj/ilastik-1.4.0b14-Linux/bin/python generate_trained_project.py \
#                                                            --save_ilp_to='/home/dmitry/storage/prj/app_debug_data'
# /home/dmitry/storage/prj/ilastik-1.4.0b14-Linux/bin/python generate_trained_project.py
# --save_ilp_to='/home/dmitry/storage/prj/app_debug_data'
# --train_images_dir=/home/paul/Documents/Projects/ilastik/ilastik-master/sly-kit/src/debug/ilastik/train_img
# --machine_masks_dir=/home/paul/Documents/Projects/ilastik/ilastik-master/sly-kit/src/debug/ilastik/masks_machine
# --label_names=['background', 'cucumber', 'kiwi', 'lemon']
# --label_colors=[[0, 0, 0], [0, 255, 0], [255, 0, 0],[255, 255, 0]]
# --num_trees_total=100