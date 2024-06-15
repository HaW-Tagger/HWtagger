import csv
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from tools.images import timing
from resources import parameters
from resources.tag_categories import KAOMOJI
# from wd14 tagger
IMAGE_SIZE = 448
FILES = ["keras_metadata.pb", "saved_model.pb", "selected_tags.csv"]
SUB_DIR_FILES = ["variables.data-00000-of-00001", "variables.index"]
CSV_FILE = FILES[-1]

CHARACTERS = False


# ********************* DISCLAIMER *****************************
# this code is not used anymore, check the onnx version!
# **************************************************************


# Untouched
def preprocess_image(image):
    image = np.array(image)
    image = image[:, :, ::-1]  # RGB->BGR

    # pad to square
    size = max(image.shape[0:2])
    pad_x = size - image.shape[1]
    pad_y = size - image.shape[0]
    pad_l = pad_x // 2
    pad_t = pad_y // 2
    image = np.pad(image, ((pad_t, pad_y - pad_t), (pad_l, pad_x - pad_l), (0, 0)), mode="constant", constant_values=255)

    interp = cv2.INTER_AREA if size > IMAGE_SIZE else cv2.INTER_LANCZOS4
    image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE), interpolation=interp)

    image = image.astype(np.float32)
    return image

# Removed a lot of useless things
def main(train_data, model_dir, batch_size, remove_underscore, threshold, character_threshold):
    parameters.log.info("Loading SwinV2")

    # removed onnx
    from tensorflow.keras.models import load_model

    model = load_model(f"{model_dir}")

    # Link Tags with Model
    with open(os.path.join(model_dir, CSV_FILE), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        header = l[0]  # tag_id,name,category,count
        rows = l[1:]
    assert header[0] == "tag_id" and header[1] == "name" and header[2] == "category", f"unexpected csv format: {header}"

    general_tags = [row[1] for row in rows[1:] if row[2] == "0"]
    character_tags = [row[1] for row in rows[1:] if row[2] == "4"]
    # Finished Link Tags

    # CHANGES for data images
    image_paths = []
    for k in train_data.keys():
        image_paths.append(k)
    parameters.log.info(f"Found {len(image_paths)} images.")

    #undesired_tags = set(args.undesired_tags.split(stripped_caption_separator))

    def run_batch(path_imgs):
        imgs = np.array([im for _, im in path_imgs])

        # Removed onnx
        probs = model(imgs, training=False)
        probs = probs.numpy()

        for (image_path, _), prob in zip(path_imgs, probs):
            # 最初の4つはratingなので無視する
            # # First 4 labels are actually ratings: pick one with argmax
            # ratings_names = label_names[:4]
            # rating_index = ratings_names["probs"].argmax()
            # found_rating = ratings_names[rating_index: rating_index + 1][["name", "probs"]]

            # それ以降はタグなのでconfidenceがthresholdより高いものを追加する
            # Everything else is tags: pick any where prediction confidence > threshold
            combined_tags = []
            for i, p in enumerate(prob[4:]):
                if i < len(general_tags) and p >= threshold:
                    tag_name = general_tags[i]
                    if remove_underscore and len(tag_name) > 3 and tag_name not in KAOMOJI:  # ignore emoji tags like >_< and ^_^
                        tag_name = tag_name.replace("_", " ")

                    # if tag_name not in undesired_tags:
                    combined_tags.append([tag_name, round(float(p), 3)])

                elif i >= len(general_tags) and p >= character_threshold:  # character threshold to replace if needed
                    tag_name = character_tags[i - len(general_tags)]
                    if remove_underscore and len(tag_name) > 3 and tag_name not in KAOMOJI:
                        tag_name = tag_name.replace("_", " ")

                    # if tag_name not in undesired_tags:
                    combined_tags.append([tag_name, round(float(p), 3)])

            train_data[image_path] = combined_tags

    data = [(None, ip) for ip in image_paths]

    b_imgs = []
    for data_entry in data:
        if data_entry is None:
            continue
        image, image_path = data_entry
        if image is not None:
            image = image.detach().numpy()
        else:
            try:
                image = Image.open(Path(image_path))
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image = preprocess_image(image)
            except Exception as e:
                parameters.log.exception(f"Could not load image path / 画像を読み込めません: {image_path}", exc_info=e)
                continue
        b_imgs.append((image_path, image))

        if len(b_imgs) >= batch_size:
            run_batch(b_imgs)
            #progress_bar.setValue(progress_bar.value()+len(b_imgs))
            b_imgs.clear()

    if len(b_imgs) > 0:
        run_batch(b_imgs)
        #progress_bar.setValue(len(image_paths))

    return train_data


def main2(train_data, model_dir, batch_size, remove_underscore, threshold, character_threshold):
    parameters.log.info(f"Loading SwinV2, Batch:{batch_size}, importing tensorflow")
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    parameters.log.info("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    # added the compile tag cause we're only using it for inference and not training
    model = load_model(f"{model_dir}", compile=False)
    #tf.compat.v1.enable_eager_execution()
    # Link Tags with Model
    with open(os.path.join(model_dir, CSV_FILE), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        header = l[0]  # tag_id,name,category,count
        rows = l[1:]
    assert header[0] == "tag_id" and header[1] == "name" and header[2] == "category", f"unexpected csv format: {header}"

    #the csv has all character tags concentrated at the end of the table
    general_tags = [row[1] for row in rows[1:] if row[2] == "0"]
    character_tags = [row[1] for row in rows[1:] if row[2] == "4"]

    image_paths = [k for k in train_data.keys()]

    def rgb_to_bgr(input): # func copied from tensorflow io
        """
        Convert a RGB image to BGR.

        Args:
        input: A 3-D (`[H, W, 3]`) or 4-D (`[N, H, W, 3]`) Tensor.
        name: A name for the operation (optional).

        Returns:
        A 3-D (`[H, W, 3]`) or 4-D (`[N, H, W, 3]`) Tensor.
        """
        rgb = tf.unstack(input, axis=-1)
        r, g, b = rgb[0], rgb[1], rgb[2]
        return tf.stack([b, g, r], axis=-1)
    
    def preprocess_image3(image, IMAGE_SIZE):
        # we resize first to lighten the load of the pad
        size = tf.reduce_max(tf.shape(image)[:2])
        #interp = tf.cond(size > IMAGE_SIZE,
        #         lambda: tf.constant("area", dtype=tf.string),
        #         lambda: tf.constant("lanczos3", dtype=tf.string))
        #resized_image = tf.image.resize(image, (IMAGE_SIZE, IMAGE_SIZE), preserve_aspect_ratio=True, method=interp)
        resized_image = tf.cond(size > IMAGE_SIZE,
                        lambda: tf.image.resize(image, (IMAGE_SIZE, IMAGE_SIZE), preserve_aspect_ratio=True, method="area"),
                        lambda: tf.image.resize(image, (IMAGE_SIZE, IMAGE_SIZE), preserve_aspect_ratio=True, method="lanczos3"))
        resized_image = rgb_to_bgr(resized_image)
        size = tf.reduce_max(tf.shape(resized_image)[:2])
        pad_x = size - tf.shape(resized_image)[1]
        pad_y = size - tf.shape(resized_image)[0]
        pad_l = pad_x // 2
        pad_t = pad_y // 2
        resized_image = tf.pad(resized_image, [[pad_t, pad_y - pad_t], [pad_l, pad_x - pad_l], [0, 0]], mode="constant", constant_values=255)
        #resized_image = tf.image.resize(resized_image, (IMAGE_SIZE, IMAGE_SIZE), method=interp)
        parameters.log.debug(tf.shape(resized_image)[1:])
        return resized_image
    
    def load_ds(img_paths):
        # creates a dataset ds given a directory
        # keep shuffle False if you want same ordered samples
        list_ds = tf.data.Dataset.list_files(img_paths, shuffle=False)
        return list_ds 

    def path_to_img(file_path):
        # Load the raw data from the file as a string
        return tf.io.decode_image(tf.io.read_file(file_path), channels=3, expand_animations=False)
        
    def ds_performance(ds, BATCH_SIZE):
        """
        This is a code that uses the tensorflow dataset library and is used to load imgs in parallel
        as to speed up the lag between opening and processing multiple images
        Originally written for a basic denoising model, so the commended out code is the legacy code for that

        IMAGE_SIZE, image resolution we want to load the image in

        """
        ds = ds.map(lambda x: path_to_img(x), num_parallel_calls=tf.data.AUTOTUNE, deterministic=True)
        ds = ds.map(lambda x: preprocess_image3(x, IMAGE_SIZE), num_parallel_calls=tf.data.AUTOTUNE, deterministic=True)
        ds = ds.batch(BATCH_SIZE, drop_remainder=False)
        ds = ds.prefetch(buffer_size=tf.data.AUTOTUNE)
        
        return ds
    
    name_ds = load_ds(image_paths)
    data_ds = ds_performance(name_ds, batch_size)
    name_ds = name_ds.batch(batch_size, drop_remainder=False)


    parameters.log.info(f"Found {len(image_paths)} images. Starting tag inference with SwinV2")

    for path_batch, img_batch in zip(name_ds, data_ds):
        #img_batch = np.array(img_batch, dtype=np.float32)
        parameters.log.debug(tf.shape(img_batch))
        prob_batch = model(img_batch, training=False)
        prob_batch = prob_batch.numpy()

        gen_tag_len = len(general_tags)
        for f_path, prob_vec in zip(path_batch, prob_batch):
            prob_vec = prob_vec[4:]
            f_path = f_path.numpy().decode()
            pred = np.asarray(prob_vec>threshold).nonzero()[0]
            # here we clip pred by the general tag len, basically removing index associated with characters
            # if you want to add character support, add a separate pred variable 
            # with the char threshold and check the index > general_tags
            clipped_pred = pred[(gen_tag_len>pred)]
            parameters.log.debug(clipped_pred)
            # we subtract one cause of the index
            tag_prob = [(general_tags[i], prob_vec[i]) for i in clipped_pred]
            parameters.log.debug(tag_prob)
            tag_prob.sort(reverse=True, key=lambda x:x[1])
            train_data[f_path] = []
            for tag_name, prob in tag_prob:
                    if len(tag_name) > 3 and tag_name not in KAOMOJI:
                        train_data[f_path].append((tag_name.replace('_', ' '), round(float(prob), 3)))
                    else:
                        train_data[f_path].append((tag_name, round(float(prob), 3)))
            if CHARACTERS:
                pred = np.asarray(prob_vec>character_threshold).nonzero()[0]
                clipped_char_pred = pred[(gen_tag_len<=pred)]
                tag_prob = [(character_tags[i], prob_vec[i]) for i in clipped_char_pred]
                tag_prob.sort(reverse=True, key=lambda x:x[1])
                for tag_name, prob in tag_prob:
                    if len(tag_name) > 3:
                        train_data[f_path].append((tag_name.replace('_', ' '), round(float(prob), 3)))
                    else:
                        train_data[f_path].append((tag_name, round(float(prob), 3)))
    
    return train_data

@timing
def auto_tagger(train_images_paths: dict, threshold=parameters.PARAMETERS["swinv2_threshold"], 
                character_threshold=parameters.PARAMETERS["swinv2_character_threshold"],model_dir="models/SwinV2/", batch_size=4, remove_underscore=True):
    """
    train images
    :param threshold:
    :param train_images_paths:
    :param model_dir:
    :param batch_size:
    :param remove_underscore:
    :return:
    """
    train_data = train_images_paths
    model_dir = model_dir
    batch_size = batch_size
    remove_underscore = remove_underscore
    return main2(train_data, model_dir, batch_size, remove_underscore, threshold, character_threshold)
