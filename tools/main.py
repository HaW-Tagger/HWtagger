import concurrent.futures
import enum
import os, sys
import warnings

from tqdm import tqdm

from resources import parameters
from resources import tag_categories
from tools import files

COLOR_CATEGORIES = tag_categories.COLOR_CATEGORIES
TAG_CATEGORIES = tag_categories.TAG_CATEGORIES

# todo: autodownload the models using huggingface_hub

def swin_v2v2_auto_tag(images_paths: list[str]):
    """
    Tags detected using the Swinv2 tagger, you can put any WD1.4 model in the models folder though
    :param images_paths:
    :param tag_threshold:
    :param progress_bar:
    :return: dict with the images_paths as the key and the tags as values
    """
    temp_dict = {}
    from tools import swinv2_tagger
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'
    for img in images_paths:
        temp_dict[img] = []
    train_data = swinv2_tagger.auto_tagger(temp_dict)
    return train_data

def swin_v2v3_auto_tag(images_paths: list[str]):
    """
    Tags detected using the Swinv2 tagger, you can put any WD1.4 model in the models folder though
    :param images_paths:
    :param tag_threshold:
    :param progress_bar:
    :return: dict with the images_paths as the key and the tags as values
    """
    from tools import swinv2_tagger_onnx
    model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["swinv2v3_folder"])
    if not os.path.exists(model_folder):
        # check the backup location
        model_folder = os.path.join(os.path.join(parameters.MAIN_FOLDER, "HWtagger"), parameters.PARAMETERS["swinv2v3_folder"])
    temp_dict = swinv2_tagger_onnx.main(images_paths, model_folder)
    return temp_dict

def character_only_swin_v2v2_auto_tag(image_paths: list[str]):
    """
    Tags detected using the Swinv2 tagger, you can put any WD1.4 model in the models folder though
    :return: dict with the images_paths as the key and the tags as values
    """
    temp_dict = {}
    from tools import swinv2_tagger
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'
    for img in image_paths:
        temp_dict[img] = []
    train_data = swinv2_tagger.auto_tagger(temp_dict)
    return train_data

def character_only_swin_v2v3_auto_tag(image_paths: list[str]):
    """
    Tags detected using the Swinv2 tagger, you can put any WD1.4 model in the models folder though
    :return: dict with the images_paths as the key and the tags as values
    """
    from tools import swinv2_tagger_onnx
    model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["swinv2v3_folder"])
    
    if not os.path.exists(model_folder):
        # checl the backup location
        model_folder = os.path.join(os.path.join(parameters.MAIN_FOLDER, "HWtagger"), parameters.PARAMETERS["swinv2v3_folder"])
    
    temp_dict = swinv2_tagger_onnx.main(image_paths, model_folder, character_only=True)
    return temp_dict

def caformer_auto_tag(image_paths: list[str]):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from tools import caformer_tagger
        model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["caformer_folder"])
        if not os.path.exists(model_folder):
            # checl the backup location
            model_folder = os.path.join(os.path.join(parameters.MAIN_FOLDER, "HWtagger"), parameters.PARAMETERS["caformer_folder"])
        
        
        model_dir = os.path.join(model_folder, "model.ckpt")
        model_json_dir = os.path.join(model_folder, "class.json")
        bs = 1
        bs_max = parameters.PARAMETERS["max_batch_size"]
        if len(image_paths) > 100:
            bs=2
        if len(image_paths) > 1000:
            bs=4
        if bs_max > bs:
            bs = bs_max
        tags = caformer_tagger.main(image_paths,
                                    model_dir,
                                    model_json_dir,
                                    bs)

    return tags

def aesthetic_scorer(image_paths: list[str]):
    from tools import image_scoring
    model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["aesthetic_folder"])
    if not os.path.exists(model_folder):
        # checl the backup location
        model_folder = os.path.join(os.path.join(parameters.MAIN_FOLDER, "HWtagger"), parameters.PARAMETERS["aesthetic_folder"])
    
    temp_dict = image_scoring.main(image_paths, model_folder)
    return temp_dict

def classify_image_source(image_paths: list[str]):
    from tools import image_classification
    model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["classifier_folder"])
    if not os.path.exists(model_folder):
        # checl the backup location
        model_folder = os.path.join(os.path.join(parameters.MAIN_FOLDER, "HWtagger"), parameters.PARAMETERS["classifier_folder"])
    
    temp_dict = image_classification.main(image_paths, model_folder)
    return temp_dict

def create_variation_from_tag():
    only_color = ["red", "blue", "green", "black", "white", "grey", "gray", "beige", "brown", "pink", "orange", "gold",
                  "blonde", "yellow", "purple", "aqua"]
    tags = input("insert the tag you want to have the variations of:")
    result = []
    tags_used = []
    for tag in tags:
        if tag not in tags_used:
            result.append(",".join([x+" "+tag for x in only_color]))
            tags_used.append(tag)
    parameters.log.info(result)
    create_variation_from_tag()

def similarity_example(images_paths,*, threshold=0.9, hash_size=32, bands=32):
    near_duplicates = files.find_near_duplicates(images_paths, threshold=threshold, hash_size=hash_size, bands=bands)
    if near_duplicates:
        parameters.log.info(f"Found {len(near_duplicates)} near-duplicate images in images (threshold {threshold:.2%})")
        for a,b,s in near_duplicates:
            parameters.log.info(f"{s:.2%} similarity: file 1: {a} - file 2: {b}")
    else:
        parameters.log.info(f"No near-duplicates found in images (threshold {threshold:.2%})")

def tqdm_parallel_map(executor, fn, *iterables, **kwargs):
    """
    from: https://techoverflow.net/2017/05/18/how-to-use-concurrent-futures-map-with-a-tqdm-progress-bar/

    Equivalent to executor.map(fn, *iterables),
    but displays a tqdm-based progress bar.

    Does not support timeout or chunksize as executor.submit is used internally

    **kwargs is passed to tqdm.
    """
    futures_list = []
    for iterable in iterables:
        futures_list += [executor.submit(fn, i) for i in iterable]
    for f in tqdm(concurrent.futures.as_completed(futures_list), total=len(futures_list), **kwargs):
        yield f.result()

def tagger_caller(tagger = parameters.AvailableTaggers):
    match tagger:
        case parameters.AvailableTaggers.SWINV2V2:
            return swin_v2v2_auto_tag
        case parameters.AvailableTaggers.SWINV2V2_CHARACTERS:
            return character_only_swin_v2v2_auto_tag
        case parameters.AvailableTaggers.SWINV2V3:
            return swin_v2v3_auto_tag
        case parameters.AvailableTaggers.SWINV2V3_CHARACTERS:
            return character_only_swin_v2v3_auto_tag
        case parameters.AvailableTaggers.CAFORMER:
            return caformer_auto_tag