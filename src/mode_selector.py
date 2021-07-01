import os
import json
import tarfile
import globals as g
import init_directories
import init_ui_progress
import supervisely_lib as sly


if g.mode == "Create new Project":
    classifier_path = None
    classifier_status = "No trained classifier detected"
    selected_classes = json.loads(os.environ["modal.state.classes"])
    path_to_trained_project = os.path.join(init_directories.proj_dir, f'{g.project.name}.ilp')
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
else:
    remote_classifier_path = os.environ["modal.state.classifierPath"]
    remote_classifier_info = g.api.file.get_info_by_path(g.team_id, remote_classifier_path)
    local_classifier_path = os.path.join(init_directories.proj_dir, "existing_project.tar")
    progress_upload_cb = init_ui_progress.get_progress_cb(g.api, g.task_id, 1,
                                                 "Preparing project",
                                                 g.api.file.get_info_by_path(g.team_id, remote_classifier_path).sizeb,
                                                 is_size=True,
                                                 func=init_ui_progress.set_progress)
    g.api.file.download(g.team_id, remote_classifier_path, local_classifier_path)

    tr = tarfile.open(local_classifier_path)
    tr.extractall(init_directories.proj_dir)
    sly.fs.silent_remove(local_classifier_path)
    for file in os.listdir(init_directories.proj_dir):
        if file.endswith(".ilp"):
            remote_classifier_status = f"{file} {remote_classifier_info.updated_at}"
            os.rename(os.path.join(init_directories.proj_dir, file), os.path.join(init_directories.proj_dir, f"{g.project.name}.ilp"))
            path_to_trained_project = os.path.join(init_directories.proj_dir, f"{g.project.name}.ilp")
            break

    ex_meta_json = sly.json.load_json_file(os.path.join(init_directories.proj_dir, "meta.json"))
    ex_meta = sly.ProjectMeta.from_json(ex_meta_json)
    selected_classes = [obj_class.name for obj_class in ex_meta.obj_classes]
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
    project_meta = g.project_meta.merge(ex_meta)
    g.api.project.update_meta(g.project_id, project_meta.to_json())
    g.api.task.set_field(g.task_id, "state.loading", False)
    
machine_map = {obj_class: [idx, idx, idx] for idx, obj_class in enumerate(selected_classes, start=1)}
