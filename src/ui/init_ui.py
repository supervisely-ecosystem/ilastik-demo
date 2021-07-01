import os
import train
import settings
import target_classes
import globals as g
import mode_selector as ms


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
