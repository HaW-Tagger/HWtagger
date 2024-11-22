import os, json, csv, datetime
import concurrent.futures
import shutil
import hashlib
import re

import imagehash
import numpy as np
from PIL import Image
from pathlib import Path
import pandas as pd

from tools import misc_func

import resources.parameters
from resources import parameters
from huggingface_hub import hf_hub_download, snapshot_download

def load_database(folder):
    if "TEMP_DISCARDED" in os.listdir(folder):
        export_images(get_all_images_in_folder(os.path.join(folder, "TEMP_DISCARDED")), folder)
    with open(os.path.join(folder, parameters.DATABASE_FILE_NAME), 'r') as f:
        db = json.load(f)
    return db

def save_database(database: dict, folder):
    add_history(folder)
    backup_database_file(folder)
    with open(os.path.join(folder, parameters.DATABASE_FILE_NAME), 'w') as f:
        json.dump(database, f)

def check_database_exist(folder):
    # return bool, if database.json exists
    return os.path.exists(os.path.join(folder, parameters.DATABASE_FILE_NAME))

def create_database_file(folder):
    with open(os.path.join(folder, parameters.DATABASE_FILE_NAME), 'w') as f:
        json.dump({}, f)
    parameters.log.info("Created database file")

def backup_database_file(folder):
    files = os.listdir(folder)
    backups = []
    for file in files:
        if parameters.DATABASE_FILE_NAME+".bak" in file:
            backups.append(file)
    backups.sort(key=lambda x: int(x[x.index(".bak")+4:]))
    while len(backups)>0:
        if len(backups) >= parameters.PARAMETERS['max_databases_view_backup']:
            os.remove(os.path.join(folder, backups[-1]))
        else:
            dst_path = os.path.join(folder,backups[-1][:backups[-1].index(".bak")+4] + str(int(backups[-1][backups[-1].index(".bak")+4:])+1).zfill(3))
            os.rename(os.path.join(folder, backups[-1]), dst_path)
        backups.pop()
    os.rename(os.path.join(folder, parameters.DATABASE_FILE_NAME), os.path.join(folder, parameters.DATABASE_FILE_NAME+".bak"+'001'))

def get_all_images_in_folder(folder, image_ext=resources.parameters.IMAGES_EXT, rejected_folders=resources.parameters.PARAMETERS["discard_folder_name_from_search"]):
    """
    return all images paths from a certain folder, recursively
    Args:
        rejected_folders: list of rejected names that could be inside folders
        folder:
        image_ext:

    Returns: list[str]
    """
    S = []
    for f in os.listdir(folder):
        if not any([x in f for x in rejected_folders]):
            if f.endswith(image_ext):
                S.append(os.path.join(folder, f))
            elif os.path.isdir(os.path.join(folder, f)):
                S.extend(get_all_images_in_folder(os.path.join(folder, f), image_ext, rejected_folders))
    return S

def get_all_databases_folder(folder, rejected_folders=resources.parameters.PARAMETERS["discard_folder_name_from_search"]):
    """
    return all folders belonging to a folder that contains a database.json file
    Args:
        rejected_folders:
        folder:

    Returns:
    """
    S = []
    for f in os.listdir(folder):
        if not any([x in f for x in rejected_folders]):
            if f == parameters.DATABASE_FILE_NAME:
                S.append(folder)
            elif os.path.isdir(os.path.join(folder, f)):
                S.extend(get_all_databases_folder(os.path.join(folder, f), rejected_folders))
    return S

def read_history():
    try:
        with open("history.json", 'r') as f:
            history = json.load(f)
    except FileNotFoundError:
        create_history()
        history = {}
    return history

def create_history():
    with open("history.json", 'w') as f:
        json.dump({}, f)

def add_history(database_path):
    history = read_history()
    if database_path not in history.keys():
        ct = datetime.datetime.now()
        history[database_path] = {}
        history[database_path] = {'date': [ct.year, ct.month, ct.day, ct.hour]}
        with open("history.json", 'w') as f:
            json.dump(history, f)


