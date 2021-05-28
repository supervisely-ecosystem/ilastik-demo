import os
import numpy as np
import supervisely_lib as sly

from supervisely_lib.io.json import dump_json_file
from supervisely_lib.imaging.color import generate_rgb
from utils import generate_trained_project_file, predict_image, bw_to_color, draw_predicitons

TEAM_ID = 8
WORKSPACE_ID = 58
PROJECT_ID = 3708
DATASET_ID = 5700
IMAGE_ID = 893411

os.environ['SERVER_ADDRESS'] = "http://78.46.75.100:38585/"
os.environ['API_TOKEN'] = "NPNY2NTeOtqgjI5IHgVZgHdBgpYa095xK8haVgPYauuJXaoIq3Jit7TAbiQLTZk08AcaJRWqtNpIQ2sDtsoeEMCsHjKlf1TNGDSexeyliiApSToSYbU2CHDFD50IYsdS"
api = sly.Api.from_env()

output_path = "/home/paul/Documents/Projects/ilastik/ilastik-master/sly-kit/src/debug"

image = api.image.get_info_by_id(IMAGE_ID)

project = api.project.get_info_by_id(PROJECT_ID)
project_meta_json = api.project.get_meta(project.id)
project_meta = sly.ProjectMeta.from_json(project_meta_json)

label_names = [obj_class.name for obj_class in project_meta.obj_classes]
label_colors = [obj_class.color for obj_class in project_meta.obj_classes]

## FOLDER STRUCTURE
debug_dir = output_path
proj_dir = os.path.join(debug_dir, project.name)
img_dir = os.path.join(proj_dir, 'img')
ann_dir = os.path.join(proj_dir, 'ann')
machine_masks_dir = os.path.join(proj_dir, 'masks_machine')
pixel_segm_dir = os.path.join(proj_dir, "pixel_segmentation")

path_to_trained_project = os.path.join(pixel_segm_dir,f'{image.name}.ilp')
path_to_predictions = os.path.join(pixel_segm_dir, 'predictions')
path_to_img_prediction = os.path.join(path_to_predictions, f'{image.name}.h5')

sly.fs.mkdir(img_dir)
sly.fs.mkdir(ann_dir)
sly.fs.mkdir(machine_masks_dir)
sly.fs.mkdir(pixel_segm_dir)
sly.fs.mkdir(os.path.join(pixel_segm_dir, 'predictions'))

# Process Image for prediction
api.image.download_path(IMAGE_ID, os.path.join(img_dir, image.name))
ann_json = api.annotation.download(IMAGE_ID).annotation
ann = sly.Annotation.from_json(ann_json, project_meta)
#dump_json_file(ann_json, os.path.join(ann_dir, f'{image.name}.json')) NO USE?

machine_map = {obj_class.name: [idx, idx, idx] for idx, obj_class in enumerate(project_meta.obj_classes, start=1)}
machine_colors = [machine_color for machine_color in machine_map.values()]
machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
for label in ann.labels:
    if not label.obj_class.name.endswith("_prediction"):
        label.geometry.draw(machine_mask, color=machine_map[label.obj_class.name])
dump_json_file(machine_map, os.path.join(proj_dir, 'obj_class_to_machine_color.json'), indent=2)

mask_img_name = os.path.splitext(image.name)[0] + '.png'
sly.image.write(os.path.join(machine_masks_dir, mask_img_name), machine_mask)
generate_trained_project_file(path_to_trained_project, img_dir, machine_masks_dir, label_names, label_colors, 100)

pred_label_names = []
pred_label_colors = []
existing_colors = label_colors
for name in label_names:
    if name.endswith("_prediction"):
        pred_label_names.append(name)
    else:
        pred_label_names.append(name + "_prediction")

    new_label_color = generate_rgb(existing_colors)
    pred_label_colors.append(new_label_color)
    existing_colors.append(new_label_color)


predicted_image_bw = predict_image(path_to_trained_project, img_dir, path_to_img_prediction)
predicted_image_col = bw_to_color(predicted_image_bw, machine_colors, pred_label_colors)

predictions = draw_predicitons(api, PROJECT_ID, project_meta, ann, predicted_image_col, pred_label_names, pred_label_colors)
api.annotation.upload_ann(IMAGE_ID, predictions)
