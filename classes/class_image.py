import os.path
from os.path import exists, splitext

import PIL.Image
from PIL import Image, ImageQt

import resources.tag_categories
from classes.class_elements import *
from resources import parameters
from tools import images

# ["3d", "anime coloring", "comic", "illustration", "not_painting"]
kept_classify_tags = ["3d", "anime coloring","comic"]
kept_completeness_tags = ["rough art"]
simple_keys = ["md5", "original_md5", "path", "manually_reviewed", "score_value", "classify_value", "completeness_value", "resolved_conflicts"]
tags_lists_keys = ["auto_tags", "external_tags"]
tags_list_keys = ["manual_tags", "rejected_manual_tags", "filtered_new_tags", "filtered_rejected_tags",
                  "secondary_rejected_tags", "secondary_new_tags"]
tag_keys = ["score_label", "classify_label", "completeness_label"]
sentence_keys = ["sentence_description"]

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
        self.path: str = ""

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
        # Groups
        self.groups: list[GroupElement] = []

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
        self.uncommon_tags: dict[str:float] = {}

        # pixel related, one time calc done together
        self.brightness_value = None
        self.average_pixel = None
        self.contrast_comp = None
        self.underlighting = None
        self.gradient = None

        if image_dict is not None:
            self.init_image_dict(image_dict)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        for simple_key in simple_keys:
            if getattr(self, simple_key) != getattr(other, simple_key):
                return False

        for tl_key in tags_lists_keys:
            if getattr(self, tl_key) != getattr(other, tl_key):
                return False

        for tl_key in ["manual_tags", "rejected_manual_tags", "secondary_rejected_tags", "secondary_new_tags"]:
            if getattr(self, tl_key) != getattr(other, tl_key):
                return False

        for tag_key in tag_keys:
            if getattr(self, tag_key) != getattr(other, tag_key):
                return False

        for sentence_key in sentence_keys:
            if getattr(self, sentence_key) != getattr(other, sentence_key):
                return False

        if self.rects != other.rects:
            return False

        return True

    def get_special_tags(self):
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
            if len(hand_names) > 1:
                tags.append("hands")
        return tags

    def update_full_tags(self):
        #manual + from txt + auto tags + filtered tags +secondary tags
        self.full_tags.clear()
        self.full_tags += self.get_special_tags()
        self.full_tags = self.full_tags + self.external_tags + self.auto_tags + self.filtered_new_tags
        self.full_tags -= self.get_rejected_tags()
        self.full_tags += self.manual_tags

    def get_prefiltered_full_tags(self):
        """
        only used by the filter
        return the full tag as if there was no filter, except for manually rejected tags
        """
        #manual + from txt + auto tags + filtered tags +secondary tags
        full_tags = TagsList(name="full_tags")
        self.full_tags += self.get_special_tags()
        full_tags = full_tags + self.external_tags + self.auto_tags - self.rejected_manual_tags + self.manual_tags
        return full_tags

    def init_image_dict(self, image_dict):
        """
        it will work, with an image dict containing only the path, md5 or anything else
        will replace auto tags or external tags items if identical name/key
        will replace rect if rect name is in rect
        Args:
            image_dict:
        """
        new_keys = image_dict.keys()
        for simple_key in simple_keys: # updating single value metadata
            if simple_key in new_keys:
                setattr(self, simple_key, image_dict[simple_key])

        for tl_key in tags_lists_keys: # overwrite and update lists of tags (ex: caformer and swin)
            if tl_key in new_keys:
                getattr(self, tl_key).overwrite(image_dict[tl_key])

        for tl_key in tags_list_keys:
            if tl_key in new_keys:
                setattr(self, tl_key, TagsList(tags=image_dict[tl_key], name=tl_key))

        for tag_key in tag_keys:
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
        if "swinv2_auto_tags" in new_keys:
            self.auto_tags["Swinv2v3"] = image_dict["swinv2_auto_tags"]

        # In case we don't have an original md5, but have a md5
        if "original_md5" not in new_keys and not self.original_md5 and "md5" in new_keys:
            self.original_md5 = self.md5

        if "from_txt_tags" in new_keys:
            if image_dict["from_txt_tags"]:
                self.external_tags["legacy_from_txt"] = image_dict["from_txt_tags"]

        #todo: add filter to everything that needs it, make this function mostly parallel

    def is_image_in_path(self,rejected_folders=parameters.PARAMETERS["discard_folder_name_from_search"]):
        """
        Returns: False if the image path doesn't exist

        Args:
            rejected_folders:
        """
        if any([x in self.path for x in rejected_folders]):
            return False
        return exists(self.path)

    def get_saving_dict(self):
        """
        return the dict for saving the image data
        """
        result = {}
        error = False
        if self.md5 and isinstance(self.md5, str):
            result["md5"] = self.md5
        else:
            error = True
        if self.original_md5 and isinstance(self.original_md5, str):
            result["original_md5"] = self.original_md5
        else:
            error = True
        if self.path and isinstance(self.path, str):
            result["path"] = self.path
        else:
            error = True
        if self.auto_tags and isinstance(self.auto_tags, TagsLists):
            result["auto_tags"] = self.auto_tags.save_tuple()
        else:
            error = True
        if self.external_tags and isinstance(self.external_tags, TagsLists):
            result["external_tags"] = self.external_tags.save()
        else:
            error = True
        if self.manual_tags and isinstance(self.manual_tags, TagsList):
            result["manual_tags"] = self.manual_tags.save()
        else:
            error = True
        if self.rejected_manual_tags and isinstance(self.rejected_manual_tags, TagsList):
            result["rejected_manual_tags"] = self.rejected_manual_tags.save()
        else:
            error = True
        if self.sentence_description and isinstance(self.sentence_description, SentenceElement):
            result["sentence_description"] = self.sentence_description.save()
        else:
            error = True
        if isinstance(self.manually_reviewed, bool):
            result["manually_reviewed"] = self.manually_reviewed
        else:
            error = True
        if self.filtered_new_tags and isinstance(self.filtered_new_tags, TagsList):
            result["filtered_new_tags"] = self.filtered_new_tags.save()
        else:
            error = True
        if self.filtered_rejected_tags and isinstance(self.filtered_rejected_tags, TagsList):
            result["filtered_rejected_tags"] = self.filtered_rejected_tags.save()
        else:
            error = True
        if self.resolved_conflicts and isinstance(self.resolved_conflicts, list):
            result["resolved_conflicts"] = self.resolved_conflicts
        else:
            error = True
        if self.secondary_new_tags and isinstance(self.secondary_new_tags, TagsList):
            result["secondary_new_tags"] = self.secondary_new_tags.save()
        else:
            error = True
        if self.secondary_rejected_tags and isinstance(self.secondary_rejected_tags, TagsList):
            result["secondary_rejected_tags"] = self.secondary_rejected_tags.save()
        else:
            error = True
        if self.score_label and isinstance(self.score_label, TagElement):
            result["score_label"] = self.score_label.save()
        else:
            error = True
        if (self.score_value or self.score_label) and isinstance(self.score_value, float):
            result["score_value"] = self.score_value
        else:
            error = True
        if self.classify_label and isinstance(self.classify_label, TagElement):
            result["classify_label"] = self.classify_label.save()
        else:
            error = True
        if (self.classify_value or self.classify_label) and isinstance(self.classify_value, float):
            result["classify_value"] = self.classify_value
        else:
            error = True
        if self.completeness_label and isinstance(self.completeness_label, TagElement):
            result["completeness_label"] = self.completeness_label.save()
        else:
            error = True
        if (self.completeness_value or self.completeness_label) and isinstance(self.completeness_value, float):
            result["completeness_value"] = self.completeness_value
        else:
            error = True
        if self.rects and all(isinstance(rect, RectElement) for rect in self.rects):
            result["rects"] = [x.save() for x in self.rects]

        #if error: # It seems like error is unused?
        #    parameters.log.error("error saving some parameter, pls check")

        # todo: return error
        return result

    def create_output(self, add_backslash_before_parenthesis=False, keep_tokens_separator: str= "|||", main_tags: list[str]=[], secondary_tags: list[str]=[], use_aesthetic_score=False, score_trigger=True, use_sentence=False, sentence_in_trigger=False, remove_tags_in_sentence=True):
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
                    result += self.rects[[rect.name for rect in self.rects].index(segment[1])].create_output(add_backslash_before_parenthesis=add_backslash_before_parenthesis, keep_tokens_separator=keep_tokens_separator, main_tags=main_tags, secondary_tags=secondary_tags, use_sentence=use_sentence)

            elif segment == "#full_tags":
                tags = self.get_full_only_tags()
                np.random.shuffle(tags)
                identified_main_tags = []
                identified_secondary_tags = []

                if main_tags or secondary_tags:
                    for main_tag in main_tags:
                        if "*" in main_tag:
                            k = 0
                            while k < len(tags):
                                if re.fullmatch(r'.*'.join(main_tag.split("*")), tags[k]):
                                    identified_main_tags.append(tags[k])
                                    tags.remove(tags[k])
                                else:
                                    k+=1
                        elif main_tag in tags:
                            identified_main_tags.append(main_tag)
                            tags.remove(main_tag)
                    for secondary_tag in secondary_tags:
                        if "*" in secondary_tag:
                            k = 0
                            while k < len(tags):
                                if re.fullmatch(r'.*'.join(secondary_tag.split("*")), tags[k]):
                                    identified_secondary_tags.append(tags[k])
                                    tags.remove(tags[k])
                                else:
                                    k+=1
                        elif secondary_tag in tags:
                            identified_secondary_tags.append(secondary_tag)
                            tags.remove(secondary_tag)

                temp_tags = []
                if identified_main_tags:
                    temp_tags += identified_main_tags
                if identified_secondary_tags:
                    np.random.shuffle(identified_secondary_tags)
                    temp_tags += identified_secondary_tags

                if len(segments) == 1:
                    if keep_tokens_separator:  # todo: improves all requirements
                        temp_tags.append(keep_tokens_separator)
                    if use_aesthetic_score:
                        score_label = self.score_label.tag
                        if score_label in tag_categories.QUALITY_LABELS:
                            match score_label.index(score_label):
                                case 0:
                                    score_label = parameters.PARAMETERS["custom_scores_0"]
                                case 1:
                                    score_label = parameters.PARAMETERS["custom_scores_1"]
                                case 2:
                                    score_label = parameters.PARAMETERS["custom_scores_2"]
                                case 3:
                                    score_label = parameters.PARAMETERS["custom_scores_3"]
                                case 4:
                                    score_label = parameters.PARAMETERS["custom_scores_4"]
                                case 5:
                                    score_label = parameters.PARAMETERS["custom_scores_5"]
                                case 6:
                                    score_label = parameters.PARAMETERS["custom_scores_6"]
                        if score_trigger:
                            temp_tags.insert(0, score_label)
                        else:
                            tags.append(score_label)
                            np.random.shuffle(tags)

                tags = temp_tags + tags
                result += ", ".join(tags)

            elif segment == "#score_label":
                if self.score_label:
                    score_label = self.score_label.tag
                    if score_label in tag_categories.QUALITY_LABELS:
                        match score_label.index(score_label):
                            case 0:
                                result += parameters.PARAMETERS["custom_scores_0"]
                            case 1:
                                result += parameters.PARAMETERS["custom_scores_1"]
                            case 2:
                                result += parameters.PARAMETERS["custom_scores_2"]
                            case 3:
                                result += parameters.PARAMETERS["custom_scores_3"]
                            case 4:
                                result += parameters.PARAMETERS["custom_scores_4"]
                            case 5:
                                result += parameters.PARAMETERS["custom_scores_5"]
                            case 6:
                                result += parameters.PARAMETERS["custom_scores_6"]
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

    def remove_manual_tags(self, tags: list | str | TagsList | TagElement):
        self.manual_tags -= tags

    def remove_rejected_manual_tags(self, tags: list | str | TagsList | TagElement):
        self.rejected_manual_tags -= tags

    def append_rejected_manual_tags(self, tags: list | str | TagsList | TagElement):
        self.rejected_manual_tags += tags

    def append_secondary_tags(self, tags: list | str | TagsList | TagElement):
        self.secondary_new_tags += tags

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



        #filter out tags in low if another tag in TAGS is in the full_tags
        filtered_tags = full_tags.has_low()
        rejected += filtered_tags


        # removing duplicates and adding to self
        self.filtered_new_tags += new_tags - self.rejected_manual_tags
        self.filtered_rejected_tags += rejected - self.manual_tags

        # by this stage we're done with programmatically fixing/filtering tags

        # update the unresolved
        self.update_full_tags()
        if update_review:
            self.update_review_tags()

    def filter_sentence(self):
        """
        Not yet implemented, will replace words from the caption/sentence to other things that are decided somewhere else
        Returns:

        """
        return

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

    def get_full_only_tags(self):
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

    def is_in_group(self, group_name: str):
        """
        return True if the image belong to the group_name
        Args:
            group_name:
        """
        return group_name in self.groups

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

        return self.full_tags.recommendations() - self.rejected_tags

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

        if self.image_object is None:
            img_obj = Image.open(self.path)
            self.image_height = img_obj.height
            self.image_width = img_obj.width
            self.image_ratio = self.image_width/self.image_height

        self.image_ratio = self.image_width / self.image_height

        # todo: for wasabi: make it work with other resolutions ??

        bucketed_resolution = images.get_bucket_size(self.image_height,self.image_width, base_height=1024, base_width=1024, bucket_steps=64)

        return bucketed_resolution

    def get_brightness(self):
        # returns a np.float
        if not self.brightness_value:
            def intensity_count(img_object):
                # adapting code/theory from https://stackoverflow.com/a/58270890
                # I had similar idea of finding the contribution of blue on dark colors, but someone beat me to the punch
                # we also try to ignore white pixels, by removing pixels above (240, 240, 240) RGB
                np_img = np.array(img_object.convert('RGB'))
                np_square_img = np.square(np_img, dtype=np.float32)

                min_channel = np.min(np_img, axis=-1)
                max_channel = np.max(np_img, axis=-1)
                diff_channel = max_channel - min_channel

                # calculate brightness with rgb
                brightness_arr = (0.299 * np_square_img[:, :, 0]) + (0.587 * np_square_img[:, :, 1]) + (
                            0.114 * np_square_img[:, :, 2])

                # 16256 ~ 127.5^2
                brightness_loc = brightness_arr > 16256
                bright_nonwhite_loc = np.logical_and(brightness_loc, diff_channel > 10)

                # group pixels into a 3x3 grid

                # zero initialization
                H, W, _ = np_img.shape
                grid_height = H // 3
                grid_width = W // 3
                grid_avg = np.zeros((3, 3), dtype=np.float32)
                for i in range(3):
                    for j in range(3):
                        start_row, start_col = i * grid_height, j * grid_width
                        end_row = (i + 1) * grid_height if i < 2 else H
                        end_col = (j + 1) * grid_width if j < 2 else W

                        # Compute the average of the current grid cell
                        grid_avg[i, j] = np.mean(brightness_loc[start_row:end_row, start_col:end_col], axis=(0, 1), dtype=np.float32)
                parameters.log.debug(grid_avg)
                # sum of different grid shapes
                upper_sum = grid_avg[0, 0] + grid_avg[0, 1] + grid_avg[0, 2]
                upper_n_sum = upper_sum + grid_avg[1, 0] + grid_avg[1, 2]
                upper2_sum = upper_n_sum + grid_avg[1,1]
                lower_sum = grid_avg[2, 0] + grid_avg[2, 1] + grid_avg[2, 2]
                plus_shaped_sum = grid_avg[0,1] + grid_avg[1,0] + grid_avg[1,1] + grid_avg[1,2] + grid_avg[2,1]
                quadrent_sum = grid_avg[0,0] + grid_avg[0,2] + grid_avg[2,0] + grid_avg[2,2]

                # difference of different grid shapes
                center_diff = max(plus_shaped_sum/5 - quadrent_sum/4, 0.001)
                top_bottom_diff = max(np.average(upper_sum/3 - lower_sum/3), 0.001)
                bottom_top_diff = max(np.average(lower_sum/3 - upper_sum/3), 0.001)
                bottom_top2_diff = max(np.average(lower_sum/3 - upper2_sum/6), 0.001)
                parameters.log.debug(center_diff, top_bottom_diff, bottom_top_diff)

                brightness_ratio = np.average(bright_nonwhite_loc)

                contrast = 0
                underlight = 0
                if brightness_ratio > 0.005:
                    if center_diff > 0.1: # if center is significantly brighter than the surroundings
                        contrast = center_diff
                    elif top_bottom_diff > 0.1: # if upper is significantly brighter than lower
                        contrast = top_bottom_diff
                    elif bottom_top_diff > 0.1:
                        contrast = bottom_top_diff
                    else:
                        contrast = max(center_diff, top_bottom_diff, bottom_top_diff)

                    if bottom_top2_diff > 0.1: # if lower is brighter than upper
                        underlight = bottom_top2_diff

                return np.average(np_img), brightness_ratio, underlight, contrast

            self.average_pixel, self.brightness_value, self.underlighting, self.contrast_comp = intensity_count(self.image_object)
            parameters.log.debug(self.path, self.underlighting, self.contrast_comp)
        return self.brightness_value

    def get_filename(self):
        if not self.image_name:
            self.image_name = os.path.basename(self.path)
        return self.image_name

    def get_gradient(self):
        #parameters.log.debug("run")

        if not self.gradient:
            def likly_gradient(img_object):

                np_img = np.array(img_object.convert('RGB'))

                min_channel = np.min(np_img, axis=-1)
                max_channel = np.max(np_img, axis=-1)
                diff_channel = max_channel - min_channel

                # check for monocolor:
                colored_avg = np.average(diff_channel > 10)
                if colored_avg < 0.01: # if less than 1% of the img has non-gray color
                    return 0

                # adapted skin color detection to numpy from here:
                # https://github.com/WillBrennan/SkinDetector/blob/master/skin_detector/skin_detector.py

                def get_rgb_mask(rgb_img, diff_chan):
                    lower_thresh = np.array([0, 50, 0], dtype=np.uint8)
                    upper_thresh = np.array([255, 230, 220], dtype=np.uint8)

                    # idk if the 255 multiplier is necessary
                    #mask_a = 255 * np.all(np.logical_and(rgb_img > lower_thresh, rgb_img < upper_thresh), axis=-1)
                    #parameters.log.debug(mask_a[0, 0])

                    # idk where they got the 20 and 255 from, no info regarding experiments or numerical calculations for them
                    #mask_b = 255 * ((rgb_img[:, :, 2] - rgb_img[:, :, 1]) / 20)
                    #mask_c = 255 * (diff_chan / 20)
                    #mask_d = np.bitwise_and(np.uint64(mask_a), np.uint64(mask_b))
                    #mask_rgb = np.bitwise_and(np.uint64(mask_c), np.uint64(mask_d))

                    #mask_rgb[mask_rgb < 128] = 0
                    #mask_rgb[mask_rgb >= 128] = 1

                    r_g_dominant = rgb_img[:, :, 0] > rgb_img[:, :, 1]

                    mask_rgb = np.all(np.logical_and(rgb_img > lower_thresh, rgb_img < upper_thresh), axis=-1)

                    mask_rgb = np.logical_and(r_g_dominant, mask_rgb)
                    mask_rgb = np.logical_and(diff_chan, mask_rgb)
                    parameters.log.debug("RBG", mask_rgb[70])
                    return mask_rgb.astype(float)


                def get_hsv_mask(hsv_img):
                    parameters.log.debug("HSV", hsv_img)
                    lower_thresh = np.array([45, 52, 108], dtype=np.uint8)
                    upper_thresh = np.array([255, 255, 255], dtype=np.uint8)
                    mask_hsv = np.all(np.logical_and(hsv_img > lower_thresh, hsv_img < upper_thresh), axis=-1)
                    parameters.log.debug("HSV", mask_hsv[70])
                    return mask_hsv.astype(float)

                def get_ycrcb_mask(ycrcb_img):
                    parameters.log.debug("YCBR",ycrcb_img)
                    lower_thresh = np.array([90, 100, 130], dtype=np.uint8)
                    upper_thresh = np.array([230, 120, 180], dtype=np.uint8)
                    mask_ycrcb = np.all(np.logical_and(ycrcb_img > lower_thresh, ycrcb_img < upper_thresh), axis=-1)
                    parameters.log.debug("YCBR", mask_ycrcb[70])
                    return mask_ycrcb.astype(float)

                mask_hsv = get_hsv_mask(np.array(img_object.convert('HSV')))
                mask_rgb = get_rgb_mask(np_img, diff_channel)
                mask_ycrcb = get_ycrcb_mask(np.array(img_object.convert('YCbCr')))

                n_masks = 3.0
                mask = (mask_hsv + mask_rgb + mask_ycrcb) / n_masks
                parameters.log.debug(mask)
                thresh=0.5
                mask[mask < thresh] = 0
                mask[mask >= thresh] = 1
                mask = mask.astype(int)


                mask = mask[:, np.newaxis]

                parameters.log.debug("Avg mask", mask.shape)
                parameters.log.debug("Img", np_img.shape)
                masked_values = np_img
                masked_values[mask] = [0, 0, 0]
                """
                from PIL import Image
                #parameters.log.info("masked val", masked_values.shape, masked_values)
                from matplotlib import pyplot as plt
                img = Image.fromarray(masked_values, 'RGB')
                img.show()
                x = input("next")
                """
                return np.average(mask)


            def fake_gradient(img_object):
                np_img = np.array(img_object.convert('RGB'))
                H, W, _ = np_img.shape
                min_channel = np.min(np_img, axis=-1)
                max_channel = np.max(np_img, axis=-1)
                diff_channel = max_channel - min_channel

                # check for monocolor:
                colored_avg = np.average(diff_channel > 10)
                if colored_avg < 0.01: # if less than 1% of the img has non-gray color
                    return 0
                flat_image = np_img.reshape(-1, 3)
                colors, counts = np.unique(flat_image, return_counts = True, axis = 0)
                sorted_count = sorted(counts, reverse=True)
                max_color = 50
                curr_sum = 0
                # returns the number of colors needed to describe 80% of the img
                percent_ratio = 0.8
                HW = H*W
                parameters.log.debug(counts)
                for i, c in enumerate(sorted_count):
                    curr_sum +=c
                    if curr_sum/(HW) > percent_ratio:
                        return i
                    if c < 3 and i < max_color:
                        return max_color
                    elif c < 3 and i > max_color:
                        return i

                return i


            self.gradient = fake_gradient(self.image_object)
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

    def get_search_tags(self) -> set[str]:
        manual_source = "source_manual" if self.manual_tags else []
        group_names = ["group_" + x.group_name for x in self.groups] if self.groups else []
        full_tags = self.full_tags + ["source_"+ x for x in self.external_tags.names()] + ["source_"+ x for x in self.auto_tags.names()] + manual_source + group_names
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
        for simple_key in simple_keys:
            if getattr(self, simple_key) != getattr(other, simple_key):
                result[simple_key] = getattr(self, simple_key)

        for tl_key in tags_lists_keys:
            if getattr(self, tl_key) != getattr(other, tl_key):
                result[tl_key] = getattr(self, tl_key)

        for tl_key in ["manual_tags", "rejected_manual_tags", "secondary_rejected_tags", "secondary_new_tags"]:
            if getattr(self, tl_key) != getattr(other, tl_key):
                result[tl_key] = getattr(self, tl_key)

        for tag_key in tag_keys:
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

        for simple_key in simple_keys:
            if simple_key in changes_keys:
                setattr(self, simple_key, changes[simple_key])

        for tl_key in tags_lists_keys:
            if tl_key in changes_keys:
                getattr(self, tl_key).overwrite(changes[tl_key])

        for tl_key in tags_list_keys:
            if tl_key in changes_keys:
                setattr(self, tl_key, TagsList(tags=changes[tl_key], name=tl_key))

        for tag_key in tag_keys:
            if tag_key in changes_keys:
                setattr(self, tag_key, TagElement(changes[tag_key]))

        for sentence_key in sentence_keys:
            if sentence_key in changes_keys:
                setattr(self, sentence_key, SentenceElement(changes[sentence_key]))

        # difference with the equals function
        if "groups" in changes_keys:
            self.groups = changes["groups"]

        if "rects" in changes_keys:
            self.rects = changes["rects"]

        filter_conditions = ["auto_tags", "external_tags", "manual_tags", "rejected_manual_tags", "secondary_rejected_tags", "secondary_new_tags"]
        if any([condition in changes_keys for condition in filter_conditions]):
            self.filter()

    def tooltip(self, tag: TagElement) -> str:
        tooltip_text = f"Tag: {tag}"

        if tag in tag_categories.TAG_DEFINITION.keys():
            tooltip_text += f"\nDefinition:  {tag_categories.TAG_DEFINITION[tag]}"

        external_tags_origin = self.get_external_tag_origin(tag)
        if external_tags_origin:
            tooltip_text += f"\nOrigin: {', '.join(external_tags_origin)} - external tags"
        auto_tags_origin = self.get_auto_tag_origin(tag)


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

    def uncommon_tags_tooltip(self, tag: str) -> str:
        tooltip_text = f"Tag: {tag}"

        if tag in self.uncommon_tags:
            tooltip_text += f"\nOccurrence: {round((self.uncommon_tags[tag] * 100), 2)} % of the selected images"
        if tag in tag_categories.TAG_DEFINITION.keys():
            tooltip_text += f"\nDefinition:  {tag_categories.TAG_DEFINITION[tag]}"

        return tooltip_text

def percentile_to_label(percentile):
    mapping = tag_categories.QUALITY_LABELS_MAPPING
    for label, threshold in sorted(mapping.items(), key=lambda x: (-x[1], x[0])):
        if percentile >= threshold:
            return label
    return "WORST"
