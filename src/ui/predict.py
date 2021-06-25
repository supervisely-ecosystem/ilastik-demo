import globals as g
import supervisely_lib as sly


@g.my_app.callback("remove_predicted_labels")
@sly.timeit
# @g.my_app.ignore_errors_and_show_dialog_window()
def remove_predicted_labels(api: sly.Api, task_id, context, state, app_logger):
    image_id = context['imageId']
    ann_info = g.api.annotation.download(image_id).annotation
    ann = sly.Annotation.from_json(ann_info, g.project_meta)
    for label in ann.labels:
        if g.prediction_tag in label.tags:
            ann = ann.delete_label(label)
            g.api.annotation.upload_ann(image_id, ann)
    api.task.set_field(task_id, "state.loading", False)
