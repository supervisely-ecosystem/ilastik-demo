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
project = api.project.get_info_by_id(project_id)
project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

prediction_tag_meta = sly.TagMeta("ilastik_prediction", sly.TagValueType.NONE)
prediction_tag = sly.Tag(prediction_tag_meta)

tag_meta = project_meta.get_tag_meta(prediction_tag_meta.name)
if tag_meta is None:
    project_meta = project_meta.add_tag_meta(prediction_tag_meta)
    api.project.update_meta(project_id, project_meta.to_json())