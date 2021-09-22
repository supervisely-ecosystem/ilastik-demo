import os
import sys
from pathlib import Path
import supervisely_lib as sly


root_source_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {root_source_dir}")
sys.path.append(root_source_dir)

source_path = str(Path(sys.argv[0]).parents[0])
sly.logger.info(f"Source directory: {source_path}")
sys.path.append(source_path)

ui_sources_dir = os.path.join(source_path, "ui")
sys.path.append(ui_sources_dir)
sly.logger.info(f"Added to sys.path: {ui_sources_dir}")


import globals as g
import init_ui
import init_directories
import init_mode
import cache
import target_classes
import train
import predict
import settings
import init_ui_progress


## MAX
#@TODO: show modal window ValueError("Unknown level 'debug'. Supported levels: ['warning', 'info', 'error']")
#@TODO: create all features
#@TODO: hotkeys
#@TODO: add multiple images to train-headless

#@TODO: add slyfields with description to buttons?
#@TODO: Predict all unlabeled images button?
#@TODO: Videos support?
def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "team_id": g.team_id,
            "workspace_id": g.workspace_id,
            "task_id": g.task_id
        }
    )

    data = {}
    state = {}

    if g.mode == "Existing Project":
        initial_events = [{"state": None, "context": None, "command": "preprocessing_project"}]

    init_ui.init(data, state)
    g.my_app.compile_template(root_source_dir)
    if g.mode == "Create new Project":
        g.my_app.run(data=data, state=state)
    else:
        g.my_app.run(data=data, state=state, initial_events=initial_events)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