def subfolders_load(folder):
    """
    return a list of tuples, image location and tags
    :param folder:
    :return:
    """
    S = []
    for f in os.listdir(folder):
        if os.path.isdir(os.path.join(folder,f)):
            S.extend(subfolders_load(os.path.join(folder, f)))
        elif f.endswith(resources.parameters.IMAGES_EXT):
            s = (os.path.join(folder, f), [])
            for t in os.listdir(folder):
                if t == f.rsplit('.')[0]+".txt" or t == f+".txt":
                    with open(os.path.join(folder, t), 'r') as txt:
                        tags = txt.readline().split(',')
                        striped_tags = [x.strip() for x in tags]
                    s[1].extend(striped_tags)
            S.append(s)
    return S


def recursive_dict_values(tags):
    all_values = []
    if type(tags) is dict:
        all_values.extend(recursive_dict_values(list(tags.values())))
    if type(tags) is list:
        for tag in tags:
            if type(tag) is list:
                all_values.extend(recursive_dict_values(tag))
            else:
                all_values.append(tag)
    return all_values


def save_image(old_img_path, new_image_path, tags: list):
    """
    :param old_img_path: path of the image to be copied
    :param new_image_path: path to the image output
    :param tags: all tags in order in a list
    :return: nothing
    """
    if Path(old_img_path) != Path(new_image_path):
        try:
            shutil.copy(old_img_path, new_image_path)
        except:
            os.makedirs(os.path.dirname(new_image_path))
            shutil.copy(old_img_path, new_image_path)
    with open(new_image_path.rsplit('.')[0]+".txt", 'w') as f:
        tags_line = ",".join(tags)
        f.write(tags_line)


def to_png(path, pool: concurrent.futures.ThreadPoolExecutor):
    """
    convert all .jpg files to PNG files in a single folder ( subfolders included )
    :param pool: the concurrent.futures subprocess
    :param path:
    :return:
    """
    files = os.listdir(path)
    for i in files:
        if os.path.isdir(os.path.join(path, i)):
            to_png(os.path.join(path, i), pool)
        elif os.path.join(path, i).endswith('jpg'):
            src_path=os.path.join(path, i)
            dst_path=os.path.join(path, i)[:-4]+".png"
            pool.submit(convert_image_to_png, src_path, dst_path)
        elif os.path.join(path, i).endswith('jpeg'):
            src_path = os.path.join(path, i)
            dst_path = os.path.join(path, i)[:-5] + ".png"
            pool.submit(convert_image_to_png, src_path, dst_path)
def to_png_from_images_paths(images_paths, pool: concurrent.futures.ThreadPoolExecutor):
    """
    convert all .jpg files to PNG files in a single folder ( subfolders included )
    :param pool: the concurrent.futures subprocess
    :param images_paths:
    :return:
    """
    for i in images_paths:
        if i.endswith('jpg'):
            src_path=i
            dst_path=i[:-4]+".png"
            pool.submit(convert_image_to_png, src_path, dst_path)
        elif i.endswith('jpeg'):
            src_path = i
            dst_path = i[:-5] + ".png"
            pool.submit(convert_image_to_png, src_path, dst_path)

def convert_image_to_png(src_path, dst_path):
    if os.path.exists(dst_path):
        parameters.log.info(f"dst_path: {dst_path} exists, can't convert src_path: {src_path} to png.")
        return False
    with Image.open(src_path, mode='r') as img:
        img.save(dst_path, format="png")
    os.remove(src_path)
    return True

def to_md5(path):
    """
    convert all files to md5 files in a single folder ( subfolders included )
    :param path:
    :return:
    """
    files = os.listdir(path)

    for i in files:
        if os.path.isdir(os.path.join(path, i)):
            to_md5(os.path.join(path, i))
        elif os.path.join(path, i).endswith(resources.parameters.IMAGES_EXT):
            image_md5 = get_md5(os.path.join(path, i))
            new_path = os.path.join(path, image_md5 + os.path.splitext(i)[1])
            if not os.path.exists(new_path):
                shutil.copy2(os.path.join(path, i), new_path)
                os.remove(os.path.join(path, i))
