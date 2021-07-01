import os
import sys
from pathlib import Path
import supervisely_lib as sly


my_app = sly.AppService()

api: sly.Api = my_app.public_api


task_id = my_app.task_id
team_id = int(os.environ['context.teamId'])
owner_id = int(os.environ['context.userId'])
workspace_id = int(os.environ['context.workspaceId'])

mode = os.environ['modal.state.projectMode']
project_id = os.environ['modal.state.slyProjectId']

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
