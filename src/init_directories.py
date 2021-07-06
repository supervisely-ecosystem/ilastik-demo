import os
import globals as g
import supervisely_lib as sly

proj_dir = os.path.join(g.my_app.data_dir, g.project.name)
train_dir = os.path.join(proj_dir, 'train')
train_ann_dir = os.path.join(proj_dir, 'train_ann')
test_dir = os.path.join(proj_dir, 'test')
machine_masks_dir = os.path.join(proj_dir, 'masks_machine')


def init_directories():
    sly.fs.mkdir(proj_dir)
    sly.fs.clean_dir(proj_dir)
    sly.fs.mkdir(train_dir)
    sly.fs.mkdir(train_ann_dir)
    sly.fs.mkdir(test_dir)
    sly.fs.mkdir(machine_masks_dir)
