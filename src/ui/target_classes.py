import os
import cache
import globals as g
import supervisely_lib as sly


def init(data, state):
    state["classesInfo"] = []
    for obj_class in g.project_meta.obj_classes:
        if obj_class.name in g.selected_classes:
            state["classesInfo"].append(obj_class.to_json())
