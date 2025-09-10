from __future__ import annotations
# annotation used for type hinting and forward referencing

import copy
import os.path
from os.path import exists, join, splitext, split

import PIL.Image
import numpy as np
import resources.tag_categories
from PIL import Image, ImageQt
from operator import itemgetter
from clip import tokenize
from collections import Counter
import math
from resources import parameters, tag_categories
from tools import images, files
from classes.class_elements import *
from tools.images import timing, overlapping_area_ratio
from tools.tag_pairing import build_recommendation_pairs
from tools.wd14_based_taggers import percentile_to_label


# ["3d", "anime coloring", "comic", "illustration", "not_painting"], the last two are removed so they're not inserted into the tags
kept_classify_tags = ["3d", "anime coloring","comic"]
kept_completeness_tags = ["rough art"]


"""
    The following keys used for saving, etc
    if you plan on adding more keys or editing behavior, make sure to check the following major functions:

    __init__
    __eq__
    init_image_dict
    get_saving_dict
    get_changes
    apply_changes
    add_new_content
    * other minor functions are also affected so check those
"""
simple_keys = ["md5", "original_md5", "path", "manually_reviewed", "resolved_conflicts", "related_md5s"]

tag_value_keys = ["score_value", "classify_value", "completeness_value"]
tag_label_keys = ["score_label", "classify_label", "completeness_label"]

manual_tags_list = ["manual_tags", "rejected_manual_tags","secondary_rejected_tags", "secondary_new_tags"]
systematic_tags_list = ["filtered_new_tags", "filtered_rejected_tags"]

sentence_keys = ["sentence_description"]
tags_lists_keys = ["auto_tags", "external_tags"]
misc_keys = ["order_added", "rects"]

tags_list_keys = manual_tags_list + systematic_tags_list
basic_keys = simple_keys + tag_value_keys

import functools, time

#from version 2, page 203 - 205 of Fluent Python by Luciano Ramalho
def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        arg_lst = [] #name = func.__name__
        if args:
            arg_lst.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ["%s=%r" % (k,w) for k, w in sorted(kwargs.items())]
            arg_lst.append(", ".join(pairs))
        arg_str = ", ".join(arg_lst)
        parameters.log.info("[%0.8fs] %s(%s) -> %r " % (elapsed, func.__name__, arg_str, result))
        return result
    return clocked

