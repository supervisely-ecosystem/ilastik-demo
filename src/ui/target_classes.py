import os
import cache
import globals as g
import supervisely_lib as sly


def init(data, state):
    state["classesInfo"] = None
    if g.mode == "newProject":
        project_meta = cache.get_project_meta(g.project_id)
        project_meta = project_meta.from_json(project_meta.to_json())
        state["classesInfo"] = []
        for obj_class in project_meta.obj_classes:
            if obj_class.name in g.selected_classes:
                state["classesInfo"].append(obj_class.to_json())
    else:
        raise NotImplementedError()


def refresh_classes():
    g.refresh_meta()

    classes_info = []
    selected_classes = {}
    for obj_class in g.project_meta.obj_classes:
        obj_class: sly.ObjClass
        if obj_class.geometry_type in [sly.Bitmap, sly.AnyGeometry]:
            classes_info.append(obj_class.to_json())
            selected_classes[obj_class.name] = True

    fields = [
        {"field": "state.classesInfo", "payload": classes_info},
        {"field": "state.selectedClasses", "payload": selected_classes},
    ]
    g.api.app.set_fields(g.task_id, fields)