def to_md5_from_images_paths(images_paths):
    """
    convert all files to md5 files from paths
    :param images_paths:
    :return:
    """

    for i in images_paths:
        if i.endswith(resources.parameters.IMAGES_EXT):
            image_md5 = get_md5(i)
            new_path = os.path.join(os.path.dirname(i), image_md5 + os.path.splitext(i)[1])
            if not os.path.exists(new_path):
                shutil.copy2(i, new_path)
                os.remove(i)


def get_md5(file_path):
    """
    return the md5 for an image (or any other file type)
    :param file_path:
    :return:
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_multiple_md5(files_paths) -> list[tuple[str, str]]:
    """
    concurrent md5 calculation (supposedly faster than direct ones)
    Args:
        files_paths:

    Returns:
        result: list[tuple(md5, file_path)]
    """
    result = []
    def get_md5_and_path(file_path):
        """
        return the md5 for an image (or any other file type)
        :param file_path:
        :return:
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        result.append((hash_md5.hexdigest(), file_path))

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
    for path in files_paths:
        pool.submit(get_md5_and_path, path)
    pool.shutdown(wait=True)
    return result

def create_txt(images_dict: dict):
    """
    create txt files when given a database
    :param images_dict: image_path: [tags]
    :return:
    """
    for image in images_dict.keys():
        tags = images_dict[image]
        with open(os.path.splitext(image)[0]+".txt", 'w') as f:
            f.write(', '.join(tags)+"\n")
    parameters.log.info("Successfully created the .txt containing tags")

def get_favourites():
    result=[]
    try:
        with open(os.path.join(resources.parameters.MAIN_FOLDER, 'resources/favourites.txt'), 'r') as f:
            favourites = f.readline().split(',')
            result = [tag.strip() for tag in favourites if tag != ""]
            return result
    except FileNotFoundError:
        return result

def save_favourites(tags_list):
    with open(os.path.join(resources.parameters.MAIN_FOLDER, 'resources/favourites.txt'), 'w') as f:
        f.write(', '.join(tags_list))
    parameters.log.info("Saved favourite tags to {'resources/favourites.txt'}")

def get_duplicate_string(string_list):
    seen_tags = set()
    unique_tags, dupes = [], []
    for str_tag in string_list:
        if str_tag not in seen_tags:
            unique_tags.append(str_tag)
            seen_tags.add(str_tag)
        else:
            dupes.append(str_tag)
    return dupes

def loose_tags_check(search_tags, full_tags):
    """return a bool if all search tag is included in the full tags (fuzzy search), search tags: ([tag], positive, exact)"""
    for search_tag in search_tags:
        print(search_tag, full_tags)
        # with asterisks
        if len(search_tag[0]) > 1:
            if search_tag[1]:  # positive
                one_positive = False
                for tag in full_tags:
                    if all([search_tag[0][i] in tag for i in range(len(search_tag[0]))]):
                        # find if in right order
                        if re.fullmatch(r'.*'.join(search_tag[0]), tag):
                            one_positive = True
                            break
                if not one_positive:
                    return False
            else:  # negative
                one_negative = False
                for tag in full_tags:
                    if all([search_tag[0][i] in tag for i in range(len(search_tag[0]))]):
                        # find if in right order
                        if re.fullmatch(r'.*'.join(search_tag[0]), tag):
                            one_negative = True
                            break
                if one_negative:
                    return False

        elif search_tag[0][0] == "2persons":
            # todo: 1other
            two_persons = False
            if "2girls" in full_tags and not any([x in full_tags for x in ["multiple boys", "1boy", "2boys"]]):
                two_persons=True
            if "2boys" in full_tags and not any([x in full_tags for x in ["multiple girls", "1girl", "2girls"]]):
                two_persons=True
            if "1boy" in full_tags and "1girl" in full_tags and not any([x in full_tags for x in ["multiple girls", "multiple boys", "2girls", "2boys"]]):
                two_persons=True

            if search_tag[1] and not two_persons:  # positive
                return False
            elif not search_tag[1] and two_persons: #negative
                return False

        elif search_tag[2]: #exact
            if search_tag[1]: #positive
                if search_tag[0][0] not in full_tags:
                    return False
            else: # negative
                if search_tag[0][0] in full_tags:
                    return False
        else: #inexact
            if search_tag[1]: #positive
                if not any([search_tag[0][0] in str(ft) for ft in full_tags]):
                    return False
            else: # negative
                if any([search_tag[0][0] in str(ft) for ft in full_tags]):
                    return False
    return True
    # return all(any([t[0] in ft for ft in full_tags]) for t in search_tags if t[1]==True) and all(all([t[0] not in ft for ft in full_tags]) for t in search_tags if t[1]==False)

