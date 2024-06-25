import concurrent.futures
import html
import json
import os
import shutil
from collections import Counter
import copy

import cloudscraper
import tqdm

from classes.class_image import ImageDatabase
from tools import files, main
from resources import parameters, tag_categories
from clip import tokenize
import numpy as np

class VirtualDatabase:
    def __init__(self):
        self.images: list[ImageDatabase] = []
        self.duplicate_paths = []
        self.similar_images: list[set[int]] = []
        self.trigger_tags = {
            'main_tags': [],
            'secondary_tags': []
        }
        self.groups: dict[str: dict] = {}

    def append_images_dict(self, image_dict) -> bool:
        is_dupe = image_dict["md5"] in self.get_all_md5()
        if not is_dupe:
            is_dupe = image_dict["path"] in self.get_all_paths()
            if not is_dupe:
                self.images.append(ImageDatabase(image_dict))
        return is_dupe

    def index_of_image_by_md5(self, image_md5) -> int:
        # todo: return -1 in case of failure
        return self.get_all_md5().index(image_md5)

    def index_of_images_by_md5(self, images_md5: list[str]) -> list[int]:
        # todo: return -1 in case of failure
        md5_images_list = self.get_all_md5()
        to_return = []
        for md5 in images_md5:
            to_return.append(md5_images_list.index(md5))
        return to_return

    def index_of_image_by_image_path(self, image_path) -> int:
        """takes the absolute path of the image"""
        # todo: return -1 in case of failure
        return self.get_all_paths().index(image_path)

    def tag_images(self, image_paths: list[str]):
        path_set = set(image_paths)
        if len(path_set) < 1:
            parameters.log.error("No images are going to get tagged")
            return False
        untagged_images_paths = {}
        for tagger in parameters.PARAMETERS["automatic_tagger"]:
            tags = main.tagger_caller(tagger)(list(path_set))
            tagged_images_paths = set(tags.keys())
            for image_path in tagged_images_paths:
                image_index = self.index_of_image_by_image_path(image_path)
                self.images[image_index].init_image_dict(
                    {"auto_tags": {tagger.value[0]: tags[image_path]}})
                self.images[image_index].update_simple_auto_tags()
            not_used_paths = path_set - tagged_images_paths
            if not_used_paths:
                untagged_images_paths[tagger.value[0]] = not_used_paths

        if untagged_images_paths:
            parameters.log.error(f"These files were not added to the database {untagged_images_paths}")

    def character_only_tag_images(self, image_paths: list[str],*, character_tagger=parameters.AvailableTaggers.SWINV2V3_CHARACTERS):
        path_set = set(image_paths)
        if len(path_set) < 1:
            parameters.log.error("No images are going to get tagged")
            return False
        untagged_images_paths = {}
        tags = main.tagger_caller(character_tagger)(list(path_set))
        tagged_images_paths = set(tags.keys())
        for image_path in tagged_images_paths:
            image_index = self.index_of_image_by_image_path(image_path)
            # if there are values for the taggers for characters they are merged, if not they are made
            if character_tagger.value[0] in self.images[image_index].auto_tags.keys():
                result = {"auto_tags": {character_tagger.value[0]: self.images[image_index].auto_tags[character_tagger.value[0]]+[tag for tag in tags[image_path] if tag not in self.images[image_index].auto_tags[character_tagger.value[0]]]}}
            else:
                result = {"auto_tags": {character_tagger.value[0]: tags[image_path]}}
            self.images[image_index].init_image_dict(result)
            self.images[image_index].update_simple_auto_tags()
        not_used_paths = path_set - tagged_images_paths
        if not_used_paths:
            untagged_images_paths[character_tagger.value[0]] = not_used_paths

        if untagged_images_paths:
            parameters.log.error(f"These files were not added to the database {untagged_images_paths}")

    def score_images(self, image_paths: list[str]):
        path_set = set(image_paths)
        if len(path_set) < 1:
            parameters.log.error("No images are going to get tagged")
            return False
        scores = main.aesthetic_scorer(list(path_set))
        used_path_keys = path_set.intersection(scores)
        for image_path in used_path_keys:
            image_index = self.index_of_image_by_image_path(image_path)
            self.images[image_index].init_image_dict({"score_label": scores[image_path][0], "score_value": scores[image_path][1]})

    def classify_images(self, image_paths: list[str]):
        path_set = set(image_paths)
        if len(path_set) < 1:
            parameters.log.error("No images are going to get tagged")
            return False
        # dict (img_path) --> (class_name, prob)
        classifications = main.classify_image_source(image_paths)
        used_path_keys = path_set.intersection(classifications)
        for image_path in used_path_keys:
            image_index = self.index_of_image_by_image_path(image_path)
            self.images[image_index].init_image_dict({
                "classify_label": str(classifications[image_path][0]),
                "classify_value": float(classifications[image_path][1])
            })

    def retag_images(self, images_index: list[int]=None):
        """
        automatically retag and rewrite autotags for images, if only one tagger is selected then it removes the other tags
        """
        if not images_index:
            image_paths: list[str] = self.get_all_paths()
        else:
            image_paths: list[str] = [self.images[x].path for x in images_index]
        parameters.log.info(f"{len(image_paths)} images are going to be retagged.")
        self.tag_images(image_paths)

    def rescore_images(self, images_index: list[int]=None):
        """
        automatically rescore and rewrite scores for images
        """
        if not images_index:
            image_paths: list[str] = self.get_all_paths()
        else:
            image_paths: list[str] = [self.images[x].path for x in images_index]
        parameters.log.info(f"{len(image_paths)} images are going to be rescored.")
        self.score_images(image_paths)

    def reclassify_images(self, images_index: list[int]=None):
        """
        automatically rescore and rewrite scores for images
        """
        if not images_index:
            image_paths: list[str] = self.get_all_paths()
        else:
            image_paths: list[str] = [self.images[x].path for x in images_index]
        parameters.log.info(f"{len(image_paths)} images are going to be reclassified.")
        self.classify_images(image_paths)

    def filter_all(self):
        if len(self.images) < 100:
            for image in self.images:
                image.filter()
        else:
            pool = concurrent.futures.ThreadPoolExecutor()

            if len(self.images) < 1000:
                for image in self.images:
                    pool.submit(lambda i: i.filter(), image)
            else:
                for _ in main.tqdm_parallel_map(pool, lambda i: i.filter(), self.images):
                    pass
            pool.shutdown(wait=True)
        parameters.log.info("Filter applied to all images")

    def filter_sentence_all(self):
        if len(self.images) < 100:
            for image in self.images:
                image.filter_sentence()
        else:
            pool = concurrent.futures.ThreadPoolExecutor()

            if len(self.images) < 1000:
                for image in self.images:
                    pool.submit(lambda i: i.filter(), image)
            else:
                for _ in main.tqdm_parallel_map(pool, lambda i: i.filter_sentence(), self.images):
                    pass
            pool.shutdown(wait=True)
        parameters.log.info("Filter sentence applied to all images")

    def update_all_full_tags(self):
        for image in self.images:
            image.update_full_tags()

    def reset_all_scores(self):
        """
        automatically reset scores for all images
        """
        for image in self.images:
            image.reset_score()

    def create_txt_files(self, add_backslash_before_parenthesis=False, token_separator=True, keep_tokens_separator="|||", use_trigger_tags=True, use_aesthetic_score=False, use_sentence=False, sentence_in_trigger=False, remove_tags_in_sentence=True, score_trigger=True):
        token_keeper = keep_tokens_separator
        if not token_separator:
            token_keeper = ""
        main_tags = self.trigger_tags["main_tags"]
        secondary_tags = self.trigger_tags["secondary_tags"]
        if not use_trigger_tags:
            main_tags = []
            secondary_tags = []
        for image in self.images:

            to_write = image.create_txt_file(add_backslash_before_parenthesis=add_backslash_before_parenthesis,
                                             keep_tokens_separator=token_keeper,
                                             main_tags=main_tags,
                                             secondary_tags=secondary_tags,
                                             use_aesthetic_score=use_aesthetic_score,
                                             use_sentence=use_sentence,
                                             sentence_in_trigger=sentence_in_trigger,
                                             remove_tags_in_sentence=remove_tags_in_sentence,
                                             score_trigger=score_trigger
                                             )
            with open(os.path.join(os.path.splitext(image.path)[0] + ".txt"), 'w') as f:
                f.write(to_write + "\n")
        parameters.log.info("Successfully created the .txt files containing full tags")

    def get_all_paths(self):
        return [img.path for img in self.images]

    def get_all_md5(self):
        return [img.md5 for img in self.images]

    def add_image_to_group(self, group_name, image_index):
        """
        create the group if necessary
        Args:
            group_name:
            image_index:

        Returns: Nothing

        """
        # todo: change temporary group storage to index, so that the problem are way fewer in the future
        if group_name not in self.groups.keys():
            self.groups[group_name] = {"images": []}

        if self.images[image_index].md5 in self.groups[group_name]["images"]:
            return
        self.groups[group_name]["images"].append(self.images[image_index].md5)
        self.images[image_index].group_names.append(group_name)

    def add_images_to_group(self, group_name, images_index: list[int]):
        """
        create the group if necessary
        Args:
            group_name:
            images_index:

        Returns: Nothing

        """
        if group_name not in self.groups.keys():
            self.groups[group_name] = {"images": []}

        all_images_in_group = set(self.groups[group_name]["images"])
        for image_index in images_index:
            if not self.images[image_index].md5 in all_images_in_group:
                self.groups[group_name]["images"].append(self.images[image_index].md5)
                self.images[image_index].group_names.append(group_name)
                all_images_in_group.add(self.images[image_index].md5)

    def remove_image_from_group(self, group_name, image_index):
        """
        remove the image from the group
        Args:
            group_name:
            image_index:

        Returns: Nothing

        """
        if group_name not in self.groups.keys():
            return
        if self.images[image_index].md5 not in self.groups[group_name]["images"]:
            return
        self.groups[group_name]["images"].remove(self.images[image_index].md5)
        self.images[image_index].group_names.remove(group_name)

    def remove_empty_groups(self):
        to_remove = []
        for group in self.groups.keys():
            if not self.groups[group]["images"]:
                to_remove.append(group)
        for x in to_remove:
            del self.groups[x]

    def create_images_objects(self, max_image_size):
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
        for _ in main.tqdm_parallel_map(pool, lambda image: image.load_image_object((max_image_size, max_image_size)), self.images):
            pass
        pool.shutdown(wait=True)

    def tokenize_all_images(self):
        all_full_tags = [", ".join(x.get_full_tags()) for x in self.images]
        all_tokens = tokenize(all_full_tags, context_length=500, truncate=True).count_nonzero(dim=1)
        all_sentences = [x.sentence_description for x in self.images]
        all_sentence_tokens = tokenize(all_sentences, context_length=500, truncate=True).count_nonzero(dim=1)
        for k in range(len(self.images)):
            self.images[k].full_tags_token_length = all_tokens[k] - 2
            self.images[k].sentence_token_length = all_sentence_tokens[k] - 2

    def remove_images_by_path(self, path_list):
        db_path = self.get_all_paths()
        path_indexes = [db_path.index(p) for p in path_list if p in db_path]
        self.remove_images_by_index(path_indexes)

    def remove_images_by_md5(self, md5_list):
        db_md5 = self.get_all_md5()
        path_indexes = [db_md5.index(md5) for md5 in md5_list if md5 in db_md5]
        self.remove_images_by_index(path_indexes)

    def remove_images_by_index(self, index_list):
        index_list.sort(reverse=True)
        for idx in index_list:
            del self.images[idx]

    def get_ungrouped_images(self) -> list[int]:
        if not self.groups:
            return [x for x in range(len(self.images))]
        all_grouped_images = set()
        for group_name in self.groups.keys():
            if self.groups[group_name]["images"]:
                all_grouped_images.update([x for x in self.groups[group_name]["images"]])
        all_images_md5 = self.get_all_md5()
        return self.index_of_images_by_md5([x for x in all_images_md5 if x not in all_grouped_images])

    def find_similar_images(self):
        if self.similar_images:
            return False
        
        # a list of set with the index of the two images
        self.similar_images: list[set[int]] = []
        # a list of pairs, [[imgA_path, imgB_path, similarity_percentage]]
        similar_images: list[tuple[str, str, float]] = files.find_near_duplicates([image.path for image in self.images], threshold=parameters.PARAMETERS["similarity_threshold"])
        parameters.log.info(f"{len(similar_images)} pairs of similar images were found")
        for i in range(len(similar_images)):
            image_0: int = self.index_of_image_by_image_path(similar_images[i][0])
            image_1: int = self.index_of_image_by_image_path(similar_images[i][1])
            k = 0
            added = False
            while not added and k < len(self.similar_images):
                if image_0 in self.similar_images[k] and image_1 in self.similar_images[k]:
                    added = True
                elif image_0 not in self.similar_images[k] and image_1 not in self.similar_images[k]:
                    k+=1
                else:
                    self.similar_images[k].update({image_0, image_1})
                    added = True
            if not added:
                self.similar_images.append({image_0, image_1})
        # todo: make similarity have an average similarity for the group or for each image

        # remove groups that are other groups but smaller
        k = 0
        # k is the index of the currently evaluated img
        while k < len(self.similar_images):
            p = 0
            while p < len(self.similar_images):
                if p == k:
                    p += 1
                    continue
                if all([index in self.similar_images[p] for index in self.similar_images[k]]):
                    self.similar_images.pop(k)
                    break
                else:
                    p+=1
            if p >= len(self.similar_images):
                k+=1

        # sort by len of similarity group (bigger groups are first)
        self.similar_images.sort(key=lambda x: len(x))
        self.add_similarity_group_to_image()
        return True

    def add_similarity_group_to_image(self):
        if not self.similar_images:
            return False
        for image in self.images:
            image.similarity_group = 0
        for k in range(len(self.similar_images)):
            for i in self.similar_images[k]:
                self.images[i].similarity_group = k+1

    def remove_groups(self):
        """
        remove all occurrences of existing groups
        """
        self.groups = {}
        for image in self.images:
            image.group_names = []

    def remove_group(self, group_name):
        """
        remove all occurrences of existing group
        """
        del self.groups[group_name]
        for image in self.images:
            if group_name in image.group_names:
                image.group_names.remove(group_name)

    def change_md5_of_image(self, image_index, new_md5):
        """
        update all locations in where the md5 is used in the database and update the md5 of the image
        Args:
            image_index:
            new_md5:
        """
        for group in self.groups.keys():
            if self.images[image_index].md5 in self.groups[group]["images"]:
                self.groups[group]["images"][self.groups[group]["images"].index(self.images[image_index].md5)] = new_md5
        self.images[image_index].md5 = new_md5

    def purge_manual_tags(self, images_index: list[int]):
        """
        remove all manual tags and manual rejected tags, not entirely cleaned from human intervention though
        Args:
            images_index:
        """
        for index in images_index:
            self.images[index].rejected_manual_tags = []
            self.images[index].manual_tags = []
            self.images[index].get_rejected_tags()

    def purge_human_intervention(self, images_index: list[int]):
        """
        remove all human intervention, doesn't filter
        """
        for index in images_index:
            self.images[index].rejected_manual_tags = []
            self.images[index].manual_tags = []
            self.images[index].manually_reviewed = False
            self.images[index].resolved_conflicts = []
            if self.images[index].score_value:
                self.images[index].reset_score()
            self.images[index].get_rejected_tags()

    def auto_tag_all_images(self):
        self.tag_images(self.get_all_paths())
    def score_all_images(self):
        self.score_images(self.get_all_paths())
    def classify_all_images(self):
        self.classify_images(self.get_all_paths())

    def add_offline_tags_all_images(self,*, is_sentence: bool=False, do_search_complete_name: bool=False, extension_name: str='.txt', source_name: str):
        self.add_offline_tags(self.get_all_paths(), is_sentence=is_sentence, do_search_complete_name=do_search_complete_name, extension_name=extension_name, source_name=source_name)

    def add_offline_tags(self, image_paths,*, is_sentence: bool=False, do_search_complete_name: bool=False, extension_name: str='.txt', source_name: str="from_txt"):
        for image_path in image_paths:

            # for each img dir/.../img_file.png
            # check for dir/.../img_file.txt or dir/.../img_file.png.txt
            txt_name1 = os.path.splitext(image_path)[0] + extension_name
            txt_name2 = image_path + extension_name

            used_txt_name = txt_name1 if os.path.exists(txt_name1) else txt_name2 if do_search_complete_name and os.path.exists(txt_name2) else None

            if used_txt_name:
                with open(used_txt_name, 'r') as f:
                    if is_sentence:
                        tags = ''.join(f.readlines()).strip()
                    else:
                        tags = f.readline().split(',')
                        tags = [x.strip().replace('\\', '') for x in tags if parameters.PARAMETERS["keep_token_tags_separator"] != x.strip()]
                image_index = self.index_of_image_by_image_path(image_path)
                if is_sentence:
                    self.images[image_index].sentence_description = tags
                else:
                    self.images[image_index].init_image_dict({"external_tags": {source_name: tags}})

    def retrieve_danbooru_tags_all_images(self):
        self.retrieve_danbooru_tags([k for k in range(len(self.images))])

    def retrieve_danbooru_tags(self, images_index: list[int]):
        parameters.log.info("Scraping danbooru for tags")
        api_url = "https://danbooru.donmai.us/posts.json"
        USER_AGENT = "HaW Tagger"
        HTTP_HEADERS = {'User-Agent': USER_AGENT}
        scraper = cloudscraper.create_scraper()
        successful_retrievals = 0
        for index in tqdm.tqdm(images_index):
            image = self.images[index]
            url = f'{api_url}?md5={image.original_md5}'
            response = scraper.get(url=url, headers=HTTP_HEADERS)
            if response.status_code == 200:
                data = response.json()
                successful_retrievals += 1
                all_tags = data['tag_string_general'].split(" ") + data['tag_string_character'].split(" ")+ data['tag_string_meta'].split(" ")
                all_tags = [x.strip() for x in all_tags if x.strip()]
                all_tags = [x.replace('_', ' ') if len(x) > 3 or x not in tag_categories.KAOMOJI else x for x in all_tags]
                image.add_external_tags_key("danbooru", all_tags)
        parameters.log.info(f"Successfully retrieved danbooru tags for {successful_retrievals} images")

    def retrieve_gelbooru_tags_all_images(self, unsafe: bool=True):
        self.retrieve_gelbooru_tags([k for k in range(len(self.images))], unsafe)

    def retrieve_gelbooru_tags(self, images_index: list[int], unsafe: bool):
        parameters.log.info("Scraping gelbooru for tags")
        api_url = "https://gelbooru.com/"
        USER_AGENT = "HaW Tagger"
        HTTP_HEADERS = {'User-Agent': USER_AGENT}
        scraper = cloudscraper.create_scraper()
        successful_retrievals = 0
        all_accepted_tags = set(tag_categories.COLOR_DICT.keys())
        all_accepted_tags = all_accepted_tags.union(set(files.get_dict_caformer_tag_frequency().values()))
        all_accepted_tags = all_accepted_tags.union(set(files.get_pd_swinbooru_tag_frequency()["name"]))
        all_accepted_tags = all_accepted_tags.union(set(tag_categories.LOW2TAGS_KEYSET.union(tag_categories.TAG2HIGH_KEYSET)))
        all_accepted_tags = all_accepted_tags.union(set(tag_categories.DESCRIPTION_TAGS.keys()))

        for index in tqdm.tqdm(images_index):
            image = self.images[index]
            all_tags = []
            url = f'{api_url}?page=dapi&s=post&q=index&json=1&tags=md5:{image.original_md5}'
            response = scraper.get(url=url, headers=HTTP_HEADERS)
            if response.status_code == 200 and response.text:
                data = response.json()
                if "post" in data.keys():
                    successful_retrievals += 1
                    all_tags = html.unescape(data["post"][0]['tags']).split(" ")
                    all_tags = [x.strip() for x in all_tags if x.strip()]
                    all_tags = [x.replace('_', ' ') if len(x) > 3 or x not in tag_categories.KAOMOJI else x for x in all_tags]
            if all_tags:
                if not unsafe:
                    image.add_external_tags_key("gelbooru", all_tags)
                else:
                    accepted_gelbooru = []
                    for tag in all_tags:
                        if tag in all_accepted_tags:
                            accepted_gelbooru.append(tag)
                    image.add_external_tags_key("gelbooru", accepted_gelbooru)
                    image.add_external_tags_key("rejected_gelbooru", all_tags)
        parameters.log.info(f"Successfully retrieved gelbooru tags for {successful_retrievals} images")

    def retrieve_rule34_tags_all_images(self, unsafe: bool=True):
        self.retrieve_rule34_tags([k for k in range(len(self.images))], unsafe=unsafe)

    def retrieve_rule34_tags(self, images_index: list[int], unsafe: bool):
        parameters.log.info("Scraping rule34 for tags")
        api_url = "https://api.rule34.xxx/"
        USER_AGENT = "HaW Tagger"
        HTTP_HEADERS = {'User-Agent': USER_AGENT}
        scraper = cloudscraper.create_scraper()
        successful_retrievals = 0
        all_accepted_tags = set(tag_categories.COLOR_DICT.keys())
        all_accepted_tags = all_accepted_tags.union(set(files.get_dict_caformer_tag_frequency().values()))
        all_accepted_tags = all_accepted_tags.union(set(files.get_pd_swinbooru_tag_frequency()["name"]))
        all_accepted_tags = all_accepted_tags.union(set(tag_categories.LOW2TAGS_KEYSET.union(tag_categories.TAG2HIGH_KEYSET)))
        all_accepted_tags = all_accepted_tags.union(set(tag_categories.DESCRIPTION_TAGS.keys()))

        for index in tqdm.tqdm(images_index):
            image = self.images[index]
            all_tags = []
            url = f'{api_url}?page=dapi&s=post&q=index&json=1&tags=md5:{image.original_md5}'
            response = scraper.get(url=url, headers=HTTP_HEADERS)
            if response.status_code == 200 and response.text:
                data = response.json()
                successful_retrievals += 1
                all_tags = html.unescape(data[0]['tags']).split(" ")
                all_tags = [x.strip() for x in all_tags if x.strip()]
                all_tags = [x.replace('_', ' ') if len(x) > 3 or x not in tag_categories.KAOMOJI else x for x in all_tags]
            elif response.status_code == 200 and os.path.splitext(os.path.basename(image.path))[0] != image.original_md5:
                url = f'{api_url}?page=dapi&s=post&q=index&json=1&tags=md5:{os.path.splitext(os.path.basename(image.path))[0]}'
                response = scraper.get(url=url, headers=HTTP_HEADERS)
                if response.status_code == 200 and response.text:
                    data = response.json()
                    successful_retrievals += 1
                    all_tags = data[0]['tags'].split(" ")
                    all_tags = [x.strip() for x in all_tags if x.strip()]
                    all_tags = [x.replace('_', ' ') if len(x) > 3 or x not in tag_categories.KAOMOJI else x for x in
                                all_tags]
            if all_tags:
                if not unsafe:
                    image.add_external_tags_key("rule34", all_tags)
                else:
                    accepted_rule34 = []
                    for tag in all_tags:
                        if tag in all_accepted_tags:
                            accepted_rule34.append(tag)
                    image.add_external_tags_key("rule34", accepted_rule34)
                    image.add_external_tags_key("rejected_rule34", all_tags)
        parameters.log.info(f"Successfully retrieved rule34 tags for {successful_retrievals} images")

    def rename_all_images_to_png(self):
        self.rename_images_to_png([k for k in range(len(self.images))])

    def rename_images_to_png(self, images_index: list[int]):
        for index in images_index:
            image = self.images[index]
            if os.path.exists(image.path) and os.path.splitext(image.path)[1].lower() != ".png":
                dst_path = os.path.splitext(image.path)[0]+".png"
                if files.convert_image_to_png(image.path, dst_path):
                    image.path=dst_path
                    self.change_md5_of_image(index, files.get_md5(image.path))

    def rename_all_images_to_md5(self):
        self.rename_images_to_png([k for k in range(len(self.images))])

    def rename_images_to_md5(self, images_index: list[int]):
        for index in images_index:
            image = self.images[index]

            if os.path.exists(image.path):
                file_md5 = files.get_md5(image.path)
                if os.path.splitext(os.path.basename(image.path))[0] != file_md5:
                    dst_path = os.path.join(os.path.dirname(image.path), file_md5+os.path.splitext(image.path)[1])
                    if not os.path.exists(dst_path):
                        os.rename(image.path, dst_path)
                        image.path = dst_path
                        self.change_md5_of_image(index, file_md5)

    def get_frequency_of_all_tags(self):
        c = Counter()
        for image in self.images:
            c.update(image.get_full_tags())
        return c.most_common()

    def refresh_unsafe_tags(self, images_index: list[int]):
        all_accepted_tags = set(tag_categories.COLOR_DICT.keys())
        all_accepted_tags = all_accepted_tags.union(set(files.get_dict_caformer_tag_frequency().values()))
        all_accepted_tags = all_accepted_tags.union(set(files.get_pd_swinbooru_tag_frequency()["name"]))
        all_accepted_tags = all_accepted_tags.union(
            set(tag_categories.LOW2TAGS_KEYSET.union(tag_categories.TAG2HIGH_KEYSET)))
        all_accepted_tags = all_accepted_tags.union(set(tag_categories.DESCRIPTION_TAGS.keys()))
        for index in images_index:
            self.images[index].refresh_unsafe_tags(all_accepted_tags)



