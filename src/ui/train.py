import os
import cache
import datetime
import subprocess
import globals as g
import supervisely_lib as sly


def init(data, state):
    if g.mode == "Create new Project":
        data["trainSet"] = None
    else:
        data["trainSet"] = os.listdir(g.train_dir)
    state["toDelete"] = None


@g.my_app.callback("add_to_train")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def add_to_train(api: sly.Api, task_id, context, state, app_logger):
    try:
        image_id = context['imageId']
        project_id = context['projectId']

        cache.download_train(image_id, project_id)
        train_images = os.listdir(g.train_dir)
        fields = [
            {"field": "data.trainSet", "payload":  train_images},
            {"field": "state.loading", "payload":  False}
        ]
        api.app.set_fields(g.task_id, fields)
    except Exception as e:
        api.task.set_field(task_id, "state.loading", False)
        raise e


@g.my_app.callback("remove_from_train")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def remove_from_train(api: sly.Api, task_id, context, state, app_logger):
    try:
        image_name = state["toDelete"]
        train_images = os.listdir(g.train_dir)
        if image_name not in train_images:
            g.my_app.show_modal_window(f"Image: {image_name} is not in the training set")
            api.task.set_field(task_id, "state.loading", False)
        else:
            cache.remove_train_image_from_set(image_name)
            train_images.remove(image_name)
            if len(train_images) == 0:
                fields = [
                    {"field": "data.trainSet", "payload": None}
                ]
            else:
                fields = [
                    {"field": "data.trainSet", "payload":  train_images}
                ]
            api.app.set_fields(g.task_id, fields)
            api.task.set_field(task_id, "state.loading", False)
    except Exception as e:
        api.task.set_field(task_id, "state.loading", False)
        raise e


@g.my_app.callback("train_model")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def train_model(api: sly.Api, task_id, context, state, app_logger):
    try:
        images_paths = sly.fs.list_files(g.train_dir, sly.image.SUPPORTED_IMG_EXTS)
        masks = []
        for image_path in images_paths:
            mask_path = os.path.join(g.machine_masks_dir, sly.fs.get_file_name_with_ext(image_path))
            if not sly.fs.file_exists(mask_path):
                raise RuntimeError(f"Mask doesn't exist: {mask_path}")
            masks.append(mask_path)

        interpreter = "/ilastik-build/ilastik-1.4.0b14-Linux/bin/python"
        ilp_path = os.path.join(g.my_app.data_dir, g.proj_dir, f"{g.project.name}.ilp")

        train_script_path = os.path.join(g.source_path, "train_headless.py")
        train_cmd = f"{interpreter} " \
                    f"{train_script_path} " \
                    f"--project={ilp_path} "
        for image_path, mask_path in zip(images_paths, masks):
            train_cmd += f"--images='{image_path}' "
            train_cmd += f"--masks='{mask_path}' "

        sly.logger.info("Training", extra={"command": train_cmd})
        bash_out = subprocess.Popen([train_cmd], shell=True, executable="/bin/bash", stdout=subprocess.PIPE).communicate()
        output_log = bash_out[0]
        error_log = bash_out[1]
        g.my_app.show_modal_window("PixelClassification has been successfully trained", level="info")

        classifier_status = f"{g.project.name}.ilp {datetime.datetime.fromtimestamp(os.path.getmtime(ilp_path))}Z"
        fields = [
            {"field": "state.classifierStatus", "payload": classifier_status},
            {"field": "state.loading", "payload": False}
        ]
        api.app.set_fields(task_id, fields)
    except Exception as e:
        api.task.set_field(task_id, "state.loading", False)
        raise e
