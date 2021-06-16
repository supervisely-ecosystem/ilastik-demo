import os
import supervisely_lib as sly

my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['context.projectId'])
debug_dir = os.environ['debug_dir']
api: sly.Api = my_app.public_api
TASK_ID = my_app.task_id

project = api.project.get_info_by_id(PROJECT_ID)
project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project.id))
label_names = [obj_class.name for obj_class in project_meta.obj_classes]
label_colors = [obj_class.color for obj_class in project_meta.obj_classes]
machine_map = {obj_class.name: [idx, idx, idx] for idx, obj_class in enumerate(project_meta.obj_classes, start=1)}
machine_colors = [machine_color for machine_color in machine_map.values()]

TRAIN_IMAGES_IDS = [899951, 899948, 899953]
TEST_IMAGES_IDS = [899950, 899952, 899949]

# FOLDER STRUCTURE
proj_dir = os.path.join(my_app.data_dir, project.name)  # os.path.join(g.debug_dir, g.project.name)
train_img_dir = os.path.join(proj_dir, 'train_img')
test_img_dir = os.path.join(proj_dir, 'test_img')
machine_masks_dir = os.path.join(proj_dir, 'masks_machine')
sly.fs.mkdir(train_img_dir)
sly.fs.mkdir(machine_masks_dir)
sly.fs.mkdir(os.path.join(proj_dir, 'predictions'))

path_to_trained_project = os.path.join(proj_dir, f'{project.name}.ilp')
predictions_dir = os.path.join(proj_dir, 'predictions')
