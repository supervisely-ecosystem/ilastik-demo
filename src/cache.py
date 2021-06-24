import os
import cv2
import supervisely_lib as sly
import globals as g

project_meta = {}


def get_project_meta(project_id):
    project_meta = g.api.project.get_meta(project_id)
    project_meta = sly.ProjectMeta.from_json(project_meta)
    return project_meta

def update_project_meta(project_id):
    pass


# def download(image_id, dir):
#     info = g.api.image.get_info_by_id(image_id)
#
#
#     cached_image_path = os.path.join(g.cache_dir, f"{image_id}.png")
#
#
#     if not sly.fs.file_exists(cached_image_path):
#         img = g.api.image.download_np(image_id)
#         gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
#         cv2.imwrite(cached_image_path, gray_img)
#
#     ann_json = g.api.annotation.download(image_id).annotation
#     ann_path = os.path.join(img_dir, f"{image_id}.json")
#     sly.json.dump_json_file(ann_json, ann_path)
#
#     return cached_image_path,






# def download_image(image_id, is_test=False):
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