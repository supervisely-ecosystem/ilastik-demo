import os
import json
import cache
import globals as g
import init_directories
import supervisely_lib as sly

def init(data, state):
    state["classesInfo"] = []
    selected_classes = get_classes()
    for obj_class in g.project_meta.obj_classes:
        if obj_class.name in selected_classes:
            state["classesInfo"].append(obj_class.to_json())


def get_classes():
    if g.mode == "Create new Project":
        selected_classes = json.loads(os.environ["modal.state.classes"].replace("'", '"'))
    else:
        ex_meta_json = sly.json.load_json_file(os.path.join(init_directories.proj_dir, "meta.json"))
        ex_meta = sly.ProjectMeta.from_json(ex_meta_json)
        selected_classes = [obj_class.name for obj_class in ex_meta.obj_classes]
    return selected_classes


def generate_machine_map(selected_classes):
    machine_map = {obj_class: [idx, idx, idx] for idx, obj_class in enumerate(selected_classes, start=1)}
    return machine_map
