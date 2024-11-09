import concurrent.futures
import copy
import html
import json
import os
import pathlib
import shutil
from collections import Counter
import tqdm

import tools
import tools.images
from classes.class_image import *
from resources import parameters, tag_categories
from tools import files, tagger_caller
from tools.misc_func import tqdm_parallel_map, order_tag_prompt


class VirtualDatabase:
    def __init__(self):
        self.images: list[ImageDatabase] = []
        self.duplicate_paths = []
        self.similar_images: list[tuple[set[int], float]] = []
        self.trigger_tags = {
            'main_tags': [],
            'secondary_tags': []
        }
        self.groups: dict[str: GroupElement] = {}

        #Temp Info
        self.rare_tags = set()

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

    def index_of_image_by_original_md5(self, image_md5) -> int:
        # todo: return -1 in case of failure
        return self.get_all_original_md5().index(image_md5)

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

    def multi_tagger_call(self, image_paths: list[str], tagging_models:list[str], extra_args=None):
        """
        this is only called by the call_models function below, this gets the results and interpert the values
  
        Function responsible for calling the model manager and updating values based on results,
        You can call one or multiple models by listing the models you want to run in the args

        Args:
            image_paths (list[str]): list of image paths to be tagged
            tagging_models (list[str]): list of taggers you want to use
            extra_args (_type_, optional): extra args sent to the model manager. Defaults to None.
                currently only used for Swinv2v3 tagging character's only
    
        return nothing, initailize/updates internal database values
        """
        def convert_detection(detection_list):
            # the data from yolo is a list containing:
            # [(top corner x, top corner y, bottom corner x, bottom corner y), n, c]
            # the coords need to converted to (top corner x, top corner y, width, height)
            data = [{	"name":n,
                        "coordinates":(x0, y0, x1-x0, y1-y0),
                        "confidence":c
                    } for ((x0, y0, x1, y1), n, c) in detection_list]
            return data
  
        tagger_models_str = []
        for t in tagging_models:
            if not isinstance(t, str): # if it's a enum thing
                tagger_models_str.append(t.value)
            else:
                tagger_models_str.append(t)

        # a dict to get the index of images via paths
        index_dict = self.get_img_path_index_dict()
  
        # results is a dict of a dict, storing the different results from the models, then we send all of it to the different update functions
        # results = {tagging_model_name: {img_path : tagged_result}}
        # the tagged_result can be different structure or types depending on the model
        results = tagger_caller.multi_model_caller(image_paths, tagger_models_str, extra_args=extra_args)



        # here we list the way we update the internal values based on results
        if "anime_aesthetic" in results: # update scores
            for img_path, new_score in results["anime_aesthetic"].items():
                self.images[index_dict[img_path]].init_image_dict({"score_label": str(new_score[0]), "score_value": float(new_score[1])})
        if "anime_classifier" in results: # update classification
            for img_path, class_score in results["anime_classifier"].items():
                self.images[index_dict[img_path]].init_image_dict({"classify_label": str(class_score[0]), "classify_value": float(class_score[1])})
        if "anime_completeness" in results: # roughness of the art
            for img_path, class_score in results["anime_completeness"].items():
                self.images[index_dict[img_path]].init_image_dict({"completeness_label": str(class_score[0]), "completeness_value": float(class_score[1])})
        if "Caformer" in results: # update caformer tags
            for img_path, new_tags in results["Caformer"].items():
                self.images[index_dict[img_path]].init_image_dict({"auto_tags": {"Caformer": new_tags}})
        if "Swinv2v3" in results: # update swin tags, two cases for char only vs normal case
            characters_only = False
            if extra_args and "Swinv2v3" in extra_args:
                characters_only = extra_args["Swinv2v3"].get("characters_only", False)
    
            for img_path, new_tags in results["Swinv2v3"].items():
                # characters are merged to pre-existing tags of the same model,otherwise newly initialized
                image_index = index_dict[img_path]
                if characters_only: # tagging only characters
                    if "Swinv2v3" in self.images[image_index].auto_tags.names():
                        result = {"auto_tags": {"Swinv2v3": list(set(self.images[image_index].auto_tags["Swinv2v3"] + new_tags))}}
                    else:
                        result = {"auto_tags": {"Swinv2v3": new_tags}}
                    self.images[image_index].init_image_dict(result)
                else:
                    self.images[index_dict[img_path]].init_image_dict({"auto_tags": {"Swinv2v3": new_tags}})
        if "Eva02_largev3" in results:  # update swin tags, two cases for char only vs normal case
            characters_only = False
            if extra_args and "Eva02_largev3" in extra_args:
                characters_only = extra_args["Eva02_largev3"].get("characters_only", False)

            for img_path, new_tags in results["Eva02_largev3"].items():
                # characters are merged to pre-existing tags of the same model,otherwise newly initialized
                image_index = index_dict[img_path]
                if characters_only:  # tagging only characters
                    if "Eva02_largev3" in self.images[image_index].auto_tags.names():
                        result = {"auto_tags": {
                            "Eva02_largev3": list(set(self.images[image_index].auto_tags["Eva02_largev3"] + new_tags))}}
                    else:
                        result = {"auto_tags": {"Eva02_largev3": new_tags}}
                    self.images[image_index].init_image_dict(result)
                else:
                    self.images[index_dict[img_path]].init_image_dict({"auto_tags": {"Eva02_largev3": new_tags}})
        if "detect_people" in results:
            #parameter.log.info(results["detect_people"])
            for img_path, detection_list in results["detect_people"].items():
                self.images[index_dict[img_path]].init_image_dict({"rects": convert_detection(detection_list)})
        if "detect_head" in results:
            #parameter.log.info(results["detect_head"])
            for img_path, detection_list in results["detect_head"].items():
                self.images[index_dict[img_path]].init_image_dict({"rects": convert_detection(detection_list)})
        if "detect_hand" in results:
            #parameter.log.info(results["detect_hand"])
            for img_path, detection_list in results["detect_hand"].items():
                self.images[index_dict[img_path]].init_image_dict({"rects": convert_detection(detection_list)})
        if "florence_caption"in results:
            for img_path, captions in results["florence_caption"].items():
                self.images[index_dict[img_path]].init_image_dict({"sentence_description": captions})


    def call_models(self, image_paths: list[str]=None, tag_images=False,  tag_only_character=False,
                 score_images=False, classify_images=False, grade_completeness=False, detect_people=False, 
                 detect_head=False, detect_hand=False, caption_image=False):
        """use this function to call the tagger/detection models, you can set the bools for the models you want to run
        This function preps the list of models passed to the real model caller
  
        Args:
            image_paths (list[str], None): if None, this will process all images, otherwise this takes a list of paths
            The rest are bools for which models to run
   
        Returns: nothing
        """
  
        if image_paths is None: # a check to use all paths
            image_paths = self.get_all_paths()

        # generate a list of strings passed to the model caller denoting the models to run
        model_calls = []
        extra_args = None
        if tag_images:
            model_calls.extend(parameters.PARAMETERS["automatic_tagger"])
        if tag_only_character:
            model_calls.append("Swinv2v3")
            extra_args = {"Swinv2v3":{"characters_only":True}}
        if score_images:
            model_calls.append("anime_aesthetic")
        if classify_images:
            model_calls.append("anime_classifier")
        if grade_completeness:
            model_calls.append("anime_completeness")
        if detect_people:
            model_calls.append("detect_people")
        if detect_head:
            model_calls.append("detect_head")
        if detect_hand:
            model_calls.append("detect_hand")
        if caption_image:
            model_calls.append("florence_caption")

        parameters.log.info(f"Running the following models {model_calls}")
        if any(model_calls):
            self.multi_tagger_call(image_paths, model_calls, extra_args)

    def _get_reapplied_paths(self, images_index: list[int]=None):
        return [self.images[x].path for x in images_index] if images_index else self.get_all_paths()

    def re_call_models(self, image_indices: list[int]=None, tag_images=False,  tag_only_character=False,
                    score_images=False, classify_images=False, grade_completeness=False,
                    detect_people=False, detect_head=False, detect_hand=False, caption_image=False
                    ):
        """This prints a message for what is reapplied to the images and calls the model callers
        """
        image_paths = self._get_reapplied_paths(image_indices) # if none, get all paths

        message_type = ["retagged", "retagged (characters only)", "rescored", "reclassified",
                        "regraded", "redetect people", "redetect head", "redetect hands", "recaption"]
        message_bools = [tag_images, tag_only_character, score_images, classify_images,
                   grade_completeness, detect_people, detect_head, detect_hand, caption_image]
        used_models_message = [mt for mt, mb in zip(message_type, message_bools) if mb]

        if len(used_models_message) > 1: # add and for multiple items
            used_models_message[-1] = "and " + used_models_message[-1]
        if len(used_models_message) > 2: # we need commas for lists with more than 3 items
            used_models_message = ", ".join(used_models_message)
        else: # no commas needed for 2 or less items
            used_models_message = " ".join(used_models_message)
  
        parameters.log.info(f"{len(image_paths)} images are going to be {used_models_message}.")

        self.call_models(image_paths, tag_images=tag_images, tag_only_character=tag_only_character, score_images=score_images,
                   classify_images=classify_images, grade_completeness=grade_completeness, detect_people=detect_people,
                    detect_head=detect_head, detect_hand=detect_hand, caption_image=caption_image)

    def filter_all(self):
        if len(self.images) < 100:
            for image in self.images:
                image.filter()
        else:
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=64)
            for image in self.images:
                pool.submit(lambda i: i.filter(), image)
            pool.shutdown(wait=True)
        parameters.log.info("Filter applied to all images")

    def update_filter_review(self):
        for image in self.images:
            image.update_review_tags()

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
                for _ in tqdm_parallel_map(pool, lambda i: i.filter_sentence(), self.images):
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

    def reset_scores(self, images_index: list[int]):
        """
        automatically reset scores for all images
        """
        for image_index in images_index:
            self.images[image_index].reset_score()

    def create_txt_files(self, add_backslash_before_parenthesis=False, token_separator=True, keep_tokens_separator="|||", use_trigger_tags=True, use_aesthetic_score=False, use_sentence=False, sentence_in_trigger=False, remove_tags_in_sentence=True, score_trigger=True, shuffle_tags=True):
        token_keeper = keep_tokens_separator
        if not token_separator:
            token_keeper = ""
        main_tags = self.trigger_tags["main_tags"]
        secondary_tags = self.trigger_tags["secondary_tags"]
        if not use_trigger_tags:
            main_tags = []
            secondary_tags = []
        for image in self.images:

            to_write = image.create_output(add_backslash_before_parenthesis=add_backslash_before_parenthesis,
                                           keep_tokens_separator=token_keeper,
                                           main_tags=main_tags,
                                           secondary_tags=secondary_tags,
                                           use_aesthetic_score=use_aesthetic_score,
                                           use_sentence=use_sentence,
                                           sentence_in_trigger=sentence_in_trigger,
                                           remove_tags_in_sentence=remove_tags_in_sentence,
                                           score_trigger=score_trigger,
                                           shuffle_tags=shuffle_tags
                                           )
            with open(os.path.join(os.path.splitext(image.path)[0] + ".txt"), 'w') as f:
                f.write(to_write + "\n")
        parameters.log.info("Successfully created the .txt files containing full tags")

    def get_img_path_index_dict(self):
        return {img.path: i for i, img in enumerate(self.images)}

    def get_all_paths(self):
        return [img.path for img in self.images]

    def get_all_image_indices(self):
        return list(range(len(self.images)))

    def get_all_md5(self):
        return [img.md5 for img in self.images]

    def get_all_original_md5(self):
        return [img.original_md5 for img in self.images]

    def add_image_to_group(self, group_name, image_index):
        """
        create the group if necessary
        Args:
            group_name:
            image_index:

        Returns: Nothing

        """
        if group_name not in self.groups:
            self.groups[group_name] = GroupElement(group_name=group_name, md5s=[self.images[image_index].md5])

        if self.images[image_index].md5 in self.groups[group_name].md5s:
            return

        self.groups[group_name].append(self.images[image_index].md5)
        self.images[image_index].groups.append(self.groups[group_name])

    def add_images_to_group(self, group_name, images_index: list[int]):
        """
        create the group if necessary
        Args:
            group_name:
            images_index:

        Returns: Nothing

        """
        for image_index in images_index:
            self.add_image_to_group(group_name, image_index)

    def remove_image_from_group(self, group_name, image_index):
        """
        remove the image from the group
        Args:
            group_name:
            image_index:
        """
        if group_name not in self.groups:
            return

        if self.images[image_index].md5 not in self.groups[group_name].md5s:
            return

        self.groups[group_name].remove(self.images[image_index].md5)
        self.images[image_index].groups.pop(self.images[image_index].groups.index(group_name))

    def remove_empty_groups(self):
        to_remove = []
        for group_name in self.groups.keys():
            if not len(self.groups[group_name]):
                to_remove.append(group_name)
        if not to_remove:
            return
        for group_name in to_remove:
            self.groups.pop(group_name)

    def create_images_objects(self, max_image_size):
        if parameters.PARAMETERS["view_load_images"]:
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
            for _ in tqdm_parallel_map(pool, lambda image: image.get_image_object((max_image_size, max_image_size)), self.images):
                pass
            pool.shutdown(wait=True)
        else:
            thumb_image = Image.open(parameters.PARAMETERS["view_placeholder_default_path"])
            thumb_image.thumbnail((max_image_size, max_image_size))
            thumb_image = ImageQt.ImageQt(thumb_image)
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
            for _ in tqdm_parallel_map(pool, lambda image: image.get_image_object((max_image_size, max_image_size), thumb_image), self.images):
                pass
            pool.shutdown(wait=True)

    def update_image_objects(self, max_image_size, image_indexes):
        if parameters.PARAMETERS["view_load_images"]:
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
            for k in image_indexes:
                pool.submit(self.images[k].load_image_object((max_image_size, max_image_size)))
            pool.shutdown(wait=True)
        else:
            parameters.log.info("Thumbnails were chosen, only updating width and height")
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
            for k in image_indexes:
                pool.submit(self.images[k].load_image_parameters())
            pool.shutdown(wait=True)

    def tokenize_all_images(self):
        all_full_tags = [", ".join(x.get_full_only_tags()) for x in self.images]
        all_tokens = tokenize(all_full_tags, context_length=500, truncate=True).count_nonzero(dim=1)
        all_sentences = [x.sentence_description.sentence for x in self.images]
        all_sentence_tokens = tokenize(all_sentences, context_length=500, truncate=True).count_nonzero(dim=1)
        for k in range(len(self.images)):
            self.images[k].full_tags.token_length = all_tokens[k] - 2
            self.images[k].sentence_description.token_length = all_sentence_tokens[k] - 2

    def remove_images_by_path(self, path_list):
        db_index_dict = self.get_img_path_index_dict() # speed things up with a reverse dict search
        path_indexes = [db_index_dict[p] for p in path_list]
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
            return self.get_all_image_indices()
        all_grouped_images = set()
        for group in self.groups.values():
            if len(group):
                all_grouped_images.update(group.md5s)
        all_images_md5 = self.get_all_md5()
        return self.index_of_images_by_md5([x for x in all_images_md5 if x not in all_grouped_images])

    def find_similar_images(self):
        if self.similar_images:
            return False

        # a list of set with the index of the two images
        self.similar_images: list[tuple[set[int], float]] = []
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
                    self.similar_images[k] = (self.similar_images[k][0].union({image_0, image_1}), (self.similar_images[k][1]*(len(self.similar_images[k][0])/(len(self.similar_images[k][0])+1)))+(similar_images[i][2]*(1/(len(self.similar_images[k][0])+1))))
                    added = True
            if not added:
                self.similar_images.append(({image_0, image_1}, similar_images[i][2]))

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
        self.similar_images.sort(key=lambda x: (x[1], len(x[0])))
        self.add_similarity_group_to_image()
        return True

    def add_similarity_group_to_image(self):
        if not self.similar_images:
            return False
        for image in self.images:
            image.similarity_group = 0
            image.similarity_probability = 0.0
        for k in range(len(self.similar_images)):
            for i in self.similar_images[k][0]:
                self.images[i].similarity_group = k+1
                self.images[i].similarity_probability = self.similar_images[k][1]

    def remove_groups(self):
        """
        remove all occurrences of existing groups
        """
        self.groups = {}
        for image in self.images:
            image.groups = []

    def remove_group(self, group_name):
        """
        remove all occurrences of existing group
        """
        del self.groups[group_name]
        for image in self.images:
            if group_name in image.groups:
                image.groups.remove(group_name)

    def change_md5_of_image(self, image_index, new_md5):
        """
        update all locations in where the md5 is used in the database and update the md5 of the image
        Args:
            image_index:
            new_md5:
        """
        for group in self.groups.values():
            if self.images[image_index].md5 in group.md5s:
                group[self.images[image_index].md5] = new_md5
        self.images[image_index].md5 = new_md5
        for group in self.images[image_index].groups:
            group[self.images[image_index].md5] = new_md5

    def purge_manual_tags(self, images_index: list[int]):
        """
        remove all manual tags and manual rejected tags, not entirely cleaned from human intervention though
        Args:
            images_index:
        """
        for index in images_index:
            self.images[index].rejected_manual_tags.clear()
            self.images[index].manual_tags.clear()
            self.images[index].filter()

    def purge_human_intervention(self, images_index: list[int]):
        """
        remove all human intervention, doesn't filter
        """
        for index in images_index:
            self.images[index].rejected_manual_tags.clear()
            self.images[index].manual_tags.clear()
            self.images[index].manually_reviewed = False
            self.images[index].resolved_conflicts = []
            if self.images[index].score_value:
                self.images[index].reset_score()
            self.images[index].filter()

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
                    self.images[image_index].sentence_description.sentence = tags
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
                image.init_image_dict({"external_tags": {"danbooru": all_tags}})
        parameters.log.info(f"Successfully retrieved danbooru tags for {successful_retrievals} images")

    def retrieve_gelbooru_tags_all_images(self, unsafe: bool=True):
        self.retrieve_gelbooru_tags(self.get_all_image_indices(), unsafe)

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
                    image.init_image_dict({"external_tags": {"gelbooru": all_tags}})
                else:
                    accepted_gelbooru = []
                    for tag in all_tags:
                        if tag in all_accepted_tags:
                            accepted_gelbooru.append(tag)
                    image.init_image_dict({"external_tags": {"gelbooru": accepted_gelbooru}})
                    image.init_image_dict({"external_tags": {"rejected_gelbooru": all_tags}})
        parameters.log.info(f"Successfully retrieved gelbooru tags for {successful_retrievals} images")

    def retrieve_rule34_tags_all_images(self, unsafe: bool=True):
        self.retrieve_rule34_tags(self.get_all_image_indices(), unsafe=unsafe)

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
            elif response.status_code == 200 and len(os.path.splitext(os.path.basename(image.path))[0]) == 32 and os.path.splitext(os.path.basename(image.path))[0] != image.original_md5:
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
                    image.init_image_dict({"external_tags": {"rule34": all_tags}})
                else:
                    accepted_rule34 = []
                    for tag in all_tags:
                        if tag in all_accepted_tags:
                            accepted_rule34.append(tag)
                    image.init_image_dict({"external_tags": {"rule34": accepted_rule34}})
                    image.init_image_dict({"external_tags": {"rejected_rule34": all_tags}})
        parameters.log.info(f"Successfully retrieved rule34 tags for {successful_retrievals} images")

    def rename_images_to_png(self, images_index: list[int]):
        for index in images_index:
            image = self.images[index]
            if os.path.exists(image.path) and os.path.splitext(image.path)[1].lower() != ".png":
                dst_path = os.path.splitext(image.path)[0]+".png"
                if files.convert_image_to_png(image.path, dst_path):
                    image.path=dst_path
                    self.change_md5_of_image(index, files.get_md5(image.path))

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

    def get_frequency_of_all_tags(self) -> list[tuple[str, int]]:
        """Use a Counter object to collect frequency, then returns the dict version of the results, sorted by most common

        Returns:
            list[tuple[str, int]]: tags : frequency count
        """
        c = Counter()
        for image in self.images:
            c.update([str(tag) for tag in image.get_full_tags()])
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

    def cleanup_all_images_rejected_tags(self):
        self.cleanup_images_rejected_tags([k for k in range(len(self.images))])

    def cleanup_images_rejected_tags(self, images_index: list[int]):
        """
        This function removes all rejected manual tags that are not removing any tag
        """
        for index in images_index:
            self.images[index].cleanup_rejected_manual_tags()

    def update_rare_tags(self):
        if not self.rare_tags:
            load_tag_perc = parameters.PARAMETERS["frequency_rare_tag_threshold"]*len(self.images)
            low_frequency_tags = set([tag for tag, freq in self.get_frequency_of_all_tags() if freq <= load_tag_perc])
            self.rare_tags = low_frequency_tags
        for image in self.images:
            image.rare_tags_count = self.rare_tags.intersection(image.get_full_only_tags())

    def get_rare_tags(self):
        if not self.rare_tags:
            load_tag_perc = parameters.PARAMETERS["frequency_rare_tag_threshold"]*len(self.images)
            low_frequency_tags = set([tag for tag, freq in self.get_frequency_of_all_tags() if freq <= load_tag_perc])
            self.rare_tags = low_frequency_tags
        return self.rare_tags

    def __eq__(self, other):
        # test if correct object
        if not isinstance(other, type(self)):
            return False
        # test if same group names
        if self.groups != other.groups:
            return False
        # test if same main trigger tags, order matters
        if self.trigger_tags['main_tags'] != other.trigger_tags['main_tags']:
            return False
        # test if same secondary trigger tags, order doesn't matter
        if set(self.trigger_tags['secondary_tags']) != set(other.trigger_tags['secondary_tags']):
            return False
        # test if same amount of images
        if len(self.images) != len(other.images):
            return False
        # test if same images, order matters
        for k in range(len(self.images)):
            if self.images[k] != other.images[k]:
                return False
        return True

    def get_changes(self, other):
        """
        Returns a dict close to the saving dict (except that it uses images index instead of md5 to save) that contains only the entries that are changed from the other database
        Args:
            other: database assimilated to be the older database

        Returns:
            dict that contains ony the different entry for the database
        """
        result = defaultdict(lambda:{})
        for k in range(len(self.images)):
            image_result = self.images[k].get_changes(other.images[k])
            if image_result:
                result["images"][k] = image_result
        # test if same main trigger tags, order matters
        if self.trigger_tags['main_tags'] != other.trigger_tags['main_tags']:
            result["trigger_tags"]["main_tags"] = self.trigger_tags['main_tags']
        # test if same secondary trigger tags, order doesn't matter
        if set(self.trigger_tags['secondary_tags']) != set(other.trigger_tags['secondary_tags']):
            result["trigger_tags"]["secondary_tags"] = self.trigger_tags['secondary_tags']

        if self.groups != other.groups:
            for group in self.groups.values():
                result["groups"][group.group_name] = group.save()
        return copy.deepcopy(result)

    def apply_changes(self, changes: dict):
        """
        change the database to apply the changes from the result dict
        Args:
            changes: the dict return by the get_changes
        """
        if "images" in changes.keys():
            for k, image_dict in changes["images"].items():
                self.images[k].apply_changes(image_dict)
        if "trigger_tags" in changes.keys():
            if "main_tags" in changes["trigger_tags"].keys():
                self.trigger_tags["main_tags"] = changes["trigger_tags"]["main_tags"]
            if "secondary_tags" in changes["trigger_tags"].keys():
                self.trigger_tags["secondary_tags"] = changes["trigger_tags"]["secondary_tags"]
        if "groups" in changes.keys():
            if changes["groups"]:
                self.remove_groups()
                for group_name, group in changes["groups"].items():
                    self.add_images_to_group(group_name, group["images"])

    def apply_all_changes(self, all_changes: list[dict]):
        """
        change the database to apply the changes from the result dict
        Args:
            all_changes: the list containing dicts that will be sequentially applied to the database (the first one is applied first, etc ...)
        """
        for change in all_changes:
            self.apply_changes(change)

    def get_saving_dict(self):
        result = {"images":{}}
        for image in self.images:
            result["images"][image.md5] = image.get_saving_dict()
        result["trigger_tags"] = self.trigger_tags
        result["groups"] = {}
        for group in self.groups.values():
            result["groups"][group.group_name] = group.save()
        return result

    def get_common_image(self, images_index: list[int]) -> ImageDatabase:
        """
        Args:
            images_index: list of images index

        Returns:
            - an image database,
            - an uncommon tags list, the tags that are not common between all the images
        """
        common_image = ImageDatabase()
        common_image.auto_tags = copy.deepcopy(self.images[images_index[0]].auto_tags)
        common_image.external_tags = copy.deepcopy(self.images[images_index[0]].external_tags)
        common_image.manual_tags = copy.deepcopy(self.images[images_index[0]].manual_tags)
        common_image.rejected_manual_tags = copy.deepcopy(self.images[images_index[0]].rejected_manual_tags)
        common_image.secondary_rejected_tags = copy.deepcopy(self.images[images_index[0]].secondary_rejected_tags)
        common_image.secondary_new_tags = copy.deepcopy(self.images[images_index[0]].secondary_new_tags)

        for image_index in images_index[1:]:
            image = self.images[image_index]
            common_image.auto_tags = common_image.auto_tags.common_tags(image.auto_tags)
            common_image.external_tags = common_image.external_tags.common_tags(image.external_tags)
            common_image.manual_tags = common_image.manual_tags.all_tags_in(image.manual_tags)
            common_image.rejected_manual_tags = common_image.rejected_manual_tags.all_tags_in(image.rejected_manual_tags)
            common_image.secondary_rejected_tags = common_image.secondary_rejected_tags.all_tags_in(image.secondary_rejected_tags)
            common_image.secondary_new_tags = common_image.secondary_new_tags.all_tags_in(image.secondary_new_tags)

        common_image.manually_reviewed = True if all(self.images[index].manually_reviewed for index in images_index) else False
        common_image.score_label = self.images[0].score_label if all(self.images[index].score_label == self.images[0].score_label for index in images_index) else TagElement("")
        common_image.classify_label = self.images[0].classify_label if all(self.images[index].classify_label == self.images[0].classify_label for index in images_index) else TagElement("")
        common_image.filter()

        common_image.uncommon_tags = defaultdict(lambda:0.0)
        iterate_per_step = 1/len(images_index)

        for image_index in images_index:
            for tag in self.images[image_index].get_full_tags():
                if tag not in common_image.full_tags:
                    common_image.uncommon_tags[tag] += iterate_per_step

        return common_image

    def changed_common_image(self, new_image: ImageDatabase, selected_indexes: list[int]):
        """
        Changes data in images with the common data changed
        Args:
            new_image:
            selected_indexes:

        Returns: True if changes happened, False otherwise

        """
        previous_image = self.get_common_image(selected_indexes)
        changes_happened = False

        # I need the to add the new tags and remove the tags that are removed
        if previous_image.manual_tags != new_image.manual_tags:
            changes_happened = True
            # remove unwanted tags (tags in previous_image but not in new_image)
            unwanted_tags = previous_image.manual_tags - new_image.manual_tags
            if unwanted_tags:
                for index in selected_indexes:
                    self.images[index].manual_tags -= unwanted_tags
            # add wanted tags (tags in new_image but not in previous_image)
            wanted_tags = new_image.manual_tags - previous_image.manual_tags
            if wanted_tags:
                for index in selected_indexes:
                    self.images[index].manual_tags += wanted_tags

        if previous_image.rejected_manual_tags != new_image.rejected_manual_tags:
            changes_happened = True
            unwanted_tags = previous_image.rejected_manual_tags - new_image.rejected_manual_tags
            if unwanted_tags:
                for index in selected_indexes:
                    self.images[index].rejected_manual_tags -= unwanted_tags
            wanted_tags = new_image.rejected_manual_tags - previous_image.rejected_manual_tags
            if wanted_tags:
                for index in selected_indexes:
                    self.images[index].rejected_manual_tags += wanted_tags

        if previous_image.manually_reviewed != new_image.manually_reviewed:
            changes_happened = True
            for index in selected_indexes:
                self.images[index].manually_reviewed = new_image.manually_reviewed
        if previous_image.score_label != new_image.score_label:
            changes_happened = True
            for index in selected_indexes:
                self.images[index].score_label = new_image.score_label
        if previous_image.score_label != new_image.score_label:
            changes_happened = True
            for index in selected_indexes:
                self.images[index].score_label = new_image.score_label

        return changes_happened

