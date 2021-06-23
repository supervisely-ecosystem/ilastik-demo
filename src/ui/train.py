import supervisely_lib as sly
import globals as g


def init(data, state):
    data["trainset"] = None


@g.my_app.callback("add_to_train")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def add_to_train(api: sly.Api, task_id, context, state, app_logger):
    pass
