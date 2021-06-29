import train
import settings
import globals as g
import target_classes


def init(data, state):
    data["ownerId"] = g.owner_id
    data["mode"] = g.mode

    if g.mode == "Create new Project":
        state["classifierStatus"] = g.classifier_status
    else:
        state["classifierStatus"] = g.remote_classifier_status

    state["loading"] = False
    state["tabName"] = "info"
    #"info" "train" "predict" "settings

    target_classes.init(data, state)
    train.init(data, state)
    settings.init(data, state)

