import supervisely_lib as sly
import globals as g
import target_classes


def init(data, state):
    data["ownerId"] = g.owner_id
    state["loading"] = False
    state["tabName"] = "train"
    target_classes.init(data, state)
