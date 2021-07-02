import supervisely_lib as sly
import globals as g
import init_ui

import train
import predict
import settings

import cache
import mode_selector
import target_classes
import init_ui_progress
import init_directories


## MAX
#@TODO: show modal window ValueError("Unknown level 'debug'. Supported levels: ['warning', 'info', 'error']")
#@TODO: create all features
#@TODO: hotkeys
#@TODO: add multiple images to train-headless


#@TODO: launch app from instance

#@TODO: existing project launch progress
#@TODO: save project progress bar

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
    init_ui.init(data, state)

    g.my_app.compile_template(g.root_source_dir)
    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
