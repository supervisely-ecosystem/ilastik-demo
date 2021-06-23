import supervisely_lib as sly
import globals as g
import target_classes
import train


def init(data, state):
    data["ownerId"] = g.owner_id
    state["loading"] = False
    state["tabName"] = "info"
    target_classes.init(data, state)
    train.init(data, state)

    data["mode"] = g.mode