class Database(VirtualDatabase):
    def __init__(self, folder):
        super().__init__()
        self.folder = folder
        self.load_database()

    def __eq__(self, other):
        if self.folder != other.folder:
            return False
        return super().__eq__(other)


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



        self.images = [ImageDatabase(image_dict) for image_dict in db["images"].values()]
        for image in self.images:
            if not old_score_system:
                try:
                    if image.score_value > 1:
                        old_score_system = True
                except KeyError:
                    pass

        # trigger tags for the database
        try:
            self.trigger_tags = db["trigger_tags"]
        except KeyError:
            parameters.log.error(f"Empty data for secondary/main trigger tags: {self.folder}")

        # groups for the image
        try:
            self.groups = {group: GroupElement(group_name=group, md5s=db["groups"][group]["images"]) for group in db["groups"].keys()}
            md5_list = self.get_all_md5()
            org_md5_list = self.get_all_original_md5()
            md5_set = set(md5_list)
            original_md5_set = set(org_md5_list)
            for group in self.groups.values():
                try:
                    for image_md5 in group.md5s:
                        try:
                            # todo : check for original md5?
                            if image_md5 in md5_set:
                                img_index = md5_list.index(image_md5)
                            else: # backup is the original md5
                                img_index = org_md5_list.index(image_md5)
                            self.images[img_index].groups.append(group)
                        except ValueError:
                            parameters.log.error(f"Error on md5 search for image: {image_md5}, image doesn't exists in the database")
                except KeyError:
                    pass
        except KeyError:
            parameters.log.error(f"Empty data for groups: {self.folder}")

        if old_score_system:
            parameters.log.warning("You should redo the score of the images in this dataset")
        self.check_img_integrity()

        parameters.log.info("Database loaded.")

    def check_img_integrity(self):
        # this checks for anything bad for training
        img_names = [os.path.splitext(i.path)[0] for i in self.images]
        if len(img_names) != len(set(img_names)):
            c = Counter()
            c.update(img_names)
            psudo_dupe_names = []
            for key, val in c.most_common():
                if val == 1:
                    break
                psudo_dupe_names.append(key)
                parameters.log.error(f"duplicate name with different extensions found, please resolve: {psudo_dupe_names}")

    def save_database(self):
        result = self.get_saving_dict()
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
                new_group_images = GroupElement(group_name=group_name)
                for group_md5 in self.groups[group_name]:
                    if group_md5 in kept_md5s:
                        new_group_images.append(group_md5)
                self.groups[group_name] = new_group_images

        elif len(to_keep) == len(self.images):
            parameters.log.info(f"All {len(self.images)} images exists")

    def add_images_to_db(self, image_paths: list[str], from_txt=False, grouping_from_path=False, move_dupes=False):
        """_summary_

        Args:
            image_paths (list[str]): _description_
            from_txt (bool, optional): _description_. Defaults to False.
            grouping_from_path (bool, optional): _description_. Defaults to False.
            move_dupes (bool, optional): _description_. Defaults to False.
   
        Return: list of img_paths added to db
        """
        parameters.log.info(f"{len(image_paths)} images are going to be added to the database. (Before dupe check)")
        current_paths = set(self.get_all_paths())
        duplicate_paths = []
        if len(image_paths) < 1:
            return False
        new_paths = []
        for image_path in image_paths:
            if image_path not in current_paths:
                image_md5 = files.get_md5(image_path)

                is_dupe = self.append_images_dict({"md5": image_md5, "original_md5": image_md5, "path": image_path})
                if not is_dupe:
                    new_paths.append(image_path)
                else:
                    duplicate_paths.append(image_path)

        parameters.log.info(f"{len(new_paths)} images are going to be added to the database. (ignoring duplicate copies)")

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
            if duplicate_paths:
                files.export_images(duplicate_paths, self.folder, "DUPLICATES")

        self.check_img_integrity()
        return new_paths

    def add_image_to_groups_by_path(self, image_paths):
        for image_path in image_paths:
            image_index = self.index_of_image_by_image_path(image_path)
            image_relative_path = os.path.relpath(self.images[image_index].path, self.folder)
            relative_dir, _ = os.path.split(image_relative_path)

            if relative_dir: # has a relative path
                self.add_image_to_group(relative_dir, image_index)

    def create_json_file(self,add_backslash_before_parenthesis=False, token_separator=True, keep_tokens_separator=parameters.PARAMETERS["keep_token_tags_separator"],
                      use_trigger_tags=True, use_aesthetic_score=True, use_sentence=False, sentence_in_trigger=False, remove_tags_in_sentence=True, score_trigger=True, shuffle_tags=True):
        image_dict = {}
        token_keeper = keep_tokens_separator if token_separator else ""
        main_tags = self.trigger_tags["main_tags"]
        secondary_tags = self.trigger_tags["secondary_tags"]
        if not use_trigger_tags:
            main_tags = []
            secondary_tags = []
        for image in self.images:
            to_write = image.create_output(add_backslash_before_parenthesis=add_backslash_before_parenthesis,
                                           keep_tokens_separator=token_keeper,
                                           main_tags=main_tags,
                                           secondary_tags=secondary_tags,
                                           use_aesthetic_score=use_aesthetic_score,
                                           score_trigger=score_trigger,
                                           use_sentence = use_sentence,
                                           sentence_in_trigger = sentence_in_trigger,
                                           remove_tags_in_sentence = remove_tags_in_sentence,
                                           shuffle_tags=shuffle_tags
                                           )
            image_dict[image.path] = {}
            image_dict[image.path]["tags"] = to_write
        with open(os.path.join(self.folder, "meta_cap.json"), 'w') as f:
            json.dump(image_dict, f, indent=4)
        parameters.log.info("Created .json for exporting data for checkpoint")

    def create_sample_toml(self, export_width=1024, export_height=1024, bucket_steps=64, token_len=77):
        # use tuple for or
        required_tags = [("1girl","1boy"), ("solo", "solo focus")]
        # samples with these tags are removed
        blacklist_tags = ["loli", "shota", "monochrome","greyscale", "comic", "close up", "white border",
                          "letterboxed", "2koma", "multiple views", "sepia"]
        # these tags are filtered out from the choosen samples
        post_filter_tags = ["heart", "heart-shaped pupils", "censored", "sketch", "signature", "spoken x", 'blurry background',
                            "blurry",
                            "though bubble", "speech bubble", 'empty speech bubble', "watermark", "navel", "collarbone"]

        main_tags = self.trigger_tags["main_tags"]
        secondary_tags = self.trigger_tags["secondary_tags"]


        from sklearn.feature_extraction.text import TfidfVectorizer
        import matplotlib.pyplot as plt
        from random import shuffle

        # filter images based on filtering preferences
        def get_filtered_index_list(required_tags, blacklist_tags):
            idx_list = []
            for idx, image in enumerate(self.images):
                full_tags = image.full_tags
                # check if (image contains required tags) and (image doesn't contain blacklisted tags)
                if all(any(or_t in full_tags for or_t in t) if type(t) is tuple else t in full_tags for t in required_tags) and all(t not in full_tags for t in blacklist_tags):
                    idx_list.append(idx)
            return idx_list

        idx_list = get_filtered_index_list(required_tags=required_tags, blacklist_tags=blacklist_tags)
        if len(idx_list) == 0:
            parameters.log.info("No candidates were found using required and blacklisted tags, removing restrictions")
            idx_list = get_filtered_index_list(required_tags=[], blacklist_tags=[])

        # if the number of total samples (in database) is greater than 1000, randomly sample 1000 to cut down computation
        max_corpus_count = 1000
        if len(idx_list) > max_corpus_count:
            shuffle(idx_list)
            parameters.log.info(f"We have {len(idx_list)} potential source images for samples, reduced to random {max_corpus_count} samples")
            idx_list = idx_list[:max_corpus_count]
        else:
            parameters.log.info(f"We have {len(idx_list)} potential source images for samples")

        # limit the sample count and df size to 5 or less based on number of filtered samples
        desired_sample_count = parameters.PARAMETERS["toml_sample_max_count"] if len(idx_list) > desired_sample_count else len(idx_list)
        min_df = 5 if len(idx_list) > min_df else len(idx_list)

        corpus = [", ".join(self.images[i].get_full_only_tags()) for i in idx_list]

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
        common_coord_val = list(set(list(similar_coord[:, 0]) + list(similar_coord[:, 1])))
        common_penatly = 30 # penalty for common tags
        #tag_len_penalty = 20 # penalty for long tags

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
            img_token_len = np.array([min(255, self.images[i].get_token_length() if i not in common_coord_val or self.images[i].get_token_length() > 77 else self.images[i].get_token_length()+common_penatly)
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

        # get the selected tags and convert them to a prompt.
        prompts = []
        bucket_sizes = []
        for i in sample_indices:
            parameters.log.info(f"Used sample: {self.images[i].path}")
            full_tags = self.images[i].get_full_only_tags()
            full_tags_under_conf = self.images[i].get_full_tags_under_confidence(confidence=0.65)
            sample = order_tag_prompt(full_tags, model_prefix_tags=[parameters.PARAMETERS['export_prepend_positive_prompt']],
                                       keep_token_tags=main_tags+secondary_tags, remove_tags=post_filter_tags,
                                       tags_under_conf=full_tags_under_conf)
            resized_resolution = self.images[i].get_bucket_size(export_width, export_height, bucket_steps)

            if resized_resolution[0] < export_width and resized_resolution[1] < export_height:
                # if the resolution is lower than the bucket size, choose a default landscape, portrait, square
                # 13:19 ratio for default
                default_ratio = 19/13
                if resized_resolution[0]>resized_resolution[1]:
                    resized_resolution = tools.images.get_bucket_size(export_width * default_ratio, export_height, export_width, export_height, bucket_steps)
                elif resized_resolution[0]<resized_resolution[1]:
                    resized_resolution = tools.images.get_bucket_size(export_width, export_height * default_ratio, export_width, export_height, bucket_steps)
                else:
                    resized_resolution = (export_width, export_height)
       
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
        toml_path = self.folder
        toml_name = "exported_samples.toml"
        toml_full_path = os.path.join(toml_path, toml_name)

        neg_prompt = parameters.PARAMETERS['export_negative_prompt']

        # default prompt setting
        data_dict = {
            "prompt":{
                "negative_prompt" : neg_prompt,
                "scale" : parameters.PARAMETERS['export_cfg_scale'],
                "sample_steps": parameters.PARAMETERS['export_sample_steps'],
                "clip_skip" : 1,
                "seed" : 42,
                "subset":[]
            }
        }
        # add the individual prompt and bucket resolution
        for prompt, resolution in zip(prompts, bucket_sizes):
            data_dict["prompt"]["subset"].append({"prompt":prompt, "width":resolution[0], "height":resolution[1]})

        with open(toml_full_path, "w") as f:
            toml.dump(data_dict, f)

        parameters.log.info(f"Samples are added in {toml_full_path}")

    def create_jsonL_file(self,add_backslash_before_parenthesis=False, token_separator=True, keep_tokens_separator=parameters.PARAMETERS["keep_token_tags_separator"],
                      use_trigger_tags=True, use_aesthetic_score=True, use_sentence=False, sentence_in_trigger=False, remove_tags_in_sentence=True, score_trigger=True, shuffle_tags=True):
        jsonL_name = "dataset.jsonl"
        token_keeper = keep_tokens_separator if token_separator else ""
        main_tags = self.trigger_tags["main_tags"]
        secondary_tags = self.trigger_tags["secondary_tags"]
        if not use_trigger_tags:
            main_tags = []
            secondary_tags = []
        # Create a list of JSON objects
        content = [
                {
                    "file_name": image.path,
                    "caption": order_tag_prompt(
                        image.create_output(
                            add_backslash_before_parenthesis=add_backslash_before_parenthesis,
                            keep_tokens_separator=token_keeper,
                            main_tags=main_tags,
                            secondary_tags=secondary_tags,
                            use_aesthetic_score=use_aesthetic_score,
                            score_trigger=score_trigger,
                            use_sentence = use_sentence,
                            sentence_in_trigger = sentence_in_trigger,
                            remove_tags_in_sentence = remove_tags_in_sentence,
                            shuffle_tags=shuffle_tags
                        ),
                        model_prefix_tags=[],
                        keep_token_tags= main_tags + secondary_tags,
                        remove_tags=[],
                        tags_under_conf=[]
                    )
                }	for image in self.images
            ]
        # Write the list to a .jsonl file, one JSON object per line
        with open(os.path.join(self.folder,jsonL_name), 'w') as jsonl_file:
            for item in content:
                jsonl_file.write(json.dumps(item) + '\n')
        parameters.log.info("Created .jsonL for exporting data for checkpoint")

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

        images_index = self.get_all_image_indices()
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
            if self.images[image_index].groups: # in group
                if len(self.images[image_index].groups)==1:
                    images_tuples.append((image_index, current_path, os.path.join(self.folder, self.images[image_index].groups[0].group_name, os.path.basename(current_path))))
                else: # taking the one when sorting
                    images_tuples.append((image_index, current_path, os.path.join(self.folder, sorted(self.images[image_index].groups, key= lambda x: len(x.group_name))[0].group_name, os.path.basename(current_path))))
            else:
                images_tuples.append((image_index, current_path, os.path.join(self.folder, os.path.basename(current_path))))
        for paths in images_tuples:
            if pathlib.Path(paths[1]) != pathlib.Path(paths[2]):
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
        # todo: check if the export is okay with the new architecutre
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
                for external_list in to_export_image.external_tags.tags_lists:
                    if external_list.name not in export_database.images[export_index].external_tags:
                        export_database.images[export_index].external_tags[external_list.name] = export_database.images[export_index].external_tags[external_list.name]

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