class ImageDatabase:
    def __init__(self, image_dict=None):
        # Identification
        self.md5: str= ""
        self.original_md5: str = "" #md5 of the image before any editing or anything, you should always create your database before editing images (if you want tags from boorus or other websites)
        self.related_md5s:list[str] = []
        self.path: str = "" # stores absolute path
        self.order_added = 0
        
        # Auto Tags
        self.auto_tags: TagsLists = TagsLists(name="auto_tags")
        # tags coming from websites or txt files
        self.external_tags: TagsLists = TagsLists(name="external_tags")

        # Manual Tags
        self.manual_tags: TagsList = TagsList(name="manual_tags")
        self.rejected_manual_tags: TagsList = TagsList(name="rejected_manual_tags")

        # Filtered tags
        self.filtered_new_tags: TagsList = TagsList(name="filtered_new_tags")
        self.filtered_rejected_tags: TagsList = TagsList(name="filtered_rejected_tags")
        self.filtered_review: dict[str: list[TagElement]] = {} # sub category {set of conflicting tags}
        self.resolved_conflicts: list[str] = []

        # Other Tags
        self.sentence_description: SentenceElement = SentenceElement()
        
        # the following are build dy
        self.rejected_tags: TagsList = TagsList(name="rejected_tags") # a lot of inclusion checks on rejected tags and full tags => sets
        self.full_tags: TagsList = TagsList(name="full_tags")

        # Secondary Cleaning
        self.secondary_rejected_tags: TagsList = TagsList(name="secondary_rejected_tags")
        self.secondary_new_tags: TagsList = TagsList(name="secondary_new_tags")

        # Score, Classification, and Media
        self.manually_reviewed: bool = False
        self.score_label: TagElement = TagElement("")
        self.score_value: float = 0.0
        self.classify_label: TagElement = TagElement("")
        self.classify_value: float = 0.0
        self.completeness_label: TagElement = TagElement("")
        self.completeness_value: float = 0.0
        # Groups, stores only group names, built when dataset is loaded
        self.group_names: set[str] = set()

        # Rectangles
        
        self.rects: list[RectElement] = []

        # Temporary Data
        self.image_object = None
        self.image_ratio = None
        self.image_width = None
        self.image_height = None
        self.similarity_group: int = 0
        self.similarity_probability: float = 0.0
        self.image_name = None
        self.auto_tags_merged_confidence: dict[str: float] = {}
        self.rare_tags_count = 0
        self.built_recommendations = None # used for calculating and adding recommendation

        # pixel related, one time calc done together
        self.brightness_value = None
        self.average_pixel = None
        self.contrast_comp = None
        self.underlighting = None
        self.gradient = None
        
        self.misc_numerical_types = {}
        
        if image_dict is not None:
            self.init_image_dict(image_dict)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        for simple_key in basic_keys + tags_lists_keys + tag_label_keys + sentence_keys:
            if getattr(self, simple_key) != getattr(other, simple_key):
                return False

        for tl_key in manual_tags_list:
            if getattr(self, tl_key) != getattr(other, tl_key):
                return False

        if self.rects != other.rects:
            return False

        return True

    def init_image_dict(self, image_dict):
        """
        it will work, with an image dict containing only the path, md5 or anything else
        will replace auto tags or external tags items if identical name/key
        will replace rect if rect name is in rect
        Args:
            image_dict:
        """
        new_keys = image_dict.keys()
        
        # legacy code has "swinv2v3" and we want to remove it if "Swinv2v3" exists
        if "auto_tags" in new_keys and "swinv2v3" in image_dict["auto_tags"].keys() and "Swinv2v3" in image_dict["auto_tags"].keys():
            parameters.log.info("removing old swinv2v3 tags")
            del image_dict["auto_tags"]["swinv2v3"]
        
        
        
        for simple_key in basic_keys: # updating single value metadata
            if simple_key in new_keys:
                setattr(self, simple_key, image_dict[simple_key])

        for tl_key in tags_lists_keys: # overwrite and update lists of tags (ex: caformer and swin)
            if tl_key in new_keys:
                getattr(self, tl_key).overwrite(image_dict[tl_key])

        for tl_key in tags_list_keys:
            if tl_key in new_keys:
                setattr(self, tl_key, TagsList(tags=image_dict[tl_key], name=tl_key))

        for tag_key in tag_label_keys:
            if tag_key in new_keys:
                setattr(self, tag_key, TagElement(image_dict[tag_key]))

        for sentence_key in sentence_keys:
            if sentence_key in new_keys:
                setattr(self, sentence_key, SentenceElement(image_dict[sentence_key]))

        if "rects" in new_keys:
            # Add new rects, don't delete old ones
            for new_rect in image_dict["rects"]:
                if "name" in new_rect.keys() and "coordinates" in new_rect.keys(): # temporary check on coordinates
                    # Check if name is not in self.rect
                    if new_rect["name"] in [x.name for x in self.rects]: # if same name exists
                        self.rects[[x.name for x in self.rects].index(new_rect["name"])].apply_from_dict(new_rect)
                    else: # new name to add
                        new_rect_element = RectElement(new_rect["name"])
                        new_rect_element.apply_from_dict(new_rect)
                        self.rects.append(new_rect_element)

        # legacy code convert for database old auto tags storage
        if "caformer_auto_tags" in new_keys:
            self.auto_tags["Caformer"] = image_dict["caformer_auto_tags"]
        # remove old legacy tags if new swin tag is detected
        if "swinv2_auto_tags" in new_keys and "Swinv2v3" not in self.auto_tags.names():
            self.auto_tags["Swinv2v3"] = image_dict["swinv2_auto_tags"]

        # In case we don't have an original md5, but have a md5
        if "original_md5" not in new_keys and not self.original_md5 and "md5" in new_keys:
            self.original_md5 = self.md5

        if "from_txt_tags" in new_keys:
            if image_dict["from_txt_tags"]:
                self.external_tags["legacy_from_txt"] = image_dict["from_txt_tags"]

        if "misc_numerical_types" in new_keys:
            for k, v in image_dict["misc_numerical_types"].items():
                self.misc_numerical_types[k] = v
        
        if "order_added" in new_keys:
            self.order_added = image_dict["order_added"]
        
        #todo: add filter to everything that needs it, make this function mostly parallel

    def get_saving_dict(self):
        """
        return the dict for saving the image data
        """
        result = {}
        error = False
        basically_covered_keys = simple_keys + tags_list_keys + tag_label_keys + sentence_keys + tags_list_keys
        
        for s_key in basically_covered_keys:
            # doing a hasattr to check for that attribute, 
            # getattr to get the value and checking the boolean evaluation on it (checking for empty string, zeros, etc)
            if hasattr(self, s_key) and getattr(self, s_key):
                val = getattr(self, s_key)
                if isinstance(val, (str, bool, int, float)): #md5 hash, path, labels, etc
                    result[s_key] = val
                if isinstance(val, list): # resolved_conflict list
                    result[s_key] = val
                elif isinstance(val, TagElement):
                    result[s_key] = val.save()
                elif isinstance(val, SentenceElement):
                    result[s_key] = val.save()
                elif isinstance(val, TagsList):
                    result[s_key] = val.save()
                else:
                    error = True
        
        # handles scores (ex: score, classify, completeness values), and there's the "or" in-case the value is 0 but the label is modified
        for num_val, val_label in zip(tag_value_keys, tag_label_keys): 
            val = getattr(self, num_val)
            if (val or getattr(self, val_label)) and isinstance(val, float):
                result[num_val] = val
            else:
                error = True
                       
        if self.order_added is not None and isinstance(self.order_added, int):
            result["order_added"] = self.order_added        
        if self.auto_tags and isinstance(self.auto_tags, TagsLists):
            result["auto_tags"] = self.auto_tags.save_tuple()
        if self.external_tags and isinstance(self.external_tags, TagsLists):
            result["external_tags"] = self.external_tags.save()
        if self.rects and all(isinstance(rect, RectElement) for rect in self.rects):
            result["rects"] = [x.save() for x in self.rects]
        #if error: # It seems like error is unused?
        #    parameters.log.error("error saving some parameter, pls check")
        if self.misc_numerical_types:
            kv_pair = [(k, v) for k, v in self.misc_numerical_types.items()]
            #parameters.log.info(f"saving {kv_pair}")
            result["misc_numerical_types"] = self.misc_numerical_types
        
        return result

    def add_related_md5s(self, md5s: str|list[str]):
        if isinstance(md5s, str) and md5s not in self.related_md5s and md5s != self.md5:
            self.related_md5s.append(md5s)
        else:
            self.related_md5s += [md5 for md5 in set(md5s) if md5 not in self.related_md5s and md5 != self.md5]
    
    def get_dev_value(self):
        # feel free to modify this for testing purposes, just return a sortable value
        dev_name = ["sharpness", "blockiness"]
        return self.misc_numerical_types.get("sharpness (Laplacian Variance)", 0)

    def add_misc_numerical(self, kv_tuples: list):
        for k, v in kv_tuples:
            if not isinstance(v, (int, float)):
                parameters.log.info("Misc numerical, value is non-numeric")
            
            self.misc_numerical_types[k] = v

    def get_special_tags(self) -> list[str]:
        """returns additonal tags that are derived from other attributes like completeness and classification

        Returns:
            list[str]: list of additional tags
        """
        tags = []
        if self.classify_label.tag in kept_classify_tags and self.classify_value > 0.7:
            # source of image (3d, real, anime, etc)
            tags.append(self.classify_label)
        if self.completeness_label.tag in kept_completeness_tags and self.completeness_value > 0.7:
            # add rough art
            tags.append(self.completeness_label)
        if self.rects:
            name_list = [x.name for x in self.rects]
            hand_names = [n for n in name_list if "hand_" in n]
            
            #person_names = [n for n in name_list if "person_" in n]
            #face_names = [n for n in name_list if "head_" in n]
            if len(hand_names) == 1:
                tags.append("hand")
            elif len(hand_names) > 1:
                tags.append("hands")
            if parameters.PARAMETERS["text_rect_add_tag"]:
                text_names = [n for n in name_list if "text_" in n]
                if len(text_names) == 1:
                    tags.append("text")
                elif len(text_names) > 1:
                    tags.append("texts")
                
        return tags

    def prune_overlapping_rect(self, subtype:str=""):
        """this will check the rects stored and prune any rects with 100% overlap
        in the future, I might merge some rects of the same subtypes (text, hand, face, person, ...)
        subtype: str, default empty string will use all rects, enter a string to filter by
        """
        # we sort so we can check in decreasing size, easier to do
        if len(self.rects) > 1:
            sorted_rect = sorted([r for r in self.rects if subtype=="" or subtype in r.name], key=lambda x: x.get_area(), reverse=True)
            
            prune_name = []
            i, j = 0, 1
            while i < len(sorted_rect):
                while j < len(sorted_rect):
                    if sorted_rect[j].name not in prune_name:
                        if overlapping_area_ratio(sorted_rect[j].get_coords(), sorted_rect[i].get_coords())>=0.95:
                            prune_name.append(sorted_rect[j].name)
                            
                    j+=1
                i+=1
            #if prune_name:
            #    parameters.log.info(f"pruning {prune_name}")
            self.rects = [r for r in self.rects if r.name not in prune_name]
                        
    def merge_text_rects(self):
        if self.rects: # get copies of rects and process them, also simplifying the data being passed
            new_rect_save_data = images.clean_ocr([r.save() for r in self.rects if "text" in r.name])
            non_text = [r for r in self.rects if "text" not in r.name]
            self.rects = non_text + [RectElement().apply_from_dict(d) for d in new_rect_save_data] 
            self.prune_overlapping_rect(subtype="text")
            #parameters.log.info(self.rects)

    def update_full_tags(self):
        #manual + from txt + auto tags + filtered tags +secondary tags
        self.full_tags.clear()
        self.full_tags += self.get_special_tags() # list
        self.full_tags += self.external_tags # tagslists
        self.full_tags += self.auto_tags # tagslists
        self.full_tags += self.filtered_new_tags #TagsList
        self.full_tags += self.manual_tags #TagsList
        self.full_tags -= self.get_rejected_tags() #TagsList
        self.full_tags.clean_empty()
        
    def get_prefiltered_full_tags(self):
        """
        only used by the filter
        return the full tag as if there was no filter, except for manually rejected tags
        """
        #manual + from txt + auto tags + filtered tags +secondary tags
        full_tags = TagsList(name="full_tags")
        full_tags += self.get_special_tags()
        full_tags = full_tags + self.external_tags + self.auto_tags + self.manual_tags
        full_tags -= self.rejected_manual_tags
        return full_tags

    def is_image_in_path(self,rejected_folders=parameters.PARAMETERS["discard_folder_name_from_search"]):
        """
        Returns: False if the image path doesn't exist

        Args:
            rejected_folders:
        """
        if any([x in self.path for x in rejected_folders]):
            return False
        return exists(self.path)

    def create_output(self, add_backslash_before_parenthesis=False, keep_tokens_separator: str= "|||", 
                      main_tags: list[str]=[], secondary_tags: list[str]=[], use_aesthetic_score=False, 
                      score_trigger=True, use_sentence=False, sentence_in_trigger=False, 
                      remove_tags_in_sentence=True, shuffle_tags=True):
        """
        create the txt files, need a keep token separator option
        currently the trigger tags are removed if they are in a sentence
        """
        result = ""
        if use_sentence:
            segments = self.sentence_description.get_output_info()
        else:
            segments = ["#full_tags"]

        for segment in self.sentence_description.get_output_info():
            if isinstance(segment, tuple):
                if segment[0] == "RECT":
                    if segment[1] not in [rect.name for rect in self.rects]:
                        continue # The name is not in the image

                    # todo: improve the conditions
                    result += self.rects[[rect.name for rect in self.rects].index(segment[1])].create_output(
                        add_backslash_before_parenthesis=add_backslash_before_parenthesis, 
                        keep_tokens_separator=keep_tokens_separator, main_tags=main_tags, 
                        secondary_tags=secondary_tags, use_sentence=use_sentence, shuffle_tags=shuffle_tags)

            
            elif segment == "#full_tags":
                tags = self.get_full_only_tags(sort_by_probability_and_manual=not shuffle_tags)
                if shuffle_tags:
                    np.random.shuffle(tags)
                identified_main_tags = []
                identified_secondary_tags = []

                if main_tags or secondary_tags:# use re to check for main and secondary triggers
                    for main_tag in main_tags:
                        if "*" in main_tag:
                            k = 0
                            while k < len(tags):
                                if re.fullmatch(r'.*'.join(main_tag.split("*")), tags[k]):
                                    if tags[k] not in identified_main_tags:
                                        identified_main_tags.append(tags[k])
                                    tags.remove(tags[k])
                                else:
                                    k+=1
                        elif main_tag in tags:
                            if main_tag not in identified_main_tags:
                                identified_main_tags.append(main_tag)
                            tags.remove(main_tag)
                    for secondary_tag in secondary_tags:
                        if "*" in secondary_tag:
                            k = 0
                            while k < len(tags):
                                if re.fullmatch(r'.*'.join(secondary_tag.split("*")), tags[k]):
                                    if tags[k] not in identified_secondary_tags and tags[k] not in identified_main_tags:
                                        identified_secondary_tags.append(tags[k])
                                    tags.remove(tags[k])
                                else:
                                    k+=1
                        elif secondary_tag in tags:
                            if secondary_tag not in identified_secondary_tags:
                                identified_secondary_tags.append(secondary_tag)
                            tags.remove(secondary_tag)

                temp_tags = []
                if identified_main_tags:
                    temp_tags += identified_main_tags
                if identified_secondary_tags:
                    if shuffle_tags:
                        np.random.shuffle(identified_secondary_tags)
                    temp_tags += identified_secondary_tags

                if len(segments) == 1:
                    if keep_tokens_separator:  # todo: improves all requirements
                        temp_tags.append(keep_tokens_separator)
                    if use_aesthetic_score:
                        score_label = self.score_label.tag
                        if score_label in tag_categories.QUALITY_LABELS:
                            score_idx = score_label.index(score_label)
                            score_key = "custom_scores_" + str(score_idx)
                            score_label = parameters.PARAMETERS[score_key]
                        if score_trigger:
                            temp_tags.insert(0, score_label)
                        else:
                            tags.append(score_label)
                            if shuffle_tags:
                                np.random.shuffle(tags)

                tags = temp_tags + tags
                result += ", ".join(tags)

            elif segment == "#score_label":
                if self.score_label:
                    score_label = self.score_label.tag
                    if score_label in tag_categories.QUALITY_LABELS:
                        score_idx = score_label.index(score_label)
                        score_key = "custom_scores_" + str(score_idx)
                        result += parameters.PARAMETERS[score_key]
                    else:
                        result += score_label
            else:
                result += segment

        if add_backslash_before_parenthesis:
            result = result.replace('(', '\\(').replace(')', '\\)')

        return result

    def append_resolved_conflict(self, sub_category):
        if sub_category not in self.resolved_conflicts:
            self.resolved_conflicts.append(sub_category)

    def append_manual_tags(self, tags: list | str | TagsList | TagElement):
        self.manual_tags += tags
        self.remove_rejected_manual_tags(tags)
        

    def remove_manual_tags(self, tags: list | str | TagsList | TagElement):
        self.manual_tags -= tags
        

    def remove_rejected_manual_tags(self, tags: list | str | TagsList | TagElement):
        self.rejected_manual_tags -= tags
        self.secondary_rejected_tags -= tags
        

    def append_rejected_manual_tags(self, tags: list | str | TagsList | TagElement):
        self.secondary_rejected_tags -= tags
        self.rejected_manual_tags += tags

    def append_secondary_tags(self, tags: list | str | TagsList | TagElement):
        self.secondary_new_tags += tags

    def remove_secondary_tags(self, tags: list | str | TagsList | TagElement):
        self.secondary_new_tags -= tags
    
    def append_secondary_rejected(self, tags: list | str | TagsList | TagElement):
        self.secondary_rejected_tags += tags

    def filter(self,*, update_review=False):
        self.filtered_new_tags.clear()
        self.filtered_rejected_tags.clear()
        self.filtered_review = {}
        full_tags = self.get_prefiltered_full_tags()

        # add HIGH tags if we find associated tags from TAG and LOW:
        filtered_tags = full_tags.to_high()

        # Always rejected tags
        rejected = full_tags.hard_rejected_tags()
        full_tags -= rejected

        new_tags = filtered_tags.not_hard_rejected_tags()
        full_tags += new_tags
        
        # todo: make this setting per database (have a running setting that is shared across all images in a database) + make a KEYSET in the tag_categories directly

        if parameters.PARAMETERS["filter_remove_series"]:
            rejected_remove_series = full_tags.all_tags_in(resources.tag_categories.SERIES_TAGS.keys())
            if rejected_remove_series:
                rejected += rejected_remove_series

        if parameters.PARAMETERS["filter_remove_metadata"]:
            rejected_remove_metadata = full_tags.all_tags_in(resources.tag_categories.METADATA_TAGS.keys())
            if rejected_remove_metadata:
                rejected += rejected_remove_metadata

        if parameters.PARAMETERS["filter_remove_characters"]:
            rejected_remove_characters = full_tags.all_tags_in(resources.tag_categories.CHARACTERS_TAG.keys())
            if rejected_remove_characters:
                rejected += rejected_remove_characters

        if parameters.PARAMETERS.get("filter_multiple_gender_count", False):
            boys =("multiple boys","2boys", ["3boys","4boys","5boys","6+boys"])
            girls = ("multiple girls","2girls", ["3girls","4girls","5girls","6+girls"])
            for multi_gender, pair, multiples in [boys, girls]:
                # only reject tag "multiple x" if we find "2x" and not "3x" or above
                # if both "2x" and "multiple x" in tags, but not "3x" or above, remove "multiple x"
                if (pair in full_tags and multi_gender in full_tags) and (
                    any([x not in full_tags for x in multiples])):
                    rejected+=[multi_gender]
            
            
            tags_under_thresh = full_tags.tags_under_confidence(tag_categories.p_threshold)
            tags_under_thresh_08 = full_tags.tags_under_confidence(0.8)
            for tag in tag_categories.remove_low_threshold_list:
                if tag in tags_under_thresh:
                    rejected += [tag]
        
            if 'steam' in full_tags and 'steaming body' in full_tags and any(
                [tag in full_tags for tag in tag_categories.TAG_CATEGORIES_EXCLUSIVE["BACKGROUND COLOR"]]):
                rejected += ['steam']
            
            objects = ('sex toy', 'vibrator', 'dildo', 'bead', 'strap-on', 'plug', 'magic wand', 'aneros')
            if 'vaginal object insertion' in tags_under_thresh_08 and any([obj in full_tags for obj in objects]):
                rejected += ['vaginal object insertion']
            if 'anal object insertion' in tags_under_thresh_08 and any([obj in full_tags for obj in objects]):
                rejected += ['anal object insertion']
                
            
            
        #filter out tags in low if another tag in TAGS is in the full_tags
        filtered_tags = full_tags.has_low()
        rejected += filtered_tags
        
        # removing duplicates and adding to self
        self.filtered_new_tags += new_tags - self.rejected_manual_tags
        self.filtered_rejected_tags += rejected - self.manual_tags
        
        # by this stage we're done with programmatically fixing/filtering tags

        # update the internal dict that stores the conflicts
        self.update_full_tags()
        if update_review:
            self.update_review_tags()

    def check_missing_implied_tags(self)->TagsList:
        """
        # only used by fulltags
        Checks if any autotags were added without having the implied tags, and return it to highlights if found problematic
        Ex 1: full-package futanari requires both p*ssy and futanari to be present
        Ex 2: hetero requires both male and female to be present
        

        Returns: problematic tags that are missing implicit tags
        """
        #self.rejected_tags
        #self.full_tags
        highlight_tags = TagsList()
        
        if "hetero" in self.full_tags and not self.full_tags.loose_string_check(["boy", "girl"], require_all=True):
            highlight_tags += "hetero"
        if "full-package futanari" in self.full_tags and not self.full_tags.loose_string_check(["pussy", "futanari", "penis", "girl"], require_all=True):
            highlight_tags += "full-package futanari"
        if "futanari" in self.full_tags and not self.full_tags.loose_string_check(["penis", "girl"], require_all=True):
            highlight_tags += "futanari"
        #if highlight_tags:
        #    parameters.log.info(f"potential missing tags found: {highlight_tags}")
        if 'ahegao' in self.full_tags and 'rolling eyes' not in self.full_tags:
            highlight_tags += "ahegao"
        if 'heart-shaped pupils' in self.full_tags:
            if 'pink eyes' in self.full_tags:
                highlight_tags += "heart-shaped pupils"
                highlight_tags += "pink eyes"
            if 'purple eyes' in self.full_tags:
                highlight_tags += "heart-shaped pupils"
                highlight_tags += "purple eyes"
        
        
        return highlight_tags
        

    def filter_sentence(self):
        """
        Not yet implemented, will replace words from the caption/sentence to other things that are decided somewhere else
        Returns:

        """
        return
                     
    def drop_low_single_source_autotags(self, threshold=0.7):
        # we check if auto_tags has multiple sources and we reject tags that are only from one source
        if len(self.auto_tags) > 1:
            c = Counter()
            prob_dict = self.auto_tags.tags_under_confidence(threshold)
            for tl in self.auto_tags:
                c.update(tl.simple_tags())
            for tag, count in c.most_common():
                if (count == 1 and 
                    tag in prob_dict and 
                    tag not in self.manual_tags and
                    tag not in self.rejected_manual_tags and 
                    tag not in tag_categories.CHARACTERS_TAG):
                    self.rejected_manual_tags += tag
                    
    def refresh_unsafe_tags(self, all_accepted_tags):
        self.external_tags.refresh_unsafe_tags(all_accepted_tags)

    def update_review_tags(self):
        # here we lay out the conflicts:
        # here we will only use the dict made with exclusive categories
        tags_exclusive_keyset = resources.tag_categories.TAG2SUB_CATEGORY_EXCLUSIVE.keys()
        self.filtered_review: dict[str: list[TagElement]]={}
        full_tags = set(self.full_tags.simple_tags())
        for tag in self.full_tags:
            if tag.tag in tags_exclusive_keyset:
                for sub_category in resources.tag_categories.TAG2SUB_CATEGORY_EXCLUSIVE[tag.tag]:
                    if sub_category not in self.resolved_conflicts:
                        common_tags = full_tags.intersection(resources.tag_categories.TAG_CATEGORIES_EXCLUSIVE[sub_category])
                        if len(common_tags) > 1:
                            self.filtered_review[sub_category] = TagsList(tags=common_tags)

    def update_md5(self):
        """access this function from the database level to ensure other compenents gets the correct md5s
        return a tuple of old hash and new md5 hash
        """
        old_hash = self.md5
        self.md5 = files.get_md5(self.path)
        return (old_hash, self.md5)
    
    def get_image_object(self, max_size: tuple[int, int]=None, thumbnail_image_object: ImageQt.ImageQt=None):
        """
        return a Qt image object, a thumbnail of the given size, if the image has already been loaded, the max_size won't be taken into account
        Args:
            max_size:
            thumbnail_image_object:

        Returns:
        """
        if not self.image_object:
            if not parameters.PARAMETERS["view_load_images"] and thumbnail_image_object:
                self.load_image_parameters()
                self.image_object = thumbnail_image_object
            else:
                self.load_image_object(max_size)
        return self.image_object

    def load_image_object(self, max_size: tuple[int, int]=None):
        try:
            self.image_object = Image.open(self.path)
        except PIL.Image.DecompressionBombError as e:
            parameters.log.error(f"PIL.Image.DecompressionBombError: Image is too big, path: {self.path}, loading the thumbnail image if possible, width and height won't be available for this image.")
            if os.path.exists(parameters.PARAMETERS["view_placeholder_default_path"]):
                thumb_image = Image.open(parameters.PARAMETERS["view_placeholder_default_path"])
                thumb_image.thumbnail(max_size)
                self.image_object = ImageQt.ImageQt(thumb_image)
                return
            else:
                raise e
        self.image_height = self.image_object.height
        self.image_width = self.image_object.width
        self.image_ratio = self.image_width/self.image_height
        if max_size:
            if splitext(self.path) in [".JPEG", ".JPG", ".jpeg", ".jpg"]:
                self.image_object.draft(mode='RGBA',size=max_size)
                self.image_object.load()
            else:
                self.image_object.thumbnail(max_size)
        if self.image_object.mode not in ('RGB', 'RGBA', '1', 'L', 'P'):
            parameters.log.info(f"Converting {self.path} to readable format from {self.image_object.mode}")
            self.image_object = self.image_object.convert("RGBA")

        self.image_object = ImageQt.ImageQt(self.image_object)

    def load_image_parameters(self):
        """
        Init the width, height, ratio of the image without loading it
        """
        image_object = Image.open(self.path)
        self.image_height = image_object.height
        self.image_width = image_object.width
        self.image_ratio = self.image_width / self.image_height

    def get_sentence_token_length(self):
        return self.sentence_description.get_token_length()

    def get_sentence_length(self):
        return self.sentence_description.get_sentence_length()

    def get_token_length(self):
        return self.full_tags.get_token_length()

    def get_rejected_tags(self):
        """
        recalculate the full rejected tags, and both update it and return it
        Returns:
        """
        self.rejected_tags.clear()
        self.rejected_tags += self.rejected_manual_tags + self.filtered_rejected_tags + self.secondary_rejected_tags
        return self.rejected_tags

    def get_full_tags(self):
        """
        recalculate the full rejected tags, and both update it and return it
        Returns:

        """
        self.update_full_tags()
        return self.full_tags

    def get_full_only_tags(self, sort_by_probability_and_manual=False):
        if sort_by_probability_and_manual:
            # manual and prob is built in
            sorted_tags = sorted(self.get_full_tags(), key=lambda x: (x.manual, x.probability), reverse=True)
            #for tag in sorted_tags:
            #    print(tag.tag, tag.manual, tag.probability)
            return [tag.tag for tag in sorted_tags]
        else:
            return [tag.tag for tag in self.get_full_tags().tags]

    def get_full_tags_over_confidence(self, confidence=0.7):
        """
        recalculate and update the full rejected tags, return a copy minus the autotags under confidence
        Returns:

        """

        tags_under_confidence = self.auto_tags.tags_under_confidence(confidence=confidence)
        full_tags = self.get_full_tags()
        tags = [tag.tag for tag in full_tags if tag not in tags_under_confidence or tag in self.manual_tags]
        return tags

    def get_full_tags_under_confidence(self, confidence=0.7):
        tags_under_confidence = self.auto_tags.tags_under_confidence(confidence=confidence)
        full_tags = self.get_full_tags()
        tags = [tag.tag for tag in full_tags if tag in tags_under_confidence and tag not in self.manual_tags]
        return tags

    def get_unresolved_conflicts(self):
        """
        return the filter conflicts minus resolved conflicts
        Returns: dict

        """
        return {k:v for k, v in self.filtered_review.items()}
    
    def add_to_group(self, group_name: str | list[str] | set[str]):
        if isinstance(group_name, str):
            self.group_names.add(group_name)
        elif isinstance(group_name, list):
            for g_name in group_name:
                self.group_names.add(g_name)
        elif isinstance(group_name, set): # union
            self.group_names = self.group_names | group_name
        else:
            TypeError("Unknown type adding to group name")
        
    def remove_from_group(self, group_name: str | list[str]| set[str]):
        if isinstance(group_name, str):
            self.group_names.remove(group_name)
        elif isinstance(group_name, list):
            for g_name in group_name:
                self.group_names.remove(g_name)
        elif isinstance(group_name, set): # union
            self.group_names = self.group_names - group_name
        else:
            TypeError("Unknown type removing from group name")
        
    def is_in_group(self, group_name: str):
        """
        return True if the image belong to the group_name
        Args:
            group_name:
        """
        return group_name in self.group_names

    def reset_score(self):
        """
        Recalculates the score for the image
        """
        if self.score_value != 0:
            self.score_label = percentile_to_label(self.score_value)

    def save_sentence(self, text):
        """
        save the text as the new sentence
        Args:
            text: the new sentence to save
        """
        self.sentence_description.sentence = text.strip()

    def get_recommendations(self) -> TagsList:
        """
        return the recommendations, and calculates it each time (assumes the full tags are calculated beforehand)
        Returns:
            recommendations: a list of recommended tags
        """
        # tagsList - tagslist
        used_tags = self.full_tags - self.rejected_tags
        # build recommendation is a tuple of 2 lists [tags to show in recommendation], [tags to remove if selected]
        self.built_recommendations = build_recommendation_pairs(used_tags)
        
        add_tags = TagsList(tags=self.built_recommendations[0],name="temp")

        
        
        return self.full_tags.recommendations() + add_tags - self.rejected_tags

    def add_from_recommendation(self, tag):
        self.append_manual_tags(tag)
        self.rejected_manual_tags -= tag
        if self.built_recommendations:
            if tag in self.built_recommendations[0]:
                tag_idx = self.built_recommendations[0].index(tag)
                prunable_tags = self.built_recommendations[1][tag_idx]
                
                for t in prunable_tags:
                    self.manual_tags -= t
                    self.rejected_manual_tags += t
                    # we also reject one relational depth fom the prunable tags
                    # find and reject low tags that would have been filtered by the prunable tags
                    
                    self.rejected_manual_tags += self.full_tags.get_low_for_tag(t)
                    self.rejected_manual_tags += self.rejected_tags.get_low_for_tag(t)
                         
    def get_character_conflicts_len(self) -> int:
        """
        return the number of characters in an image tags that appear in the conflicts
        """
        x = 0
        if "KNOWN CHARACTERS 1" in self.filtered_review.keys():
            x += len(self.filtered_review["KNOWN CHARACTERS 1"])
        if "KNOWN CHARACTERS 2" in self.filtered_review.keys():
            x += len(self.filtered_review["KNOWN CHARACTERS 2"])
        if "KNOWN CHARACTERS MANUAL" in self.filtered_review.keys():
            x += len(self.filtered_review["KNOWN CHARACTERS MANUAL"])
        return x

    def get_character_count(self) -> int:
        """
        return the number of characters in an image tags
        """
        x = 0
        for tag in self.full_tags:
            if tag.tag in tag_categories.CHARACTERS_TAG.keys():
                x+=1
        return x

    def get_implied_character_count(self) -> int:
        """
        return the number of implied characters in an image tags
        """
        implied_count = 0
        char_set = {"1boy","2boys","3boys","4boys","5boys","6+boys",
                    "1girl","2girls","3girls","4girls","5girls","6+girls",
                    "1other","2others","3others","4others","5others","6+others"}
        char_counts = [["1boy","2boys","3boys","4boys","5boys","6+boys"],
                       ["1girl","2girls","3girls","4girls","5girls","6+girls"],
                       ["1other","2others","3others","4others","5others","6+others"]
                       ]
        char_dict = {c:i+1 for c_list in char_counts for i, c in enumerate(c_list)}
        
        
        for tag in self.full_tags.simple_tags():
            implied_count += char_dict.get(tag, 0)
        return implied_count
        

    def get_average_pixel(self):
        if not self.average_pixel:
            _ = self.get_brightness()
        return self.average_pixel

    def get_contrast_composition(self):
        if not self.contrast_comp:
            _ = self.get_brightness()
        return self.contrast_comp

    def get_underlighting(self):
        if not self.underlighting:
            _ = self.get_brightness()
        return self.underlighting

    def get_bucket_size(self, base_height=1024, base_width=1024, bucket_steps=64) -> tuple[int, int]:
        # we didn't impliment upscale in this bucket size cause it's not a feature we use
        # implimentation from kohya's bucket manager with some explanation of the math behind it
        #base h x w is (1024, 1024) for XL and (512 x 512) or (768, 768) for SD1.5 and SD2
        # 1536 x 1536 for newer SDXL
        if self.image_object is None:
            img_obj = Image.open(self.path)
            self.image_height = img_obj.height
            self.image_width = img_obj.width
            self.image_ratio = self.image_width/self.image_height

        self.image_ratio = self.image_width / self.image_height

        # todo: for wasabi: make it work with other resolutions ??

        bucketed_resolution = images.get_bucket_size(self.image_height,self.image_width, base_height=base_height, base_width=base_width, bucket_steps=bucket_steps)

        return bucketed_resolution

    def get_brightness(self):
        # returns a np.float
        if not self.brightness_value:
            self.average_pixel, self.brightness_value, self.underlighting, self.contrast_comp = images.intensity_count(self.image_object)
        return self.brightness_value

    def get_filename(self):
        if not self.image_name:
            self.image_name = os.path.basename(self.path)
        return self.image_name

    def get_id(self):
        if self.order_added is None:
            self.order_added = 0
        return self.order_added
 
    def get_gradient(self):
        #parameters.log.debug("run")

        if not self.gradient:
            self.gradient = images.fake_gradient(self.image_object)
        parameters.log.debug(self.gradient)
        return self.gradient

    def get_score_sort_tuple(self) -> tuple[int, float]:
        to_return = 0
        if self.score_label.tag in tag_categories.QUALITY_LABELS:
            to_return = tag_categories.QUALITY_LABELS.index(self.score_label.tag) + 1
        return to_return, self.score_value

    def get_unknown_tags_count(self) -> int:
        key_dict = tag_categories.COLOR_DICT.keys()
        return len([tag for tag in self.full_tags if tag not in key_dict])

    def get_external_tag_origin(self, tag) -> list[str]:
        result = []
        for name in self.external_tags.names():
            if "rejected" not in name and tag in self.external_tags[name]:
                result.append(name)
        return result

    def get_auto_tag_origin(self, tag) -> list[tuple[str, float]]:
        result = []
        for name in self.auto_tags.names():
            if "rejected" not in name and tag in self.auto_tags[name]:
                result.append((name, self.auto_tags[name][tag.tag].probability))
        return result

    def get_search_tags(self, include_meta=True) -> set[str]:
        manual_source = "source_manual" if self.manual_tags else []
        group_names = ["group_" + x for x in self.group_names]
        rect_names = ["rect_" + x.name for x in self.rects]
        source1 = ["source_"+ x for x in self.external_tags.names()] 
        source2 = ["source_"+ x for x in self.auto_tags.names()]
        if include_meta:
            full_tags = self.full_tags + source1 + source2  + manual_source + group_names + rect_names
        else:
            full_tags = self.full_tags
        return set([tag.tag for tag in full_tags])

    def cleanup_rejected_manual_tags(self):
        k = 0
        combined_new_tags = self.manual_tags + self.external_tags + self.auto_tags + self.secondary_new_tags
        while k < len(self.rejected_manual_tags):
            if self.rejected_manual_tags[k] not in combined_new_tags:
                self.rejected_manual_tags.pop(k)
            else:
                k+=1

    def get_rare_tags_count(self):
        return self.rare_tags_count

    def get_changes(self, other):
        """
        returns a dict with data changed between states
        Args:
            other: ImageDatabase object, the older one

        Returns:
            a dict containing the changes
        """
        # todo: improve it by checking for only different tags_list in tags_lists
        result = {}
        for simple_key in basic_keys:
            if getattr(self, simple_key) != getattr(other, simple_key):
                result[simple_key] = getattr(self, simple_key)

        for tl_key in tags_lists_keys:
            if getattr(self, tl_key) != getattr(other, tl_key):
                result[tl_key] = getattr(self, tl_key)

        for tl_key in ["manual_tags", "rejected_manual_tags", "secondary_rejected_tags", "secondary_new_tags"]:
            if getattr(self, tl_key) != getattr(other, tl_key):
                result[tl_key] = getattr(self, tl_key)

        for tag_key in tag_label_keys:
            if getattr(self, tag_key) != getattr(other, tag_key):
                result[tag_key] = getattr(self, tag_key)

        for sentence_key in sentence_keys:
            if getattr(self, sentence_key) != getattr(other, sentence_key):
                result[sentence_key] = getattr(self, sentence_key)

        if self.rects != other.rects:
            result["rects"] = self.rects

        return result

    def apply_changes(self, changes):
        """
            apply changes from a dict (comes from the get_changes function), filter and update simple tags if necessary
            Args:
                changes: dict object, the newer one
        """
        # todo: improve it by checking for only different tags_list in tags_lists
        # todo: improve rects checking equals etc
        changes_keys = changes.keys()

        for simple_key in basic_keys:
            if simple_key in changes_keys:
                setattr(self, simple_key, changes[simple_key])

        for tl_key in tags_lists_keys:
            if tl_key in changes_keys:
                getattr(self, tl_key).overwrite(changes[tl_key])

        for tl_key in tags_list_keys:
            if tl_key in changes_keys:
                setattr(self, tl_key, TagsList(tags=changes[tl_key], name=tl_key))

        for tag_key in tag_label_keys:
            if tag_key in changes_keys:
                setattr(self, tag_key, TagElement(changes[tag_key]))

        for sentence_key in sentence_keys:
            if sentence_key in changes_keys:
                setattr(self, sentence_key, SentenceElement(changes[sentence_key]))

        # difference with the equals function
        if "groups" in changes_keys:
            self.group_names = changes["groups"]

        if "rects" in changes_keys:
            self.rects = changes["rects"]

        filter_conditions = ["auto_tags", "external_tags", "manual_tags", "rejected_manual_tags", "secondary_rejected_tags", "secondary_new_tags"]
        if any([condition in changes_keys for condition in filter_conditions]):
            self.filter()

    def add_new_contents(self, other: ImageDatabase):
        """
        Used when there's another database containing the same image and we may want to merge some of the content
        We assume the self version (primary database) has higher priority in most fields
        the assumed usecase is when a secondary database ran some model not applied on the primary db and we want to 
        merge some of the missing contents.
        
        Merges and overwriting rules are per attribute and based on some assumptions
        
        unchanged values in primary database:
        - path, md5, otiginal_md5, order_added 
        
        Args:
            other: ImageDatabase object, another instance of the image stored on a different database
            
        Return: bool, if merge was successful or not
        """
        
        # check at least path, md5, or original_md5 matches are the same before continuing
        other_md5s = [other.md5, other.original_md5]
        matching_source = (self.path == other.path) or (self.md5 in other_md5s) or (self.original_md5 in other_md5s)
        if not matching_source:
            return False
        
        # tagsLists section:
        for tls_key in tags_lists_keys:
            if getattr(other, tls_key): # we only check cases when other has data
                if not getattr(self, tls_key):# self lacks data, so write data from other
                    setattr(self, tls_key, getattr(other, tls_key))
                else: # both has data, need to check what to merge, tagsList has add_data function
                    getattr(self, tls_key).add_data(getattr(other, tls_key))
                                
        # TagsList and sentence section
        # the following objects supports += operations
        taglist_sentence = manual_tags_list + systematic_tags_list + sentence_keys
        for taglist_sen in taglist_sentence:
            # modify the different attributes
            setattr(self, taglist_sen, getattr(self, taglist_sen) + getattr(other, taglist_sen))
        
        # manually reviewed and resolved conflicts
        self.manually_reviewed = self.manually_reviewed or other.manually_reviewed
        if other.resolved_conflicts: # we can get away with search for small lists
            self.resolved_conflicts+=[c for c in other.resolved_conflicts if c not in self.resolved_conflicts]
        
        # score (label, percentile), classify (label, prob), completeness (label, probability) values and labels
        for t_value, t_label in zip(tag_value_keys, tag_label_keys):
            # we don't care about two cases when the other img db doesn't have anything to add
            if getattr(other, t_value) < 0.01:
                continue
            
            if not getattr(self, t_label) and getattr(other, t_label): # get new values from other
                setattr(self, t_value, getattr(other, t_value))
                setattr(self, t_label, getattr(other, t_label))
    
            elif getattr(self, t_label) and getattr(other, t_label): # both self and other has the attribute
                if t_label == "score_label": # special checks for scoring, bc user can manually change it
                    # we can't make a ruling if the score differs between self and other (small deviation is likely)
                    # so we assume "self" to contain the "prioritized" percentile value, there's 4 total cases
                    # (self label, other label): (original, original), (different, original), (different, different)==> no change
                    # (self label, other label): (original, different) ==> overwrite with other
                    
                    if getattr(self, t_label) != getattr(other, t_label): # check for when labels are different
                        original_label = percentile_to_label(getattr(self, t_value))
                        # third condition in the if statement is for legacy tagger check, prioritize newer values [0~1]
                        if (original_label == getattr(self, t_label).tag and 
                            original_label != getattr(other, t_label).tag and
                            0 <= getattr(other, t_value) <= 1): 
                            # the other image database seems to have a manually converted label
                            setattr(self, t_value, getattr(other, t_value))
                            setattr(self, t_label, getattr(other, t_label))
            # we ignore cases where "other" doesn't contain any values        
            
        # rect section
        overlap_threashold = parameters.PARAMETERS['merge_rectangle_overlap_threshold']
        if other.rects: # rects is in secondary
            if not self.rects: # primary self is missing rects data
                self.rects = other.rects
            else: # both has rects data, keep all rect in primary, and add missing/new ones
                # we will decide if the rectangle is the "same" rectangle based on name and overlapping area
                unique_names: dict[str, list[int]] = {} # stores basename --> seen index values
                def split_basename_idx(rect_name):
                    # return basename (joined) and -1 or idx
                    rect_name_split = rect_name.split("_")
                    base_names, idx = rect_name, -1
                    if len(rect_name_split) > 1 and rect_name_split[-1].isdigit(): # if index is part of name
                        base_names, idx = "_".join(rect_name_split[:-1]), int(rect_name_split[-1])    
                    return base_names, idx
                
                def store_max_idx(rect_name):
                    base_names, idx = split_basename_idx(rect_name)  
                    if idx > -1 and idx not in unique_names.get(base_names, []):
                        unique_names[base_names] = unique_names.get(base_names, []) + [idx]

                def get_unique_name(rect_name):
                    base_names, idx = split_basename_idx(rect_name)
                    if idx > -1 and idx in unique_names.get(base_names, []):
                        found=False
                        for i in range(max(unique_names[base_names])+1):
                            if not found and i not in unique_names[base_names]:
                                new_name = base_names+"_"+str(i)
                                found=True
                        if not found:
                            new_name = base_names+"_"+str(i+1)
                    else: # index is -1
                        new_name = base_names+"_"+str(0)
                    try:
                        store_max_idx(new_name)
                    except UnboundLocalError as e:
                        print(base_names, idx, unique_names.get(base_names, []))
                        raise e
                    return new_name
                
                for r in self.rects:
                    store_max_idx(r.name)
                    
                for new_rect in other.rects:
                    add_to_rects = True
                    rect_base_name, _ = split_basename_idx(new_rect.name)
                    for r in self.rects: #look for any rectangle that looks the same
                        overlap_ratio = r.get_overlapping_area_ratio(new_rect.get_coords())
                        r_base_name, _ = split_basename_idx(r.name)
                        if overlap_ratio > overlap_threashold and rect_base_name == r_base_name:
                            #parameters.log.info(f"overlapping rect found: {r_base_name}, {rect_base_name}, {overlap_ratio}")
                            add_to_rects = False
                            # we skip only when overlap is high and name base name matches
                            # the base name is different and we may have 2 rect over the same obj
                            # but the detection target may be different, Ex: detect humans vs detect female     
                    if add_to_rects:# make unique name if needed
                        new_r = new_rect.get_copy()
                        new_r.name = get_unique_name(new_r.name)
                        self.rects.append(new_r)
                        #parameters.log.info("added new rect")

        # group section
        # we combine all groups for now, but on the database level when working on multiple groups, we may update these values
        if other.group_names: 
            self.add_to_group(other.group_names)
        
        # update misc numerical types (place to store k-v pair that is unknown at this moment)  
        if other.misc_numerical_types:
            key_self = set(self.misc_numerical_types.keys())
            key_other = set(other.misc_numerical_types.keys())
            overlapping_keys = key_self.intersection(key_other)
            diff_keys = key_other - key_self
            # ignore overlap, prioritize self, we don't have a set rule for overlapping keys so we prioritize the stored value
            for k in overlapping_keys:
                pass
            
            # update different keys
            for k in diff_keys:
                v = other.misc_numerical_types[k]
                self.misc_numerical_types[k] = v
            
        return True
                        
    def tooltip(self, tag: TagElement):
        tooltip_text = f"Tag: {tag}"
        # todo: uncommon tags
        # if tag in self.uncommon_tags_keys:
        #	tooltip_text += f"\nOccurrence: {int((self.uncommon_tags[tag]/255)*100)} % of the selected images"
        if tag in tag_categories.TAG_DEFINITION.keys():
            tooltip_text += f"\nDefinition:  {tag_categories.TAG_DEFINITION[tag]}"

        external_tags_origin = self.get_external_tag_origin(tag)
        if external_tags_origin:
            tooltip_text += f"\nOrigin: {', '.join(external_tags_origin)} - external tags"
        auto_tags_origin = self.get_auto_tag_origin(tag)

        # todo tooltip for special tags

        if auto_tags_origin:
            tooltip_text += f"\nOrigin: {', '.join(['('+str(info_tuple[0])+', '+str(info_tuple[1])+')' for info_tuple in auto_tags_origin])} - auto tags"
        if tag in self.secondary_new_tags:
            tooltip_text += f"\nOrigin: secondary_new tags"
        if tag in self.filtered_new_tags:
            tooltip_text += f"\nOrigin: filtered_new tags"
        if tag in self.rejected_manual_tags:
            tooltip_text += f"\nOrigin: rejected_manual tags"
        if tag in self.filtered_rejected_tags:
            tooltip_text += f"\nOrigin: filtered_rejected tags"
        if tag in self.manual_tags:
            tooltip_text += f"\nOrigin: manual tags"
        wiki = tag.wiki()
        if wiki:
            tooltip_text += "\n\nDanbooru wiki page:\n"+wiki
        return tooltip_text

    def print_image_info(self):
        parameters.log.info(f"{'-'*20}")
        parameters.log.info(f"Image: {self.path}")
        parameters.log.info(f"MD5: {self.md5}, Original MD5: {self.original_md5}")
        parameters.log.info(f"Groups: {self.group_names}")
        parameters.log.info(f"Resolved conflicts: {self.resolved_conflicts}")
        parameters.log.info(f"Sentence description: {self.sentence_description}")
        
        parameters.log.info(f"{'-'*5}Stored Tags{'-'*5}")
        parameters.log.info(f"Auto tags: {self.auto_tags.simple_tags()}")
        parameters.log.info(f"External tags: {self.external_tags.simple_tags()}")
        parameters.log.info(f"Manual tags: {self.manual_tags.simple_tags()}")
        parameters.log.info(f"Rejected manual tags: {self.rejected_manual_tags.simple_tags()}")
        parameters.log.info(f"Secondary new tags: {self.secondary_new_tags.simple_tags()}")
        parameters.log.info(f"Secondary rejected tags: {self.secondary_rejected_tags.simple_tags()}")
        
        parameters.log.info(f"{'-'*5}Derived Tags{'-'*5}")
        parameters.log.info(f"Filtered new tags: {self.filtered_new_tags.simple_tags()}")
        parameters.log.info(f"Filtered rejected tags: {self.filtered_rejected_tags.simple_tags()}")
        
        parameters.log.info(f"{'-'*5}Final Tags{'-'*5}")
        parameters.log.info(f"Rejected tags: {self.rejected_tags.simple_tags()}")
        parameters.log.info(f"Full tags: {self.full_tags.simple_tags()}")
        



    
def percentile_to_label(percentile):
    mapping = tag_categories.QUALITY_LABELS_MAPPING
    for label, threshold in sorted(mapping.items(), key=lambda x: (-x[1], x[0])):
        if percentile >= threshold:
            return label
    return "WORST"
