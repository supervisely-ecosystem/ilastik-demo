import os
import sys
import json
import tarfile
from pathlib import Path
import supervisely_lib as sly


my_app = sly.AppService()

task_id = my_app.task_id
team_id = int(os.environ['context.teamId'])
owner_id = int(os.environ['context.userId'])
workspace_id = int(os.environ['context.workspaceId'])

mode = os.environ['modal.state.projectMode']
project_id = os.environ['modal.state.slyProjectId']

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


## FOLDER STRUCTURE
proj_dir = os.path.join(my_app.data_dir, project.name)
train_dir = os.path.join(proj_dir, 'train')
train_ann_dir = os.path.join(proj_dir, 'train_ann')
test_dir = os.path.join(proj_dir, 'test')
test_ann_dir = os.path.join(proj_dir, 'test_ann')
machine_masks_dir = os.path.join(proj_dir, 'masks_machine')


def init_directories():
    sly.fs.mkdir(proj_dir)
    sly.fs.clean_dir(proj_dir)
    sly.fs.mkdir(train_dir)
    sly.fs.mkdir(train_ann_dir)
    sly.fs.mkdir(test_dir)
    sly.fs.mkdir(test_ann_dir)
    sly.fs.mkdir(machine_masks_dir)


init_directories()


if mode == "newProject":
    selected_classes = json.loads(os.environ["modal.state.classes"])
    path_to_trained_project = os.path.join(proj_dir, f'{project.name}.ilp')
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
else:
    remote_classifier_path = os.environ["modal.state.classifierPath"]
    local_classifier_path = os.path.join(proj_dir, "existing_project.tar")
    api.file.download(team_id, remote_classifier_path, local_classifier_path)
    tr = tarfile.open(local_classifier_path)
    tr.extractall(proj_dir)
    sly.fs.silent_remove(local_classifier_path)
    for file in os.listdir(proj_dir):
        if file.endswith(".ilp"):
            os.rename(os.path.join(proj_dir, file), os.path.join(proj_dir, f"{project.name}.ilp"))
            path_to_trained_project = os.path.join(proj_dir, f"{project.name}.ilp")
            break

    ex_meta_json = sly.json.load_json_file(os.path.join(proj_dir, "meta.json"))
    ex_meta = sly.ProjectMeta.from_json(ex_meta_json)
    selected_classes = [obj_class.name for obj_class in ex_meta.obj_classes]
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
    project_meta = project_meta.merge(ex_meta)
    api.project.update_meta(project_id, project_meta.to_json())

machine_map = {obj_class: [idx, idx, idx] for idx, obj_class in enumerate(selected_classes, start=1)}
