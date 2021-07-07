import os
import globals as g
import init_ui_progress
import init_directories
import supervisely_lib as sly
from functools import partial


def init(data, state):
    state["newProjectName"] = None


@g.my_app.callback("save")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def save_project_to_team_files(api: sly.Api, task_id, context, state, app_logger):
    try:
        if f"{g.project.name}.ilp" in sly.fs.list_files(init_directories.proj_dir):
            g.my_app.show_modal_window("Classifier not found. Please train model to save project.")
            api.task.set_field(task_id, "state.loading", False)
        else:
            sly.fs.remove_dir(init_directories.test_dir)
            project_dir = init_directories.proj_dir

            meta_json = g.api.project.get_meta(g.project_id)
            meta = sly.ProjectMeta.from_json(meta_json)
            for obj_class in meta.obj_classes:
                if obj_class.name not in ms.selected_classes:
                    meta = meta.delete_obj_class(obj_class.name)
            for tag_meta in meta.tag_metas:
                if tag_meta.name != g.prediction_tag_meta.name:
                    meta = meta.delete_tag_meta(tag_meta.name)
            sly.json.dump_json_file(meta.to_json(), os.path.join(init_directories.proj_dir, 'meta.json'))

            remote_dir_path = f"/ilastik/{state['newProjectName']}"
            if os.path.exists(remote_dir_path):
                g.my_app.show_modal_window(f"Project with name: {state['newProjectName']} already exists in Team Files. "
                                           f"Please select another name.")
                api.task.set_field(task_id, "state.loading", False)
            else:
                def upload_project_and_log_progress():
                    def upload_monitor(monitor, api: sly.Api, task_id, progress: sly.Progress):
                        if progress.total == 0:
                            progress.set(monitor.bytes_read, monitor.len, report=False)
                        else:
                            progress.set_current_value(monitor.bytes_read, report=False)
                        init_ui_progress._update_progress_ui(g.api, g.task_id, progress, 2)

                    progress = sly.Progress("Upload project directory with classifier to Team Files", 0, is_size=True)
                    progress_cb = partial(upload_monitor, api=g.api, task_id=g.task_id, progress=progress)
                    res_dir = g.api.file.upload_directory(g.team_id, project_dir, remote_dir_path,
                                                      progress_size_cb=progress_cb)
                    return res_dir
                res_dir = upload_project_and_log_progress()
                g.my_app.show_modal_window(f"Classifier has been saved to Team-Files: {res_dir}/")
                api.task.set_field(task_id, "state.loading", False)
    except Exception as e:
        api.task.set_field(task_id, "state.loading", False)
        raise e
