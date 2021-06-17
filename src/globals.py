import os
import sys
from pathlib import Path
import supervisely_lib as sly

from supervisely_lib.imaging.color import generate_rgb


def prepare_data():
    # PREPARE DATA TO APPLY MODEL
    pred_label_names = []
    pred_label_colors = []
    existing_colors = list(label_colors)
    for name in label_names:
        pred_label_names.append(name)

        new_label_color = generate_rgb(existing_colors)
        pred_label_colors.append(new_label_color)
        existing_colors.append(new_label_color)
    return pred_label_names, pred_label_colors


my_app = sly.AppService()
sly.fs.clean_dir(my_app.data_dir)  #@TODO: for debug

task_id = my_app.task_id
team_id = int(os.environ['context.teamId'])
workspace_id = int(os.environ['context.workspaceId'])
project_id = int(os.environ['context.projectId'])
owner_id = int(os.environ['context.userId'])

#debug_dir = os.environ['debug_dir']
api: sly.Api = my_app.public_api

root_source_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {root_source_dir}")
sys.path.append(root_source_dir)

source_path = str(Path(sys.argv[0]).parents[0])
sly.logger.info(f"Source directory: {source_path}")
sys.path.append(source_path)


project = api.project.get_info_by_id(project_id)
project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project.id))
label_names = [obj_class.name for obj_class in project_meta.obj_classes]
label_colors = [obj_class.color for obj_class in project_meta.obj_classes]
machine_map = {obj_class.name: [idx, idx, idx] for idx, obj_class in enumerate(project_meta.obj_classes, start=1)}
machine_colors = [machine_color for machine_color in machine_map.values()]

# TRAIN_IMAGES_IDS = [899951, 899948, 899953]
# TEST_IMAGES_IDS = [899950, 899952, 899949]

# FOLDER STRUCTURE
proj_dir = os.path.join(my_app.data_dir, project.name)  # os.path.join(g.debug_dir, g.project.name)
cache_dir = os.path.join(proj_dir, 'cache')
train_dir = os.path.join(proj_dir, 'train')
test_dir = os.path.join(proj_dir, 'test')
predictions_dir = os.path.join(proj_dir, 'predictions')
machine_masks_dir = os.path.join(proj_dir, 'masks_machine')

sly.fs.mkdir(cache_dir)
sly.fs.mkdir(train_dir)
sly.fs.mkdir(test_dir)
sly.fs.mkdir(predictions_dir)
sly.fs.mkdir(machine_masks_dir)

path_to_trained_project = os.path.join(proj_dir, f'{project.name}.ilp')
predictions_dir = os.path.join(proj_dir, 'predictions')
pred_label_names, pred_label_colors = prepare_data()
