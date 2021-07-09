import os
import json
import globals as g
import init_directories
import target_classes
import supervisely_lib as sly

def init(data, state):
    if g.mode == "Create new Project":
        state["classifierStatus"] = "No trained classifier detected"
        selected_classes = json.loads(os.environ["modal.state.classes"].replace("'", '"'))
        init_directories.init_directories()
        if len(selected_classes) < 2:
            raise Exception("At least 2 classes must be selected")
    else:
        state["classifierStatus"] = None
        init_directories.init_directories()


def init_ex_project():
    for file in os.listdir(init_directories.proj_dir):
        if file.endswith(".ilp"):
            g.api.app.set_field(g.task_id, "state.classifierStatus", file)
            os.rename(os.path.join(init_directories.proj_dir, file),
                      os.path.join(init_directories.proj_dir, f"{g.project.name}.ilp"))
            break
    ex_meta_json = sly.json.load_json_file(os.path.join(init_directories.proj_dir, "meta.json"))
    ex_meta = sly.ProjectMeta.from_json(ex_meta_json)
    selected_classes = [obj_class.name for obj_class in ex_meta.obj_classes]
    if len(selected_classes) < 2:
        raise Exception("At least 2 classes must be selected")
    g.project_meta = g.project_meta.merge(ex_meta)
    g.api.project.update_meta(g.project_id, g.project_meta.to_json())

    classes_info = []
    selected_classes = target_classes.get_classes()
    for obj_class in g.project_meta.obj_classes:
        if obj_class.name in selected_classes:
            classes_info.append(obj_class.to_json())

    train_set = os.listdir(init_directories.train_dir)
    fields = [
        {"field": "data.trainSet", "payload": train_set},
        {"field": "state.classesInfo", "payload": classes_info},
    ]
    g.api.task.set_fields(g.task_id, fields)
