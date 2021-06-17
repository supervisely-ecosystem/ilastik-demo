import supervisely_lib as sly
import globals as g
import os
import numpy as np
import utils

# context = {
#     'datasetId': 6876,
#     'teamId': 7,
#     'workspaceId': 299,
#     'projectId': 4895,
#     'imageId': 899951,
#     'figureId': None,
#     'figureClassId': None,
#     'figureClassTitle': None,
#     'toolClassId': 41103,
#     'sessionId': 'f0f454a1-07ae-47fa-98ac-58af346624b8',
#     'viewport': {
#         'offsetX': 98.99103124999999,
#         'offsetY': 17.975000000000023,
#         'zoom': 0.8538125
#     },
#     'tool': 'bitmap',
#     'userId': 276,
#     'jobId': None,
#     'request_id': '7754f23a-41a7-494e-a797-f29dc0cbe9cc'
# }


def download_data(image_id, is_test=False):
    test_ann = None
    image = g.api.image.get_info_by_id(image_id)
    if is_test:
        img_dir = g.test_img_dir
        test_ann_json = g.api.annotation.download(image.id).annotation
        test_ann = sly.Annotation.from_json(test_ann_json, g.project_meta)
        # test_anns.append(test_ann)
    else:
        img_dir = g.train_img_dir
        ann_json = g.api.annotation.download(image.id).annotation
        ann = sly.Annotation.from_json(ann_json, g.project_meta)
        machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
        for label in ann.labels:
            if not label.obj_class.name.endswith("_prediction"):
                label.geometry.draw(machine_mask, color=g.machine_map[label.obj_class.name])
        sly.image.write(os.path.join(g.machine_masks_dir, os.path.splitext(image.name)[0] + '.png'), machine_mask)
    g.api.image.download_path(image.id, os.path.join(img_dir, image.name))
    return test_ann


@g.my_app.callback("add_to_train_set")
@sly.timeit
def add_to_train_set(api: sly.Api, task_id, context, state, app_logger):
    print('context = ', context)
    print('state = ', state)
    image_id = context['imageId']
    _ = download_data(image_id, is_test=False)
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
            "TEAM_ID": g.TEAM_ID,
            "WORKSPACE_ID": g.WORKSPACE_ID,
            "TASK_ID": g.TASK_ID
        }
    )
    data = {}
    state = {}

    g.my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)
