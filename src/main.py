import os
import ui
import cv2
import subprocess
import numpy as np
import globals as g
import supervisely_lib as sly

import train
import predict

# imports to register callbacks
# import model_io
# from ui import train


#@TODO: remove utils.py
#@TODO: show modal window ValueError("Unknown level 'debug'. Supported levels: ['warning', 'info', 'error']")
#@TODO: remove auto objects before training
#@TODO: add prediction to bottom + add tag "auto" + add remove autolabels button
#@TODO: create all features
#@TODO: try catch errors
#@TODO: hotkeys
#@TODO: upload project to team files
#@TODO: buttons loading
#@TODO: add multiple images to train-headless

#@TODO: add message to train tab that model has been trained?
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
    ui.init(data, state)


    g.my_app.compile_template(g.root_source_dir)

    #sly.fs.clean_dir(g.my_app.data_dir) #@TODO: for debug
    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