def loose_tags_search_settings_from_tags_list(search_tags) -> list[tuple[str, bool, bool]]:
    temp_search_tags = []
    for tag in search_tags:
        if tag.strip():
            to_add = ([tag.strip()], True, False) #[tag],positive,exact
            if to_add[0][0][0] == "-":  # positive
                to_add = ([to_add[0][0][1:]], False, to_add[2])
            if to_add[0][0][0] == '"' and to_add[0][0][-1] == '"':  # exact
                to_add = ([to_add[0][0][1:-1]], to_add[1], True)
            if to_add[0][0][0] == "-":  # positive
                to_add = ([to_add[0][0][1:]], False, to_add[2])
            if '*' in to_add[0][0]:
                to_add = (to_add[0][0].split('*'), to_add[1], to_add[2])
            temp_search_tags.append(to_add)

    return temp_search_tags

def export_images(img_paths, base_dir, new_folder="DISCARDED"):
    if len(img_paths):
        # adds new folder to root/base_dir and exports the imgs there. will keep directory structure found
        if new_folder == 'DISCARDED':
            reason = "Moving files not fit for training (truncated images, corrupted imgs, etc)"
        elif new_folder == 'dupe':
            reason = "Moving duplicate files"
        else:
            reason = "No specific reason provided for moving files"
        new_base_dir = os.path.join(base_dir, new_folder)
        
        # make/use directory
        if not os.path.isdir(new_base_dir):
                os.makedirs(new_base_dir)
                parameters.log.info(f"New folder for exporting {new_folder} imgs (folder structure is intact)")
        else:
            parameters.log.info(f"Found {new_folder}, using this directory for exporting {new_folder} imgs")
        main_base_path = os.path.normpath(base_dir).split(os.sep)
        main_path_len = len(main_base_path)
        moved = 0
        for img in img_paths:
            old_path = os.path.normpath(img).split(os.sep)
            new_path = old_path[main_path_len:]
            
            new_path = os.path.join(*new_path) # unpack the list of directory components
            new_path = os.path.join(new_base_dir, new_path)
            new_dir = os.path.split(new_path)[0]
            if not os.path.isdir(new_dir):
                parameters.log.info(f"Making new directory for exporting files: {new_dir}")
                os.makedirs(new_dir)
            try:
            
                if new_folder not in old_path and os.path.exists(img): # check if it's in a moved folder
                    shutil.move(img, new_path)
                    moved +=1
            except Exception as e:
                parameters.log.exception(img, exc_info=e)
        parameters.log.info(f"Finished moving {moved} images to the {new_folder} folder")

def move_similar_images_back(base_dir):
    parameters.log.info("Moving back files")
    moved_count = 0
    for path in os.listdir(base_dir):
        if re.match(r'similar_\d+', path):
            past_images = get_all_images_in_folder(os.path.join(base_dir, path))
            new_images = [os.path.join(base_dir, os.path.relpath(image_path, start=os.path.join(base_dir, path))) for image_path in past_images]
            for p, n in zip(past_images, new_images):
                try:
                    shutil.move(p, n)
                    moved_count+=1
                except Exception as e:
                    parameters.log.exception(exc_info=e)
                    
                    
            if not os.listdir(os.path.join(base_dir, path)):
                os.rmdir(os.path.join(base_dir, path))
                
    if moved_count:
        parameters.log.info(f"Moved back {moved_count} files")
    else:
        parameters.log.error("No files were moved")

