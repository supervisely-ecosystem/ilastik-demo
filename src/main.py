import os
import numpy as np
import cv2
import subprocess
import supervisely_lib as sly
import ui
import globals as g

import train

# imports to register callbacks
# import model_io
# from ui import train


# def download_data(image_id, is_test=False):
#     if is_test is True:
#         img_dir = g.test_dir
#         tag_meta = g.project_meta.get_tag_meta("ilastik_prediction")
#         if tag_meta is None:
#             project_meta = g.project_meta.add_tag_meta(g.prediciton_tag_meta)
#             g.api.project.update_meta(g.project.id, project_meta.to_json())
#     else:
#         img_dir = g.train_dir
#
#     info = g.api.image.get_info_by_id(image_id)
#
#     cache_path = os.path.join(g.cache_dir, f"{image_id}{sly.fs.get_file_ext(info.name)}")
#     cache_path = os.path.splitext(cache_path)[0] + '.png'
#     if not sly.fs.file_exists(cache_path):
#         g.api.image.download_path(image_id, cache_path)
#
#     #if is_test is False:
#     image = cv2.imread(cache_path)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     image = Image.fromarray(image)
#     image.save(cache_path)
#
#     img_path = os.path.join(img_dir, f"{image_id}.png")
#     sly.fs.copy_file(cache_path, img_path)
#
#     ann_json = g.api.annotation.download(image_id).annotation
#     # ann_path = os.path.join(img_dir, f"{image_id}.json")
#     #sly.json.dump_json_file(ann_json, ann_path)
#
#     ann = sly.Annotation.from_json(ann_json, g.project_meta)
#     machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
#
#     for label in ann.labels:
#         if not label.obj_class.name.endswith("_prediction"):
#             #@TODO: skip prediction by object tag "prediction"
#             if is_test:
#                 if g.prediciton_tag in label.tags:
#                     ann = ann.delete_label(label)
#             label.geometry.draw(machine_mask, color=g.machine_map[label.obj_class.name])
#
#     if is_test is False:
#         sly.image.write(os.path.join(g.machine_masks_dir, f"{image_id}.png"), machine_mask[:, :, 0])
#
#     return ann, img_path


# @g.my_app.callback("add_to_train")
# @sly.timeit
# @g.my_app.ignore_errors_and_show_dialog_window()
# def add_to_train(api: sly.Api, task_id, context, state, app_logger):
#     image_id = context['imageId']
#     _, _ = download_data(image_id, is_test=False)
#
#     images = sly.fs.list_files(g.train_dir, sly.image.SUPPORTED_IMG_EXTS)
#     masks = []
#     for image_path in images:
#         mask_path = os.path.join(g.machine_masks_dir, sly.fs.get_file_name(image_path) + ".png")
#         if not sly.fs.file_exists(mask_path):
#             raise RuntimeError(f"Mask doesn't exist: {mask_path}")
#         masks.append(mask_path)
#
#     interpreter = "/ilastik-build/ilastik-1.4.0b14-Linux/bin/python"
#     ilp_path = os.path.join(g.my_app.data_dir, "project.ilp")
#
#     train_script_path = os.path.join(g.source_path, "train_headless.py")
#     train_cmd = f"{interpreter} " \
#                 f"{train_script_path} " \
#                 f"--project={ilp_path} "
#     for image_path, mask_path in zip(images, masks):
#         train_cmd += f"--images='{image_path}' "
#         train_cmd += f"--masks='{mask_path}' "
#
#     sly.logger.info("Training", extra={"command": train_cmd})
#     bash_out = subprocess.Popen([train_cmd], shell=True, executable="/bin/bash", stdout=subprocess.PIPE).communicate()
#     output_log = bash_out[0]
#     error_log = bash_out[1]
#     g.my_app.show_modal_window("PixelClassification has been successfully trained", level="info")
#     api.task.set_field(task_id, "state.loading", False)


@g.my_app.callback("classify_pixels")
@sly.timeit
#@g.my_app.ignore_errors_and_show_dialog_window()
def classify_pixels(api: sly.Api, task_id, context, state, app_logger):
    image_id = context['imageId']
    sly.fs.clean_dir(g.test_dir)
    sly.fs.clean_dir(g.predictions_dir)
    ann, img_path = download_data(image_id, is_test=True)
    ilp_path = os.path.join(g.my_app.data_dir, "project.ilp")

    test_cmd = f"/ilastik-build/ilastik-1.4.0b14-Linux/run_ilastik.sh " \
               f"--headless " \
               f"--project={ilp_path} " \
               f"--export_source='Simple Segmentation' " \
               f"--output_format='png' " \
               f"{img_path}"

    sly.logger.info("Testing", extra={"command": test_cmd})
    bash_out = subprocess.Popen([test_cmd], shell=True, executable="/bin/bash", stdout=subprocess.PIPE).communicate()
    output_log = bash_out[0]
    error_log = bash_out[1]

    import utils
    seg_path = img_path.replace(sly.fs.get_file_ext(img_path), "_Simple Segmentation.png")
    img = sly.image.read(seg_path)
    mask = img[:, :, 0]
    labels = []
    for class_name in g.label_names:
        color = g.machine_map[class_name][0]
        mask_bool = mask == color
        if not np.any(mask_bool):
            continue
        labels.append(sly.Label(sly.Bitmap(mask_bool), g.project_meta.get_obj_class(class_name), tags=sly.TagCollection([g.prediciton_tag])))

    ann = ann.add_labels(labels)
    api.annotation.upload_ann(image_id, ann)

    api.task.set_field(task_id, "state.loading", False)

    #utils.bw_to_color([seg_path], g.machine_colors, g.label_colors)


@g.my_app.callback("remove_predicted_labels")
@sly.timeit
def remove_predicted_labels(api: sly.Api, task_id, context, state, app_logger):
    image_id = context['imageId']
    ann_info = g.api.annotation.download(image_id).annotation
    ann = sly.Annotation.from_json(ann_info, g.project_meta)
    for label in ann.labels:
        if g.prediction_tag in label.tags:
            ann = ann.delete_label(label)
            g.api.annotation.upload_ann(image_id, ann)
    api.task.set_field(task_id, "state.loading", False)


#@TODO: remove utils.py
#@TODO: show modal window ValueError("Unknown level 'debug'. Supported levels: ['warning', 'info', 'error']")
#@TODO: remove auto objects before training
#@TODO: add prediction to bottom + add tag "auto" + add remove autolabels button
#@TODO: create all features
#@TODO: try catch errors
#@TODO: hotkeys
#@TODO: upload project to team files
#@TODO: buttons loading
#@TODO: add multiple images to train-headless
def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "team_id": g.team_id,
            "workspace_id": g.workspace_id,
            "task_id": g.task_id
        }
    )

    data = {}
    state = {}
    ui.init(data, state)


    g.my_app.compile_template(g.root_source_dir)

    #sly.fs.clean_dir(g.my_app.data_dir) #@TODO: for debug
    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
