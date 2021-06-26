import os
import sys
import json
from pathlib import Path
import supervisely_lib as sly

my_app = sly.AppService()

task_id = my_app.task_id
team_id = int(os.environ['context.teamId'])
owner_id = int(os.environ['context.userId'])
workspace_id = int(os.environ['context.workspaceId'])

mode = os.environ['modal.state.projectMode']
project_id = os.environ['modal.state.slyProjectId']

if mode == "newProject":
    selected_classes = os.environ["modal.state.classes"]
    # selected_classes = json.loads(os.environ["modal.state.classes"])
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
else:
    project_id = None
    selected_classes = None


api: sly.Api = my_app.public_api

root_source_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {root_source_dir}")
sys.path.append(root_source_dir)

source_path = str(Path(sys.argv[0]).parents[0])
sly.logger.info(f"Source directory: {source_path}")
sys.path.append(source_path)

ui_sources_dir = os.path.join(source_path, "ui")
sys.path.append(ui_sources_dir)
sly.logger.info(f"Added to sys.path: {ui_sources_dir}")


project = api.project.get_info_by_id(project_id)
project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

prediction_tag_meta = sly.TagMeta("ilastik_prediction", sly.TagValueType.NONE)
prediction_tag = sly.Tag(prediction_tag_meta)


label_names = [obj_class.name for obj_class in project_meta.obj_classes]
# label_colors = [obj_class.color for obj_class in project_meta.obj_classes]

machine_map = {obj_class.name: [idx, idx, idx] for idx, obj_class in enumerate(project_meta.obj_classes, start=1)}
# machine_colors = [machine_color for machine_color in machine_map.values()]

## FOLDER STRUCTURE
proj_dir = os.path.join(my_app.data_dir, project.name)
train_dir = os.path.join(proj_dir, 'train')
train_ann_dir = os.path.join(proj_dir, 'train_ann')
test_dir = os.path.join(proj_dir, 'test')
test_ann_dir = os.path.join(proj_dir, 'test_ann')
predictions_dir = os.path.join(proj_dir, 'predictions')
machine_masks_dir = os.path.join(proj_dir, 'masks_machine')

# cache_dir = os.path.join(proj_dir, 'cache')
# cache_img_dir = os.path.join(proj_dir, 'cache')
# cache_ann_dir = os.path.join(proj_dir, 'cache')


def init_directories():
    sly.fs.mkdir(proj_dir)
    sly.fs.clean_dir(proj_dir)
    sly.fs.mkdir(train_dir)
    sly.fs.mkdir(train_ann_dir)
    sly.fs.mkdir(test_dir)
    sly.fs.mkdir(test_ann_dir)
    sly.fs.mkdir(predictions_dir)
    sly.fs.mkdir(machine_masks_dir)
    # sly.fs.mkdir(cache_dir)


init_directories()
path_to_trained_project = os.path.join(proj_dir, f'{project.name}.ilp')
# pred_label_names, pred_label_colors = prepare_data()


# from supervisely_lib.imaging.color import generate_rgb
# def prepare_data():
#     # PREPARE DATA TO APPLY MODEL
#     pred_label_names = []
#     pred_label_colors = []
#     existing_colors = list(label_colors)
#     for name in label_names:
#         pred_label_names.append(name)
#
#         new_label_color = generate_rgb(existing_colors)
#         pred_label_colors.append(new_label_color)
#         existing_colors.append(new_label_color)
#     return pred_label_names, pred_label_colors
