#import globals as g
from src import globals as g
import supervisely_lib as sly
from src.ui import target_classes
from src.ui import train


def init(data, state):
    data["ownerId"] = g.owner_id
    state["loading"] = False
    state["tabName"] = "info"
    #"info" "train" "predict" "settings

    target_classes.init(data, state)
    train.init(data, state)

    data["mode"] = g.mode
