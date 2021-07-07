import os
import json
import globals as g
import init_directories
# import init_ui_progress
import supervisely_lib as sly

if g.mode == "Create new Project":
    classifier_path = None
    classifier_status = "No trained classifier detected"
    #state["classifierStatus"] = "No trained classifier detected"
    selected_classes = json.loads(os.environ["modal.state.classes"].replace("'", '"'))
    init_directories.init_directories()
    path_to_trained_project = os.path.join(init_directories.proj_dir, f'{g.project.name}.ilp')
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
else:
    local_classifier_path = init_directories.proj_dir
    if sly.fs.dir_exists(local_classifier_path):
        sly.fs.remove_dir(local_classifier_path)
    remote_classifier_path = os.environ["modal.state.classifierPath"]

    dir_size = 0
    detected = False
    file_infos = g.api.file.list2(g.team_id, remote_classifier_path)
    for file_info in file_infos:
        dir_size += file_info.sizeb
        if file_info.name.endswith('.ilp'):
            date = file_info.updated_at
            detected = True
    if detected is False:
        raise Exception("No trained classifier detected")

    # progress_upload_cb = init_ui_progress.get_progress_cb(g.api,
    #                                                       g.task_id, 1,
    #                                                       "Preparing project",
    #                                                       total=dir_size,
    #                                                       is_size=True)
    g.api.file.download_directory(g.team_id,
                                  remote_classifier_path,
                                  local_classifier_path)
                                  # ,progress_cb=progress_upload_cb)
    sly.fs.mkdir(init_directories.test_dir)

    for file in os.listdir(init_directories.proj_dir):
        if file.endswith(".ilp"):
            remote_classifier_status = f"{file} {date}"
            os.rename(os.path.join(init_directories.proj_dir, file), os.path.join(init_directories.proj_dir, f"{g.project.name}.ilp"))
            path_to_trained_project = os.path.join(init_directories.proj_dir, f"{g.project.name}.ilp")
            break

    ex_meta_json = sly.json.load_json_file(os.path.join(init_directories.proj_dir, "meta.json"))
    ex_meta = sly.ProjectMeta.from_json(ex_meta_json)
    selected_classes = [obj_class.name for obj_class in ex_meta.obj_classes]
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
    g.project_meta = g.project_meta.merge(ex_meta)
    g.api.project.update_meta(g.project_id, g.project_meta.to_json())
    g.api.task.set_field(g.task_id, "state.loading", False)

machine_map = {obj_class: [idx, idx, idx] for idx, obj_class in enumerate(selected_classes, start=1)}

# def reset_info(data, state):
#     if g.mode == "Existing project":
#         fields = [
#             {"field": "state.classesInfo", "payload": []},
#             {"field": "state.trainSet", "payload": []},
#             {"field": "state.classifierStatus", "payload": remote_classifier_status},
#             {"field": "state.newProjectName", "payload": None}
#         ]
#         g.api.app.set_fields(g.task_id, fields)
#         sly.logger.debug(f"AFTER RUN DATA: {data}")
#         sly.logger.debug(f"AFTER RUN STATE: {state}")
