import globals as g
import target_classes
import train
import settings


def init(data, state):
    data["ownerId"] = g.owner_id
    data["mode"] = g.mode

    state["loading"] = False
    state["tabName"] = "info"
    #"info" "train" "predict" "settings

    target_classes.init(data, state)
    train.init(data, state)
    settings.init(data, state)


