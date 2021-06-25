#import globals as g
from src import globals as g
from src import cache
import supervisely_lib as sly


def init(data, state):
    data["trainSet"] = None


def update_images(img_list):
    pass

@g.my_app.callback("add_to_train")
@sly.timeit
# @g.my_app.ignore_errors_and_show_dialog_window()
def add_to_train(api: sly.Api, task_id, context, state, app_logger):
    image_id = context['imageId']
    train_path, ann_path, mask_path = cache.download_train(image_id)
    img_name = sly.fs.get_file_name_with_ext(train_path)

    fields = [
        {"field": "data.trainSet", "payload":  [img_name]},
    ]
    api.app.set_fields(g.task_id, fields)
