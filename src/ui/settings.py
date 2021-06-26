import os
import ui
import cache
import subprocess
import numpy as np
import globals as g
import supervisely_lib as sly


def init(data, state):
    data["newProjectName"] = None

@g.my_app.callback("save")
@sly.timeit
# @g.my_app.ignore_errors_and_show_dialog_window()
def save_project_to_team_files(api: sly.Api, task_id, context, state, app_logger):
    full_archive_name = str(g.project_id) + '_' + g.project.name
    full_result_dir_name = str(g.project_id) + '_' + g.project.name

    result_dir = os.path.join(g.my_app.data_dir, full_result_dir_name)
    result_archive = os.path.join(g.my_app.data_dir, full_archive_name)

    team_id = context["teamId"]
    sly.fs.archive_directory(result_dir, result_archive)
    app_logger.info("Result directory is archived")

    upload_progress = []
    remote_archive_path = "/ApplicationsData/Export-to-Pascal-VOC/{}/{}".format(task_id, full_archive_name)

    def _print_progress(monitor, upload_progress):
        if len(upload_progress) == 0:
            upload_progress.append(sly.Progress(message="Upload {!r}".format(full_archive_name),
                                                total_cnt=monitor.len,
                                                ext_logger=app_logger,
                                                is_size=True))
        upload_progress[0].set_current_value(monitor.bytes_read)

    file_info = api.file.upload(team_id, result_archive, remote_archive_path,
                                lambda m: _print_progress(m, upload_progress))
    app_logger.info("Uploaded to Team-Files: {!r}".format(file_info.full_storage_url))
    api.task.set_output_archive(task_id, file_info.id, full_archive_name, file_url=file_info.full_storage_url)