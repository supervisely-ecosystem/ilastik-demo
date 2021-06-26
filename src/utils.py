


# from __future__ import print_function
#
# import numpy
# import supervisely_lib as sly
# from PIL import Image
#
#
# def change_grayscale_colors(input_img_path, ann, new_gray_colors):
#     npImage = numpy.array(Image.open(input_img_path))
#
#     LUT = numpy.zeros(256, dtype=numpy.uint8)
#     for idx, label_col in range(ann.labels):
#         LUT[idx] = new_gray_colors[idx]
#
#     pixels = LUT[npImage]
#     result = Image.fromarray(pixels)
#     result.save(input_img_path)
#
#
# def bw_to_color(bw_img_paths, grayscale_colors, pred_label_colors):
#     for bw_img_path in bw_img_paths:
#         img = Image.open(bw_img_path)
#         img = img.convert('RGB')
#         pixels = img.load()
#         assert len(grayscale_colors) == len(pred_label_colors)
#         for grayscale, color in zip(grayscale_colors, pred_label_colors):
#             for w in range(img.size[0]):
#                 for h in range(img.size[1]):
#                     if pixels[w, h] == tuple(grayscale):
#                         pixels[w, h] = tuple(color)
#         img.save(bw_img_path)
#     return bw_img_paths
#
#
# def draw_predicitons(api, test_img_ids, project_id, project_meta, test_anns, prediction_img_paths, prediction_labels, prediction_colors):
#     predictions = []
#     for test_img, test_ann in zip(prediction_img_paths, test_anns):
#         if test_img.endswith(".png"):
#             segmentation_img = sly.image.read(test_img)
#             colored_img = segmentation_img.astype(numpy.uint8)
#             for class_name, class_color in zip(prediction_labels, prediction_colors):
#                 mask = numpy.all(colored_img == class_color, axis=2)  # exact match (3-channel img & rgb color)
#                 bitmap = sly.Bitmap(data=mask)
#                 obj_class = sly.ObjClass(name=class_name, geometry_type=sly.Bitmap, color=class_color)
#                 test_ann = test_ann.add_label(sly.Label(bitmap, obj_class))
#                 if obj_class not in project_meta.obj_classes:
#                     project_meta = project_meta.add_obj_class(obj_class)
#                     api.project.update_meta(project_id, project_meta.to_json())
#
#                 colored_img[mask] = (0, 0, 0)
#             if numpy.sum(colored_img) > 0:
#                 sly.logger.warn('Not all objects or classes are captured from source segmentation.')
#             predictions.append(test_ann)
#
#     api.annotation.upload_anns(test_img_ids, predictions)