def find_near_duplicates(images_paths: list[str],*, threshold: float=0.9, hash_size: int=32, bands: int=32) -> list[tuple[str, str, float]]:
    """
    Find near-duplicate images

    Args:
        images_paths: List of images paths
        threshold: Images with a similarity ratio >= threshold will be considered near-duplicates
        hash_size: Hash size to use, signatures will be of length hash_size^2
        bands: The number of bands to use in the locality sensitive hashing process

    Returns:
        A list of near-duplicates found. Near duplicates are encoded as a triple: (filename_A, filename_B, similarity)
    """

    def calculate_signature(image_file: str, hash_size: int):
        """
        Calculate the dhash signature of a given file

        Args:
            image_file: the image (path as string) to calculate the signature for
            hash_size: hash size to use, signatures will be of length hash_size^2

        Returns:
            Image signature as Numpy n-dimensional array or None if the file is not a PIL recognized image
        """
        try:
            pil_image = Image.open(image_file).convert("L").resize(
                (hash_size + 1, hash_size),
                Image.LANCZOS)
            dhash = imagehash.dhash(pil_image, hash_size)
            signature = dhash.hash.flatten()
            adding_signature(signature, image_file)
            pil_image.close()
        except IOError as e:
            parameters.log.exception(f"Loading {image_file} failed.", exc_info=e)
            return

    def adding_signature(signature, image_path):
        # Keep track of each image's signature
        signatures[image_path] = np.packbits(signature)

        # Locality Sensitive Hashing
        for i in range(bands):
            signature_band = signature[i * rows:(i + 1) * rows]
            signature_band_bytes = signature_band.tobytes()
            if signature_band_bytes not in hash_buckets_list[i]:
                hash_buckets_list[i][signature_band_bytes] = list()
            hash_buckets_list[i][signature_band_bytes].append(image_path)

    rows: int = int(hash_size ** 2 / bands)
    signatures = dict()
    hash_buckets_list: list[dict[str, list[str]]] = [dict() for _ in range(bands)]

    # Iterate through all files in input directory
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
    # pool.submit(img.load_image_object, (max_image_size, max_image_size))
    for _ in misc_func.tqdm_parallel_map(pool, lambda fh: calculate_signature(fh, hash_size), images_paths):
        pass
    pool.shutdown(wait=True)

    # Build candidate pairs based on bucket membership
    candidate_pairs = set()
    for hash_buckets in hash_buckets_list:
        for hash_bucket in hash_buckets.values():
            if len(hash_bucket) > 1:
                hash_bucket = sorted(hash_bucket)
                for i in range(len(hash_bucket)):
                    for j in range(i + 1, len(hash_bucket)):
                        candidate_pairs.add(
                            tuple([hash_bucket[i], hash_bucket[j]])
                        )

    # Check candidate pairs for similarity
    near_duplicates = list()
    for cpa, cpb in candidate_pairs:
        hd = sum(np.bitwise_xor(
            np.unpackbits(signatures[cpa]),
            np.unpackbits(signatures[cpb])
        ))
        similarity = (hash_size ** 2 - hd) / hash_size ** 2
        if similarity > threshold:
            near_duplicates.append((cpa, cpb, similarity))

    # Sort near-duplicates by descending similarity and return
    near_duplicates.sort(key=lambda x: x[2], reverse=True)
    return near_duplicates

def get_dict_caformer_tag_frequency():
    # get caformer (rule34) from json
    ca_model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["caformer_folder"])
    if not os.path.exists(ca_model_folder):
        # checl the backup location
        ca_model_folder = os.path.join(os.path.join(parameters.MAIN_FOLDER, "HWtagger"), parameters.PARAMETERS["caformer_folder"])
    
    
    ca_file = "class.json"
    with open(os.path.join(ca_model_folder, ca_file), 'r') as f:
            ca_dict = json.load(f)
    return ca_dict

