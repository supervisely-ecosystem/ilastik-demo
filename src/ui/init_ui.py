import os
import train
import cache
import settings
import init_mode
import globals as g
import target_classes
import init_ui_progress


def init(data, state):
    data["ownerId"] = int(os.environ['context.userId'])
    data["mode"] = g.mode

    state["loading"] = False
    state["prepare"] = False
    state["tabName"] = "info"  # "info" "train" "predict" "settings"

    if g.mode == "Create new Project":
        state["classifierStatus"] = None
        state["prepare"] = False

    else:
        state["classifierStatus"] = None
        state["prepare"] = True


    init_mode.init(data, state)
    init_ui_progress.init_progress(data, state)
    target_classes.init(data, state)
    train.init(data, state)
    settings.init(data, state)
