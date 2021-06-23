import supervisely_lib as sly
import globals as g
import target_classes


def init(data, state):
    data["ownerId"] = g.owner_id
    state["loading"] = False
    state["tabName"] = "settings"
    target_classes.init(data, state)
