import os
import numpy as np
import subprocess
import supervisely_lib as sly
import globals as g


def download_data(image_id, is_test=False):
    test_ann = None
    if is_test is True:
        img_dir = g.test_dir
    else:
        img_dir = g.train_dir

    info = g.api.image.get_info_by_id(image_id)
    img_path = os.path.join(img_dir, f"{image_id}{sly.fs.get_file_ext(info.name)}")
    if not sly.fs.file_exists(img_path):
        g.api.image.download_path(image_id, img_path)

    ann_path = os.path.join(img_dir, f"{image_id}.json")
    ann_json = g.api.annotation.download(image_id).annotation
    sly.json.dump_json_file(ann_json, ann_path)

    ann = sly.Annotation.from_json(ann_json, g.project_meta)
    machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
    for label in ann.labels:
        if not label.obj_class.name.endswith("_prediction"):
            #@TODO: skip prediction by object tag "prediction"
            label.geometry.draw(machine_mask, color=g.machine_map[label.obj_class.name])

    sly.image.write(os.path.join(g.machine_masks_dir, f"{image_id}.png"), machine_mask)
    return ann

    # if is_test:
    #     img_dir = g.test_img_dir
    #     test_ann_json = g.api.annotation.download(image.id).annotation
    #     test_ann = sly.Annotation.from_json(test_ann_json, g.project_meta)
    #     # test_anns.append(test_ann)
    # else:
    #     img_dir = g.train_dir
    #     ann_json = g.api.annotation.download(image.id).annotation
    #     ann = sly.Annotation.from_json(ann_json, g.project_meta)
    #     machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
    #     for label in ann.labels:
    #         if not label.obj_class.name.endswith("_prediction"):
    #             label.geometry.draw(machine_mask, color=g.machine_map[label.obj_class.name])
    #     sly.image.write(os.path.join(g.machine_masks_dir, os.path.splitext(image.name)[0] + '.png'), machine_mask)
    # g.api.image.download_path(image.id, os.path.join(img_dir, image.name))
    # return test_ann


@g.my_app.callback("add_to_train")
@sly.timeit
def add_to_train(api: sly.Api, task_id, context, state, app_logger):
    image_id = context['imageId']
    _ = download_data(image_id, is_test=False)


    # generate_trained_project.py
    train_cmd = "/ilastik-build/ilastik-1.4.0b14-Linux/bin/python "
    docker_inspect_out = subprocess.Popen([docker_inspect_cmd],
                                          shell=True, executable="/bin/bash",
                                          stdout=subprocess.PIPE).communicate()[0]

    # ./ilastik-1.1.7-Linux/bin/python train_headless.py MyNewProject.ilp /tmp/cell-slide.png

    # for each image retrain model
    # generate_trained_project_file(g.path_to_trained_project,
    #                               g.train_img_dir,
    #                               g.machine_masks_dir,
    #                               g.label_names,
    #                               g.label_colors,
    #                               100)


@g.my_app.callback("apply_to_current_image")
@sly.timeit
def apply_to_current_image(api: sly.Api, task_id, context, state, app_logger):
    print('context = ', context)
    print('state = ', state)
    # infer model

    # APPLY MODEL
    image_id = context['imageId']
    test_ann = download_data(image_id, is_test=True)
    # predicted_images_bw = predict_image(g.path_to_trained_project, g.test_img_dir, g.predictions_dir)
    # predicted_images_col = utils.bw_to_color(predicted_images_bw, g.machine_colors, g.pred_label_colors)
    # utils.draw_predicitons(api, [image_id], g.project.id, g.project_meta, [test_ann],
    #                        g.predictions_dir, g.pred_label_names, g.pred_label_colors)


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
