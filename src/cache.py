import os
import cv2
import json
import numpy as np
import globals as g
import supervisely_lib as sly


def remove_train_image_from_set(image_name):
    train_img_path = os.path.join(g.train_dir, image_name)
    train_ann_path = os.path.join(g.train_ann_dir, image_name)
    mask_img_path = os.path.join(g.machine_masks_dir, image_name)

    sly.fs.silent_remove(train_img_path)
    sly.fs.silent_remove(train_ann_path)
    sly.fs.silent_remove(mask_img_path)


def download_train(image_id, project_id):
    selected_classes = g.selected_classes
    ann_json = g.api.annotation.download(image_id).annotation
    ann = sly.Annotation.from_json(ann_json, project_meta=g.project_meta)

    machine_mask = np.zeros(shape=ann.img_size + (3,), dtype=np.uint8)
    mask_img_path = os.path.join(g.machine_masks_dir, f"{image_id}.png")

    ann_classes = [label.obj_class.name for label in ann.labels]
    cnt = 0
    is_in = False
    for sel_class in selected_classes:
        for ann_class in ann_classes:
            if sel_class == ann_class:
                cnt += 1
                if cnt == 2:
                    is_in = True
                    break

    if is_in is False:
        g.my_app.show_modal_window(f"There are no selected classes on current image. Please draw labels and try again")
    else:
        for label in ann.labels:
            if g.prediction_tag in label.tags:
                ann = ann.delete_label(label)
            if label.obj_class.name in selected_classes:
                label.geometry.draw(machine_mask, color=g.machine_map[label.obj_class.name])
            else:
                ann = ann.delete_label(label)

        modified_ann_json = ann.to_json()
        train_ann_path = os.path.join(g.train_ann_dir, f"{image_id}.json")
        sly.json.dump_json_file(modified_ann_json, train_ann_path)
        sly.image.write(os.path.join(mask_img_path), machine_mask[:, :, 0])

        train_img_path = os.path.join(g.train_dir, f"{image_id}.png")
        if not sly.fs.file_exists(train_img_path):
            img = g.api.image.download_np(image_id)
            gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            cv2.imwrite(train_img_path, gray_img)


def download_test(image_id):
    test_img_path = os.path.join(g.test_dir, f"{image_id}.png")

    tag_meta = g.project_meta.get_tag_meta(g.prediction_tag.name)
    if tag_meta is None:
        project_meta = g.project_meta.add_tag_meta(g.prediction_tag_meta)
        g.api.project.update_meta(g.project.id, project_meta.to_json())

    if not sly.fs.file_exists(test_img_path):
        img = g.api.image.download_np(image_id)
        gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        cv2.imwrite(test_img_path, gray_img)

    ann_json = g.api.annotation.download(image_id).annotation
    ann = sly.Annotation.from_json(ann_json, g.project_meta)

    for label in ann.labels:
        if g.prediction_tag in label.tags:
            ann = ann.delete_label(label)
    return ann, test_img_path
