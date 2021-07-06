import globals as g
import mode_selector as ms


def init(data, state):
    state["classesInfo"] = []
    if g.mode == "Create new Project":
        for obj_class in g.project_meta.obj_classes:
            if obj_class.name in ms.selected_classes:
                state["classesInfo"].append(obj_class.to_json())
    else:
        for obj_class in ms.project_meta:
            if obj_class.name in ms.selected_classes:
                state["classesInfo"].append(obj_class.to_json())
