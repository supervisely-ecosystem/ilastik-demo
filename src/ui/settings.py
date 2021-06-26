import os
import ui
import cache
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
    if f"{g.project.name}.ilp" in sly.fs.list_files(g.proj_dir):
        g.my_app.show_modal_window("Classifier not found. Please train model to save project.")
    else:
        project_dir = g.proj_dir
        result_archive = os.path.join(g.my_app.data_dir, state["newProjectName"])

        sly.fs.archive_directory(project_dir, result_archive)
        app_logger.info("Result directory is archived")

        remote_archive_path = f"/ilastik/{state['newProjectName']}"

        if os.path.exists(remote_archive_path):
            g.my_app.show_modal_window(f"Project with name: {state['newProjectName']} already exists in Team Files. "
                                       f"Please select another name.")
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
