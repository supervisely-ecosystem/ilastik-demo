import os
import json
import cache
import init_ui
import subprocess
import numpy as np
import globals as g
import supervisely_lib as sly


def init(data, state):
    state["newProjectName"] = None

@g.my_app.callback("save")
@sly.timeit
# @g.my_app.ignore_errors_and_show_dialog_window()
def save_project_to_team_files(api: sly.Api, task_id, context, state, app_logger):
    try:
        if f"{g.project.name}.ilp" in sly.fs.list_files(g.proj_dir):
            g.my_app.show_modal_window("Classifier not found. Please train model to save project.")
            api.task.set_field(task_id, "state.loading", False)
        else:
            sly.fs.remove_dir(g.test_dir)
            sly.fs.remove_dir(g.test_ann_dir)
            project_dir = g.proj_dir
            result_archive = os.path.join(g.my_app.data_dir, state["newProjectName"] + ".tar")

            meta_json = g.api.project.get_meta(g.project_id)
            meta = sly.ProjectMeta.from_json(meta_json)
            for obj_class in meta.obj_classes:
                if obj_class.name not in g.selected_classes:
                    meta = meta.delete_obj_class(obj_class.name)
            for tag_meta in meta.tag_metas:
                if tag_meta.name != g.prediction_tag_meta.name:
                    meta = meta.delete_tag_meta(tag_meta.name)

            sly.io.json.dump_json_file(meta.to_json(), os.path.join(g.proj_dir, 'meta.json'))
            sly.fs.archive_directory(project_dir, result_archive)
            app_logger.info("Result directory is archived")

            remote_archive_path = f"/ilastik/{state['newProjectName']}" + ".tar"

            if os.path.exists(remote_archive_path):
                g.my_app.show_modal_window(f"Project with name: {state['newProjectName']} already exists in Team Files. "
                                           f"Please select another name.")
                api.task.set_field(task_id, "state.loading", False)
            else:
                upload_progress = []
                def _print_progress(monitor, upload_progress):
                    if len(upload_progress) == 0:
                        upload_progress.append(sly.Progress(message=f"Upload {state['newProjectName']}",
                                                            total_cnt=monitor.len,
                                                            ext_logger=app_logger,
                                                            is_size=True))
                    upload_progress[0].set_current_value(monitor.bytes_read)

                file_info = api.file.upload(context["teamId"], result_archive, remote_archive_path,
                                            lambda m: _print_progress(m, upload_progress))
                app_logger.info("Uploaded to Team-Files: {!r}".format(file_info.full_storage_url))
                g.my_app.show_modal_window(f"Uploaded to Team-Files: {file_info.full_storage_url}")
                api.task.set_field(task_id, "state.loading", False)
    except Exception as e:
        api.task.set_field(task_id, "state.loading", False)
        raise e
