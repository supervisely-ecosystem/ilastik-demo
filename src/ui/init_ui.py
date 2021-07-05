import os
import train
import settings
import globals as g
import target_classes
import mode_selector as ms
import init_ui_progress

def init(data, state):
    data["ownerId"] = int(os.environ['context.userId'])
    data["mode"] = g.mode

    if g.mode == "Create new Project":
        state["classifierStatus"] = ms.classifier_status
    else:
        state["classifierStatus"] = ms.remote_classifier_status

    state["loading"] = False
    state["tabName"] = "info"
    #"info" "train" "predict" "settings

    target_classes.init(data, state)
    train.init(data, state)
    settings.init(data, state)
    init_ui_progress.init_progress(data, state)
