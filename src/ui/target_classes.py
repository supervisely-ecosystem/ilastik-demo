import os
import json
import cache
import globals as g
import init_directories
import supervisely_lib as sly


def init(data, state):
    if g.mode == "Create new Project":
        state["classesInfo"] = []
        selected_classes = get_classes()
        for obj_class in g.project_meta.obj_classes:
            if obj_class.name in selected_classes:
                state["classesInfo"].append(obj_class.to_json())
    else:
        state["classesInfo"] = None


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

@g.my_app.callback("synchronise_meta")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def synchronise_meta(api: sly.Api, task_id, context, state, app_logger):
    try:
        src_project_id = g.project_id
        src_meta_json = g.api.project.get_meta(src_project_id)
        src_meta = sly.ProjectMeta.from_json(src_meta_json)
        selected_classes = get_classes()
        for obj_class in src_meta.obj_classes:
            if obj_class.name not in selected_classes:
                src_meta = src_meta.delete_obj_class(obj_class.name)
        for tag_meta in src_meta.tag_metas:
            if tag_meta.name != g.prediction_tag_meta.name:
                src_meta = src_meta.delete_tag_meta(tag_meta.name)

        dst_project_id = context['projectId']
        dst_meta_json = g.api.project.get_meta(dst_project_id)
        dst_meta = sly.ProjectMeta.from_json(dst_meta_json)
        meta = src_meta.merge(dst_meta)
        g.api.project.update_meta(dst_project_id, meta.to_json())
        api.task.set_field(task_id, "state.loading", False)
    except Exception as e:
        api.task.set_field(task_id, "state.loading", False)
        raise e
