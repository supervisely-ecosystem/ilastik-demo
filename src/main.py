import globals as g
import supervisely_lib as sly

import init_ui

import train
import predict


#@TODO: remove utils.py
#@TODO: show modal window ValueError("Unknown level 'debug'. Supported levels: ['warning', 'info', 'error']")
#@TODO: create all features
#@TODO: try catch errors
#@TODO: hotkeys
#@TODO: buttons loading
#@TODO: add multiple images to train-headless

#@TODO: launch app from instance
#@TODO: create machine map from selected classes
#@TODO: ?add message to train tab that model has been trained?
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
