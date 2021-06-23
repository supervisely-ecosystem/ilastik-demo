import supervisely_lib as sly
import globals as g


def init(data, state):
    state["classesInfo"] = None
    data["disabledClasses"] = None
    state["selectedClasses"] = None


def refresh_classes():
    g.refresh_meta()

    classes_info = []
    disabled_classes = {}
    selected_classes = {}
    for obj_class in g.project_meta.obj_classes:
        obj_class: sly.ObjClass
        classes_info.append(obj_class.to_json())
        if obj_class.geometry_type in [sly.Bitmap, sly.AnyGeometry]:
            disabled_classes[obj_class.name] = False
            selected_classes[obj_class.name] = True
        else:
            disabled_classes[obj_class.name] = True
            selected_classes[obj_class.name] = False

    fields = [
        {"field": "state.classesInfo", "payload": classes_info},
        {"field": "data.disabledClasses", "payload": disabled_classes},
        {"field": "state.selectedClasses", "payload": selected_classes},
    ]
    g.api.app.set_fields(g.task_id, fields)