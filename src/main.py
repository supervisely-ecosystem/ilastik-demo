import os
import numpy as np
import subprocess
import supervisely_lib as sly
import globals as g


def download_data(image_id, is_test=False):
    if is_test is True:
        img_dir = g.test_dir
    else:
        img_dir = g.train_dir

    info = g.api.image.get_info_by_id(image_id)

    cache_path = os.path.join(g.cache_dir, f"{image_id}{sly.fs.get_file_ext(info.name)}")
    if not sly.fs.file_exists(cache_path):
        g.api.image.download_path(image_id, cache_path)
    img_path = os.path.join(img_dir, f"{image_id}{sly.fs.get_file_ext(info.name)}")
    sly.fs.copy_file(cache_path, img_path)

    ann_json = g.api.annotation.download(image_id).annotation
    # ann_path = os.path.join(img_dir, f"{image_id}.json")
    #sly.json.dump_json_file(ann_json, ann_path)

    ann = sly.Annotation.from_json(ann_json, g.project_meta)
    machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
    for label in ann.labels:
        if not label.obj_class.name.endswith("_prediction"):
            #@TODO: skip prediction by object tag "prediction"
            label.geometry.draw(machine_mask, color=g.machine_map[label.obj_class.name])

    sly.image.write(os.path.join(g.machine_masks_dir, f"{image_id}.png"), machine_mask[:, :, 0])
    return ann, img_path


@g.my_app.callback("add_to_train")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def add_to_train(api: sly.Api, task_id, context, state, app_logger):
    image_id = context['imageId']
    _, _ = download_data(image_id, is_test=False)

    interpreter = "/ilastik-build/ilastik-1.4.0b14-Linux/bin/python"
    #interpreter = "/ilastik-build/ilastik-1.3.3post3-Linux/bin/python"
    ilp_path = os.path.join(g.my_app.data_dir, "project.ilp")

    #train_script_path = os.path.join(g.source_path, "generate_trained_project.py")
    # train_cmd = f"{interpreter} " \
    #             f"{train_script_path} " \
    #             f"--save_ilp_to=\"{ilp_path}\" " \
    #             f"--train_images_dir=\"{g.train_dir}\" " \
    #             f"--machine_masks_dir=\"{g.machine_masks_dir}\" " \
    #             f"--label_names=\"{g.label_names}\" " \
    #             f"--label_colors=\"{g.label_colors}\""

    train_script_path = os.path.join(g.source_path, "train_headless.py")
    train_cmd = f"{interpreter} " \
                f"{train_script_path} " \
                f"{ilp_path} " \
                f"{os.path.join(g.train_dir, '899992.png')} " \
                f"{os.path.join(g.machine_masks_dir, '899992.png')} " \

    sly.logger.info("Training", extra={"command": train_cmd})

    bash_out = subprocess.Popen([train_cmd], shell=True, executable="/bin/bash", stdout=subprocess.PIPE).communicate()
    output_log = bash_out[0]
    error_log = bash_out[1]


@g.my_app.callback("classify_pixels")
@sly.timeit
#@g.my_app.ignore_errors_and_show_dialog_window()
def classify_pixels(api: sly.Api, task_id, context, state, app_logger):
    image_id = context['imageId']
    sly.fs.clean_dir(g.test_dir)
    sly.fs.clean_dir(g.predictions_dir)
    ann, img_path = download_data(image_id, is_test=True)
    ilp_path = os.path.join(g.my_app.data_dir, "project.ilp")

    # interpreter = "/ilastik-build/ilastik-1.4.0b14-Linux/bin/python"
    # test_script_path = os.path.join(g.source_path, "apply_model.py")
    #
    # test_cmd =  f"{interpreter} " \
    #             f"{test_script_path} " \
    #             f"--classifier_path=\"{ilp_path}\" " \
    #             f"--test_images_dir=\"{g.test_dir}\" " \
    #             f"--save_predictions_to=\"{g.predictions_dir}\" "

    test_cmd = f"/ilastik-build/ilastik-1.4.0b14-Linux/run_ilastik.sh " \
               f"--headless " \
               f"--project={ilp_path} " \
               f"{img_path}"
    sly.logger.info("Testing", extra={"command": test_cmd})

    bash_out = subprocess.Popen([test_cmd], shell=True, executable="/bin/bash", stdout=subprocess.PIPE).communicate()
    output_log = bash_out[0]
    error_log = bash_out[1]


#@TODO: try catch errors
#@TODO: hotkeys
#@TODO: upload project to team files
#@TODO: buttons loading
def main():
    sly.logger.info(
        "Script arguments",
        extra={
            "team_id": g.team_id,
            "workspace_id": g.workspace_id,
            "task_id": g.task_id
        }
    )
    data = {
        "ownerId": g.owner_id
    }
    state = {}

    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