class Database(VirtualDatabase):
    def __init__(self, folder):
        super().__init__()
        self.folder = folder
        self.load_database()


    def load_database(self):
        if not os.path.exists(os.path.join(self.folder, parameters.DATABASE_FILE_NAME)):
            files.create_database_file(self.folder)
            parameters.log.info("Database path empty, created database.")
            return False

        db = files.load_database(self.folder)

        if "images" not in db.keys():
            parameters.log.info("Empty Database.")
            return False

        old_score_system = False # needs to be removed when time will come

        for image_dict in db["images"]:
            is_dupe = self.append_images_dict(db["images"][image_dict])
            if not old_score_system:
                try:
                    if db["images"][image_dict]["score_value"] > 1:
                        old_score_system = True
                except KeyError:
                    pass

        try:
            self.duplicate_paths = db["duplicate_paths"]
        except KeyError:
            parameters.log.error(f"Empty data for duplicate paths: {self.folder}")

        # trigger tags for the database
        try:
            self.trigger_tags = db["trigger_tags"]
        except KeyError:
            parameters.log.error(f"Empty data for secondary/main trigger tags: {self.folder}")

        # groups for the image
        try:
            self.groups = db["groups"]
            for group_name in self.groups.keys():
                try:
                    for image_md5 in self.groups[group_name]["images"]:
                        try:
                            self.images[self.index_of_image_by_md5(image_md5)].group_names.append(group_name)
                        except ValueError:
                            parameters.log.error(f"Error on md5 search for image: {image_md5}, image doesn't exists in the database")
                except KeyError:
                    pass
        except KeyError:
            parameters.log.error(f"Empty data for groups: {self.folder}")

        if old_score_system:
            parameters.log.warning("You should redo the score of the images in this dataset")

        parameters.log.info("Database loaded.")

    def save_database(self):
        result = {"images":{}}
        for image in self.images:
            result["images"][image.md5] = image.get_saving_dict()
        result["trigger_tags"] = self.trigger_tags
        result["groups"] = self.groups
        result["duplicate_paths"] = self.duplicate_paths
        files.save_database(result, self.folder)
        parameters.log.info("Saved Database")

    def check_existence_images(self):
        """
        delete all images that have non-existent images paths

        Returns:

        """
        self.update_images_paths()
        to_keep = []
        for image in self.images:
            if image.is_image_in_path():
                to_keep.append(image)
        if len(to_keep) == 0:
            parameters.log.warning("All images should be deleted, so none are")
        if len(to_keep) < len(self.images):
            parameters.log.info(f"Deleting due to not existing image path: {len(self.images) - len(to_keep)} images")
            self.images = to_keep
            # check for groups
            kept_md5s = set(self.get_all_md5())
            for group_name in self.groups.keys():
                new_group_images = []
                for group_md5 in self.groups[group_name]["images"]:
                    if group_md5 in kept_md5s:
                        new_group_images.append(group_md5)
                self.groups[group_name]["images"] = new_group_images

        elif len(to_keep) == len(self.images):
            parameters.log.info(f"All {len(self.images)} images exists")

    def add_images_to_db(self, image_paths: list[str], autotag=False, from_txt=False, grouping_from_path=False, score=False, classify=False, move_dupes=False):
        parameters.log.info(f"{len(image_paths)} images are going to be added to the database. (Before dupe check)")
        current_paths = set(self.get_all_paths())
        if len(image_paths) < 1:
            return False
        new_paths = []
        for image_path in image_paths:
            if image_path not in current_paths:
                image_md5 = files.get_md5(image_path)

                is_dupe = self.append_images_dict({"md5": image_md5, "original_md5": image_md5, "path": image_path})
                if not is_dupe:
                    new_paths.append(image_path)

        parameters.log.info(f"{len(new_paths)} images are going to be added to the database. (ignoring duplicate copies)")

        if autotag:
            self.tag_images(new_paths)
        if score:
            self.score_images(new_paths)
        if classify:
            self.classify_images(new_paths)

        if from_txt:
            for image_path in new_paths:

                # for each img dir/.../img_file.png
                # check for dir/.../img_file.txt or dir/.../img_file.png.txt
                txt_name1 = os.path.splitext(image_path)[0] + ".txt"
                txt_name2 = image_path + ".txt"

                used_txt_name = txt_name1 if os.path.exists(txt_name1) else txt_name2 if os.path.exists(txt_name2) else None

                if used_txt_name:
                    with open(used_txt_name, 'r') as f:
                        tags = f.readline().split(',')
                        striped_tags = [x.strip().replace('\\', '') for x in tags if parameters.PARAMETERS["keep_token_tags_separator"] not in x]
                    image_index = self.index_of_image_by_image_path(image_path)
                    self.images[image_index].init_image_dict({"external_tags": {"legacy_from_txt": striped_tags}})

        if grouping_from_path:
            self.add_image_to_groups_by_path(new_paths)

        if move_dupes:
            dupe_list = [image_path for image_path in image_paths if image_path not in self.get_all_paths()]
            if dupe_list:
                files.export_images(dupe_list, self.folder, "DUPLICATES")

        return new_paths

    def add_image_to_groups_by_path(self, image_paths):
        for image_path in image_paths:
            image_index = self.index_of_image_by_image_path(image_path)
            image_relative_path = os.path.relpath(self.images[image_index].path, self.folder)
            relative_dir, _ = os.path.split(image_relative_path)
            
            if relative_dir: # has a relative path
                    self.add_image_to_group(relative_dir, image_index)

    def create_json_file(self,add_backslash_before_parenthesis=False, token_separator=True, keep_tokens_separator=parameters.PARAMETERS["keep_token_tags_separator"], use_trigger_tags=True, use_aesthetic_score=True, use_sentence=False, sentence_in_trigger=False, remove_tags_in_sentence=True, score_trigger=True):
        image_dict = {}
        token_keeper = keep_tokens_separator
        if not token_separator:
            token_keeper = ""
        main_tags = self.trigger_tags["main_tags"]
        secondary_tags = self.trigger_tags["secondary_tags"]
        if not use_trigger_tags:
            main_tags = []
            secondary_tags = []
        for image in self.images:
            to_write = image.create_txt_file(add_backslash_before_parenthesis=add_backslash_before_parenthesis,
                                             keep_tokens_separator=token_keeper,
                                             main_tags=main_tags,
                                             secondary_tags=secondary_tags,
                                             use_aesthetic_score=use_aesthetic_score,
                                             score_trigger=score_trigger,
                                             use_sentence = use_sentence,
                                             sentence_in_trigger = sentence_in_trigger,
                                             remove_tags_in_sentence = remove_tags_in_sentence,
                                             )
            image_dict[image.path] = {}
            image_dict[image.path]["tags"] = to_write
        with open(os.path.join(self.folder, "meta_cap.json"), 'w') as f:
            json.dump(image_dict, f, indent=4)
        parameters.log.info("Created json for exporting data for checkpoint")

    def create_sample_toml(self, export_width=1024, export_height=1024, bucket_steps=64):
        # use tuple for or
        required_tags = [("1girl","1boy"), ("solo", "solo focus")] 
        # samples with these tags are removed
        blacklist_tags = ["loli", "shota", "monochrome","greyscale", "comic", "close up", "white border", "letterboxed", "2koma", "multiple views", "sepia"]
        # these tags are filtered out from the choosen samples
        post_filter_tags = ["heart", "heart-shaped pupils", "censored", "sketch", "signature", "spoken x", "though bubble", "speech bubble", 'empty speech bubble', "watermark"]


        main_tags = self.trigger_tags["main_tags"]
        secondary_tags = self.trigger_tags["secondary_tags"]

        desired_sample_count = parameters.PARAMETERS["toml_sample_max_count"]

        from sklearn.feature_extraction.text import TfidfVectorizer
        import seaborn as sns
        import matplotlib.pyplot as plt
        from resources.tag_categories import CATEGORY_TAG_DICT, COLOR_DICT_ORDER
        from random import shuffle

        # filter images based on filtering preferences
        idx_list = []
        for idx, image in enumerate(self.images):
            full_tags = image.full_tags
            if all(any(or_t in full_tags for or_t in t) if type(t) is tuple else t in full_tags for t in required_tags) and all(t not in full_tags for t in blacklist_tags):
                idx_list.append(idx)

        # if the number of total samples (in database) is greater than 1000, randomly sample 1000 to cut down computation
        max_corpus_count = 1000
        if len(idx_list) > max_corpus_count:
            shuffle(idx_list)
            parameters.log.info(f"We have {len(idx_list)} potential source images for samples, reduced to random {max_corpus_count} samples")
            idx_list = idx_list[:max_corpus_count]
        else:
            parameters.log.info(f"We have {len(idx_list)} potential source images for samples")
        
        if len(idx_list) < desired_sample_count:
            desired_sample_count = len(idx_list)
        min_df = 5
        if len(idx_list) < min_df:
            min_df = len(idx_list)
        

        corpus = [", ".join(self.images[i].full_tags) for i in idx_list]

        # reference/modification 
        # https://stackoverflow.com/questions/8897593/how-to-compute-the-similarity-between-two-text-documents
        # https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

        parameters.log.info("Generating TFIDF")
        vect = TfidfVectorizer(token_pattern=r'[^,]+', min_df=min_df)
        tfidf = vect.fit_transform(corpus)
        pairwise_similarity = tfidf * tfidf.T
        # convert to np
        pair_arr = pairwise_similarity.toarray()

        # look for very similar prompts/tags and penalize them so we have a lower probability of sampling them
        # fill diagonal with 0 in place (so that all self-pairs are out of the equation)
        np.fill_diagonal(pair_arr, 0)

        sq_dim_size = len(idx_list)

        difference_threshold = 0.7
        similar_coord = np.argwhere(pair_arr > difference_threshold)
        parameters.log.debug(similar_coord)
        parameters.log.debug(similar_coord[:, 0]) #x_coords
        parameters.log.debug(similar_coord[:, 1]) #y_coords
        common_coord_val = list(set(similar_coord[:, 0] +similar_coord[:, 1]))
        common_penatly = 30 # penalty for common tags

        if sq_dim_size - len(common_coord_val) < desired_sample_count: # get the unique samples and add random overlapping coords
            shuffle(common_coord_val)
            sample_indices = [i for i in idx_list if i not in common_coord_val] + common_coord_val
            sample_indices = sample_indices[:desired_sample_count]
        else: # we have ample data to choose samples from so we can be very random
            # sigmoid function to get sample probability p(x_i) = e^x_i / sum(e^x_i's)
            def get_prob_dist(token_len_list):
                img_reverse_token_len = np.array([255 - itl for itl in token_len_list])

                # shifting token distributions, x~[1, 225] is kinda big, idea:
                # 112 ~ 225/2
                # divide by 30 to make the max value ~3.7 which makes the sigmoid act simple
                img_reverse_token_len = (img_reverse_token_len-112)/30
                img_exp = np.exp(img_reverse_token_len)
                sample_prob = img_exp/np.sum(img_exp)
                return sample_prob

            img_no_penalty = np.array([min(255, self.images[i].get_token_length()) for i in idx_list])
            img_token_len = np.array([min(255, self.images[i].get_token_length() if i not in common_coord_val else self.images[i].get_token_length()+common_penatly)
                                      for i in idx_list])
            img_colors = np.array([0 if i not in common_coord_val else 1 for i in idx_list], dtype=int)

            # we make two graphs, one is without the penalties, and one with the penalty
            # the two graphs is nice for debugging the distributions
            no_penalty_prob = get_prob_dist(img_no_penalty)
            img_sample_prob = get_prob_dist(img_token_len)

            # matplotlib plot setup
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
            sample_indices = np.random.choice(idx_list, size=desired_sample_count, replace=False, p=img_sample_prob)
            parameters.log.info(([img_colors==0], img_no_penalty[img_colors==0], no_penalty_prob[img_colors==0]))
            ax1.scatter(img_no_penalty[img_colors==0], no_penalty_prob[img_colors==0], alpha=0.3, marker=".")
            ax1.scatter(img_no_penalty[img_colors==1], no_penalty_prob[img_colors==1], alpha=0.3, marker="x")

            ax2.scatter(img_token_len[img_colors==0], img_sample_prob[img_colors==0], alpha=0.3, marker=".")
            ax2.scatter(img_token_len[img_colors==1], img_sample_prob[img_colors==1], alpha=0.3, marker="x")

            np_tokens_len = np.array(img_token_len)
            sorted_index = np_tokens_len.argsort()
            sorted_y = np.cumsum(img_sample_prob[sorted_index])
            sorted_x = np_tokens_len[sorted_index]
            ax3.plot(sorted_x, sorted_y)
            plt.show()

        def convert_to_prompt(full_tag, model_prefix=[], keep_token_tags=[], post_filter=[], tags_under_conf=[]):
            # this reorders full tags, <model tags>, <special tokens>, <the other tags with descending importance>
            tag_list = model_prefix
            shuffle(keep_token_tags)
            for t in keep_token_tags:
                if t in full_tag:
                    tag_list.append(t)

            for category in COLOR_DICT_ORDER:
                tag_list.extend([t for t in CATEGORY_TAG_DICT[category] if t in full_tag and t not in tag_list and t not in tags_under_conf])
            tag_list.extend(t for t in full_tag if t not in tag_list)
            tag_list = [t for t in tag_list if t not in post_filter]
            return ", ".join(tag_list)
        
        # get the selected tags and convert them to a prompt.
        prompts = []
        bucket_sizes = []
        for i in sample_indices:
            parameters.log.info(f"Used sample: {self.images[i].path}")
            #full_tags = self.images[i].get_full_tags()
            full_tag_over_conf = self.images[i].get_full_tags_over_confidence(confidence=0.65)
            full_tags = self.images[i].get_full_tags()
            full_tags_under_conf = [t for t in full_tags if t not in full_tag_over_conf]
            sample = convert_to_prompt(full_tags, model_prefix=["score_7_up, anime"],
                                       keep_token_tags=main_tags+secondary_tags, post_filter=post_filter_tags,
                                       tags_under_conf=full_tags_under_conf)
            resized_resolution = self.images[i].get_bucket_size(export_width, export_height, bucket_steps)
            bucket_sizes.append(resized_resolution)
            #parameters.log.info(sample)
            #parameters.log.info(resized_resolution)
            #parameters.log.info("*"*20)
            prompts.append(sample)

        #xy_axis = [self.images[i].relative_path for i in idx_list]
        #parameters.log.info("Generating graph")
        #sns.heatmap(pair_arr,xticklabels=xy_axis, yticklabels=xy_axis, square=True, cbar_kws={'shrink': 0.8})
        #plt.show()
        
        # code to export the prompt:
        import toml
        import imagesize
        toml_path = self.folder
        toml_name = "exported_samples.toml"
        toml_full_path = os.path.join(toml_path, toml_name)
        
        neg_prompt = "monochrome, greyscale, furry, pony, blurry, simple background"
        
        # default prompt setting
        data_dict = {
            "prompt":{
                "negative_prompt" : neg_prompt,
                "scale" : 7,
                "sample_steps": 24,
                "clip_skip" : 1,
                "seed" : 42,
                "subset":[]
            }
        }
        # add the individual prompt and bucket resolution
        for prompt, resolution in zip(prompts, bucket_sizes):
            data_dict["prompt"]["subset"].append({"prompt":prompt, "width":resolution[0], "height":resolution[1]})
        
        
        with open(toml_full_path, "w") as f:
            toml.dump(data_dict, f,)
        
        
        parameters.log.info(f"Samples are added in {toml_full_path}")


    def update_images_paths(self):
        """
        try to change the path of the images in case the database is moved, so no images are lost even though the images point to a wrong path
        Returns:

        """
        possible_image_extensions = parameters.IMAGES_EXT
        all_absolute_paths_in_database_folder = files.get_all_images_in_folder(self.folder)
        all_md5_in_database_folder_tuple = files.get_multiple_md5(all_absolute_paths_in_database_folder)
        all_md5_in_database_folder = [x[0] for x in all_md5_in_database_folder_tuple]
        all_absolute_paths_in_database_folder = [x[1] for x in all_md5_in_database_folder_tuple]

        images_index = [k for k in range(len(self.images))]
        parameters.log.info(f"Database contains {len(self.images)} images")
        corrected_images = 0
        corrected_md5 = 0
        # common path for relative purposes
        try:
            common_path = os.path.commonpath([x.path for x in self.images])
            temp_images_index = []
            for k in images_index:
                reconstructed_absolute_path = os.path.join(self.folder,os.path.relpath(self.images[k].path, start=common_path))
                if os.path.exists(reconstructed_absolute_path): # self.folder + reconstructed relative path
                    if self.images[k].path != reconstructed_absolute_path:
                        if self.images[k].md5 not in all_md5_in_database_folder: # update md5
                            try:
                                self.change_md5_of_image(k, all_md5_in_database_folder[all_absolute_paths_in_database_folder.index(reconstructed_absolute_path)])
                                corrected_md5 += 1
                            except ValueError:
                                parameters.log.warning(("Weird Behaviour in reconstructed_absolute_path of images: ", reconstructed_absolute_path))
                        self.images[k].path = reconstructed_absolute_path
                        corrected_images += 1
                    else:
                        if self.images[k].md5 not in all_md5_in_database_folder: # update md5
                            try:
                                self.change_md5_of_image(k, all_md5_in_database_folder[all_absolute_paths_in_database_folder.index(reconstructed_absolute_path)])
                                corrected_md5 += 1
                            except ValueError:
                                parameters.log.warning(("Weird Behaviour in reconstructed_absolute_path of images: ", reconstructed_absolute_path))

                else:
                    temp_images_index.append(k)
            images_index = temp_images_index

        except ValueError:
            images_index = images_index

        if not images_index:
            if corrected_images:
                parameters.log.info(f"{corrected_images} were missing due to the moving of the database folder.")
            if corrected_md5:
                parameters.log.info(f"{corrected_md5} images had their md5 changed.")
            return


        # extension possibly changed

        temp_images_index = []
        corrected_images = 0
        for k in images_index:
            image_path = self.images[k].path
            possible_candidates = [os.path.splitext(image_path)[0]+ext for ext in possible_image_extensions if ext != os.path.splitext(image_path)[1]]
            corrected = False
            for candidate in possible_candidates:
                if os.path.exists(candidate):
                    if self.images[k].md5 not in all_md5_in_database_folder:  # update md5
                        try:
                            self.change_md5_of_image(k, all_md5_in_database_folder[all_absolute_paths_in_database_folder.index(candidate)])
                            corrected_md5 += 1
                        except ValueError:
                            parameters.log.warning(("Weird Behaviour in candidate of images: ", candidate))
                    self.images[k].path = candidate
                    corrected_images += 1
                    corrected = True
                    break
            if not corrected:
                temp_images_index.append(k)

        if len(images_index) > len(temp_images_index):
            parameters.log.info(f"Out of {len(images_index)}, {len(images_index) - len(temp_images_index)} were missing due to changing the extension.")
        else:
            parameters.log.info(f"Out of {len(images_index)}, 0 images had their extensions changed.")
        images_index = temp_images_index

        if not images_index:
            if corrected_md5:
                parameters.log.info(f"{corrected_md5} images had their md5 changed.")
            return

        #files moved around, md5 check todo: simply moving the file around the different folders while not changing the filename but modifying the rest, even the md5 (the one who does that is crazy)


        temp_images_index = []
        for k in images_index:
            if self.images[k].md5 in all_md5_in_database_folder:
                path_index = all_md5_in_database_folder.index(self.images[k].md5)
                self.images[k].path = all_absolute_paths_in_database_folder[path_index]
                #self.images[k].relative_path = os.path.relpath(all_absolute_paths_in_database_folder[path_index], self.folder)
            else:
                temp_images_index.append(k)

        parameters.log.info(f"Out of {len(images_index)}, {len(images_index)-len(temp_images_index)} were missing due to the moving of the image, same md5 found.")
        images_index = temp_images_index
        if images_index:
            parameters.log.info(f"{len(images_index)} images are still missing")
        else:
            if corrected_md5:
                parameters.log.info(f"{corrected_md5} images had their md5 changed.")

        first_10_missing = [uno for i, uno in enumerate([self.images[x].path for x in images_index]) if i < 10]
        if first_10_missing:
            parameters.log.info(f"First 10 paths that are missing: {first_10_missing}")

    def organise_image_paths_groups(self, remove_relative_images=True, remove_absolute_and_relative_images=True):
        """
        move the image files according to their groups, to the database path if not in a group

        Args:
            remove_absolute_and_relative_images:
            remove_relative_images: doesn't matter if remove_absolute_and_relative is set to True
        """
        images_tuples: list[tuple[int, str,str]]=[]
        for image_index in range(len(self.images)):
            current_path = os.path.normpath(self.images[image_index].path)
            if self.images[image_index].group_names: # in group
                if len(self.images[image_index].group_names)==1:
                    images_tuples.append((image_index, current_path, os.path.join(self.folder, self.images[image_index].group_names[0], os.path.basename(current_path))))
                else: # taking the one when sorting
                    images_tuples.append((image_index, current_path, os.path.join(self.folder, sorted(self.images[image_index].group_names)[0], os.path.basename(current_path))))
            else:
                images_tuples.append((image_index, current_path, os.path.join(self.folder, os.path.basename(current_path))))
        for paths in images_tuples:
            if paths[1] != paths[2]:
                if not os.path.isdir(os.path.dirname(paths[2])):
                    os.makedirs(os.path.dirname(paths[2]))
                shutil.copy2(paths[1], paths[2])
                self.images[0].path = paths[2]

                if remove_absolute_and_relative_images:
                    os.remove(paths[1])
                #elif remove_relative_images and self.images[0].relative_path and os.path.exists(os.path.join(self.folder, self.images[0].relative_path)):
                elif remove_relative_images:
                    try:
                        if os.path.commonpath([self.folder, paths[1]]) == self.folder:
                            os.remove(paths[1])
                    except ValueError:
                        pass

                #self.images[0].relative_path = paths[2][len(self.folder)+1:]
        parameters.log.info(f"Change the path of {len(images_tuples)} images")

    def reapply_md5(self, use_file_group=False):
        # update current hash and also update group

        for img in self.images:
            old_hash = img.md5
            new_hash = files.get_md5(img.path)
            parameters.log.debug(old_hash, new_hash)
            if old_hash != new_hash:
                img.md5 = new_hash

        if use_file_group:
            self.remove_groups()
            self.add_image_to_groups_by_path(self.get_all_paths())

    def create_frequency_txt(self):
        c = self.get_frequency_of_all_tags()
        with open(os.path.join(self.folder, "tag_frequency.txt"), 'w') as file:
            for tup in c:
                if tup[0] not in tag_categories.COLOR_DICT.keys():
                    file.write(f"{tup[1]}: {tup[0]}\n")

    def export_database(self, images_index: list[int], export_path: str, export_group_name: str=""):
        export_database = Database(export_path)
        export_md5_list = export_database.get_all_md5()
        for index in images_index:
            if self.images[index].md5 not in export_md5_list:
                to_export_image = copy.deepcopy(self.images[index])
                # copy the file name
                if not export_group_name:
                    new_path = os.path.join(export_path, os.path.basename(to_export_image.path))
                else:
                    new_path = os.path.join(export_path, export_group_name, os.path.basename(to_export_image.path))

                try:
                    shutil.copy2(to_export_image.path, new_path)
                except FileNotFoundError:
                    os.makedirs(os.path.dirname(new_path))
                    shutil.copy2(to_export_image.path, new_path)

                to_export_image.path = new_path
                export_database.images.append(to_export_image)
                export_database.add_image_to_group(export_group_name, len(export_database.images)-1)

            # todo: make the conditions when the md5 is present in the database
            else:
                to_export_image = copy.deepcopy(self.images[index])
                # compare images between present and export database
                export_index = export_database.index_of_image_by_md5(to_export_image.md5)

                # adding it to the groups
                export_database.add_image_to_group(export_group_name, export_index)

                # merge manuals
                export_database.images[export_index].append_manual_tags(to_export_image.manual_tags)
                export_database.images[export_index].append_rejected_manual_tags(to_export_image.rejected_manual_tags)
                export_database.images[export_index].resolved_conflicts = list(set(to_export_image.resolved_conflicts + export_database.images[export_index].resolved_conflicts))

                # add sentence
                if not export_database.images[export_index].sentence_description and to_export_image.sentence_description:
                    export_database.images[export_index].sentence_description = to_export_image.sentence_description

                # merge possible external tags
                for key, value in to_export_image.external_tags:
                    if key not in export_database.images[export_index].external_tags.keys():
                        export_database.images[export_index].add_external_tags_key(key, value)

                # don't touch automatic tags

                # find the best original md5: take one that is different from current and if both are different the one with data from rule34
                if to_export_image.original_md5 != export_database.images[export_index].original_md5:

                    to_export_image_diff_o_md5 = False
                    from_export_image_diff_o_md5 = False

                    if to_export_image.original_md5 != to_export_image.md5:
                        to_export_image_diff_o_md5 = True
                    if export_database.images[export_index].original_md5 != export_database.images[export_index].md5:
                        from_export_image_diff_o_md5 = True

                    if to_export_image_diff_o_md5 and not from_export_image_diff_o_md5:
                        export_database.images[export_index].original_md5 = to_export_image.original_md5
                        # no need for the other case
                    elif from_export_image_diff_o_md5 and to_export_image_diff_o_md5:

                        # check if any has external tags data, todo: make it specific to online data
                        if not export_database.images[export_index].external_tags and to_export_image.external_tags:
                            export_database.images[export_index].original_md5 = to_export_image.original_md5
        export_database.save_database()