def get_pd_swinbooru_tag_frequency():
    # get the tags booru tags used in the swin model
    swin_model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["swinv2v3_folder"])
    swin_file = "selected_tags.csv"
    tags_df = pd.read_csv(os.path.join(swin_model_folder, swin_file))
    return tags_df

def get_pd_eva02_large_tag_frequency():
    # get the tags booru tags used in the swin model
    swin_model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS["eva02_large_v3_folder"])
    swin_file = "wd-eva02-large-tagger-v3.csv"
    tags_df = pd.read_csv(os.path.join(swin_model_folder, swin_file))
    return tags_df

def download_model(name: str):
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    # use snapshot_download if we want to download an entire repo
    match name:
        case "Swinv2v2":
            rel_path = "models/SwinV2/"
            for filename in ["keras_metadata.pb", "saved_model.pb", "selected_tags.csv", "tmpugou97nr", "variables/variables.data-00000-of-00001", "variables/variables.index"]:
                rel_file_path = rel_path + filename
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=rel_file_path, local_dir=parameters.MAIN_FOLDER)
            hf_hub_download(repo_id="PhoenixAscencio/HWtagger", filename="models/SwinV2", local_dir=parameters.MAIN_FOLDER)
        case "Swinv2v3":
            rel_path = "models/SwinV2v3/"
            for filename in ["config.json", "model.onnx", "selected_tags.csv", "sw_jax_cv_config.json"]:
                rel_file_path = rel_path + filename
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=rel_file_path, local_dir=parameters.MAIN_FOLDER)
        case "Caformer":
            for filename in ["models/ML-danbooru-caformer/class.json", "models/ML-danbooru-caformer/model.ckpt"]:
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=filename, local_dir=parameters.MAIN_FOLDER)
        case "anime_aesthetic":
            rel_path = "models/anime_aesthetic/"
            for filename in ["swinv2pv3_v0_448_ls0.2_x_meta.json", "model.onnx", "swinv2pv3_v0_448_ls0.2_x_metrics.json"]:
                rel_file_path = rel_path + filename
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=rel_file_path, local_dir=parameters.MAIN_FOLDER)
        case "anime_classifier":
            rel_path = "models/anime_classifier/"
            for filename in ["mobilenetv3_v1.3_dist_meta.json", "model.onnx", "mobilenetv3_v1.3_dist_metrics.json"]:
                rel_file_path = rel_path + filename
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=rel_file_path, local_dir=parameters.MAIN_FOLDER)
        case "detect_people":
            for filename in ["models/person_detect/person_detect_plus_v1.1_best_m.onnx"]:
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=filename, local_dir=parameters.MAIN_FOLDER)
        case "detect_head":
            for filename in ["models/head_detect/head_detect_best_s.onnx"]:
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=filename, local_dir=parameters.MAIN_FOLDER)
        case "detect_hand":
            rel_path = "models/hand_detect/"
            for filename in ["model.onnx", "model_artifacts.json"]:
                rel_file_path = rel_path + filename
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=rel_file_path, local_dir=parameters.MAIN_FOLDER)
        case "anime_completeness":
            rel_path = "models/anime_completeness/"
            for filename in ["model.onnx", "meta.json", "metrics.json"]:
                rel_file_path = rel_path + filename
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=rel_file_path, local_dir=parameters.MAIN_FOLDER)
        case "Eva02_largev3":
            rel_path = "models/wd-eva02-large-tagger-v3/"
            for filename in ["wd-eva02-large-tagger-v3.csv", "wd-eva02-large-tagger-v3.onnx"]:
                rel_file_path = rel_path + filename
                pool.submit(hf_hub_download, repo_id="PhoenixAscencio/HWtagger", filename=rel_file_path,
                            local_dir=parameters.MAIN_FOLDER)
        case _:
            parameters.log.error(f"Unknown case when downloading model, check for typo for model")
    pool.shutdown(wait=True)