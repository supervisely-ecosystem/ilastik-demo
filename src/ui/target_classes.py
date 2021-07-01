import globals as g
import mode_selector as ms


def init(data, state):
    state["classesInfo"] = []
    for obj_class in g.project_meta.obj_classes:
        if obj_class.name in ms.selected_classes:
            state["classesInfo"].append(obj_class.to_json())
