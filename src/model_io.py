import supervisely_lib as sly
import globals as g
import target_classes


@g.my_app.callback("new")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def start_new_model(api: sly.Api, task_id, context, state, app_logger):
    g.init_directories()
    target_classes.refresh_classes()


@g.my_app.callback("load")
@sly.timeit
@g.my_app.ignore_errors_and_show_dialog_window()
def load_existing_model(api: sly.Api, task_id, context, state, app_logger):
    raise NotImplementedError()