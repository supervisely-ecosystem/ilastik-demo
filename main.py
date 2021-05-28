import os
import numpy as np
import supervisely_lib as sly

from supervisely_lib.io.json import dump_json_file
from supervisely_lib.imaging.color import generate_rgb
from utils import generate_trained_project_file, predict_image, bw_to_color, draw_predicitons

## ENVIRONMENT
debug_dir = "/home/paul/Documents/Projects/ilastik/ilastik-master/sly-kit/src/debug"
os.environ['SERVER_ADDRESS'] = "http://78.46.75.100:38585/"
os.environ['API_TOKEN'] = "NPNY2NTeOtqgjI5IHgVZgHdBgpYa095xK8haVgPYauuJXaoIq3Jit7TAbiQLTZk08AcaJRWqtNpIQ2sDtsoeEMCsHjKlf1TNGDSexeyliiApSToSYbU2CHDFD50IYsdS"
api = sly.Api.from_env()

## CONSTANTS
TEAM_ID = 8
WORKSPACE_ID = 58
PROJECT_ID = 3708
DATASET_ID = 5700
TRAIN_IMAGES_IDS = [893408, 893411, 893413]
TEST_IMAGES_IDS = [893414, 893415, 893416]


## PROJECT
project = api.project.get_info_by_id(PROJECT_ID)
project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project.id))

## FOLDER STRUCTURE
proj_dir = os.path.join(debug_dir, project.name)
train_img_dir = os.path.join(proj_dir, 'train_img')
test_img_dir = os.path.join(proj_dir, 'test_img')
machine_masks_dir = os.path.join(proj_dir, 'masks_machine')

sly.fs.mkdir(train_img_dir)
sly.fs.mkdir(machine_masks_dir)
sly.fs.mkdir(os.path.join(proj_dir, 'predictions'))


path_to_trained_project = os.path.join(proj_dir,f'{project.name}.ilp')
predictions_dir = os.path.join(proj_dir, 'predictions')


## DOWNLOAD TRAIN DATA
train_images = api.image.get_info_by_id_batch(TRAIN_IMAGES_IDS)
test_images = api.image.get_info_by_id_batch(TEST_IMAGES_IDS)
test_anns = []

label_names = [obj_class.name for obj_class in project_meta.obj_classes]
label_colors = [obj_class.color for obj_class in project_meta.obj_classes]

machine_map = {obj_class.name: [idx, idx, idx] for idx, obj_class in enumerate(project_meta.obj_classes, start=1)}
machine_colors = [machine_color for machine_color in machine_map.values()]

for train_img, test_img in zip(train_images, test_images):
    api.image.download_path(train_img.id, os.path.join(train_img_dir, train_img.name))
    api.image.download_path(test_img.id, os.path.join(test_img_dir, test_img.name))
    test_ann_json = api.annotation.download(test_img.id).annotation
    test_ann = sly.Annotation.from_json(test_ann_json, project_meta)
    test_anns.append(test_ann)

    ann_json = api.annotation.download(train_img.id).annotation
    ann = sly.Annotation.from_json(ann_json, project_meta)
    machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
    for label in ann.labels:
        if not label.obj_class.name.endswith("_prediction"):
            label.geometry.draw(machine_mask, color=machine_map[label.obj_class.name])
    sly.image.write(os.path.join(machine_masks_dir, os.path.splitext(train_img.name)[0] + '.png'), machine_mask)


## TRAIN MODEL
generate_trained_project_file(path_to_trained_project, train_img_dir, machine_masks_dir, label_names, label_colors, 100)


## PREPARE DATA TO APPLY MODEL
pred_label_names = []
pred_label_colors = []
existing_colors = label_colors
for name in label_names:
    if name.endswith("_prediction"):
        pred_label_names.append(name)
    elif name not in pred_label_names and name + "_prediction" not in pred_label_names:
        pred_label_names.append(name + "_prediction")

    new_label_color = generate_rgb(existing_colors)
    pred_label_colors.append(new_label_color)
    existing_colors.append(new_label_color)


## APPLY MODEL
predicted_images_bw = predict_image(path_to_trained_project, test_img_dir, predictions_dir)
predicted_images_col = bw_to_color(predicted_images_bw, machine_colors, pred_label_colors)


## DISPLAY PREDICTIONS
draw_predicitons(api, TEST_IMAGES_IDS, PROJECT_ID, project_meta, test_anns, predicted_images_col, pred_label_names, pred_label_colors)
