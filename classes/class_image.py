import os.path
from os.path import exists, join, splitext, split
import numpy as np
import resources.tag_categories
from PIL import Image, ImageQt
from operator import itemgetter
from clip import tokenize
from collections import Counter
import math
from resources import parameters, tag_categories

# ["3d", "anime coloring", "comic", "illustration", "not_painting"]
kept_classify_tags = ["3d", "anime coloring","comic"]

class ImageDatabase:
    def __init__(self, image_dict=None, fast_load=False):
        # Identification
        self.md5: str= ""
        self.original_md5: str = "" #md5 of the image before any editing or anything, you should always create your database before editing images (if you want tags from boorus or other websites)
        self.path: str = ""

        # Auto Tags
        self.auto_tags: dict[str: list[tuple[str, float]]] = {} # example: {"caformer": [("tag1", 0.5), ("tag2", 0.6)]}
        # tags coming from websites or txt files
        self.external_tags: dict[str: list[str]] = {}
        self.external_tags_list: list[str] = []

        # Simple Auto Tags
        self.simple_auto_tags: dict[str: list[str]] = {} # example: {"caformer": {"tag1", "tag2"}}
        self.simple_auto_tags_list: list[str] = []
        self.update_simple_auto_tags()

        # Manual Tags
        self.manual_tags: list[str] = []
        self.rejected_manual_tags: list[str] = []

        # Filtered tags
        self.filtered_new_tags: list[str] = []
        self.filtered_rejected_tags: list[str] = []
        self.filtered_review: dict[str: list[str]] = {} # sub category {set of conflicting tags}
        self.resolved_conflicts: list[str] = []

        # Other Tags
        self.sentence_description: str = ""
        self.rejected_tags: set[str] = set() # a lot of inclusion checks on rejected tags and full tags => sets
        self.full_tags: set[str] = set()
        self.full_tags_token_length: int = 0
        self.sentence_token_length: int = 0

        # Secondary Cleaning
        self.secondary_rejected_tags: list[str] = []
        self.secondary_new_tags: list[str] = []

        # States
        self.manually_reviewed: bool = False

        # Score, Classification, and Media
        self.score_label: str = ""
        self.score_value: float = 0
        self.classify_label: str = ""
        self.classify_value: float = 0

        # Groups
        self.group_names: list[str] = []

        # Temporary Data
        self.image_object = None
        self.image_ratio = None
        self.image_width = None
        self.image_height = None
        self.similarity_group: int = 0
        self.image_name = None
        self.auto_tags_merged_confidence: dict[str: float] = {}
        self.rare_tags_count = 0
        
        # todo: make similarity group into a tuple of the group then the average belong to the group
        
        # pixel related, one time calc done together
        self.brightness_value = None
        self.average_pixel = None
        self.contrast_comp = None
        self.underlighting = None
        self.gradient = None

        if image_dict is not None:
            self.init_image_dict(image_dict, fast_load)

    def update_simple_auto_tags(self):
        """
        create the auto tags without the tuple
        """
        self.simple_auto_tags_list = []
        self.external_tags_list = []
        self.simple_auto_tags = {}
        for key in self.auto_tags.keys():
            self.simple_auto_tags[key] = [x[0] for x in self.auto_tags[key]]
        for key in self.simple_auto_tags.keys():
            self.simple_auto_tags_list += self.simple_auto_tags[key]
        for key in self.external_tags.keys():
            if "rejected" not in key:
                self.external_tags_list += self.external_tags[key]
        #for key in self.external_tags.keys():
        #    self.external_tags_list += self.external_tags[key]
        self.simple_auto_tags_list = list(set(self.simple_auto_tags_list))
        self.external_tags_list = list(set(self.external_tags_list))

    def update_full_tags(self):
        # update rejected
        self.get_rejected_tags()

        #manual + from txt + auto tags + filtered tags +secondary tags
        nontagger_vals = []
        if self.classify_label in kept_classify_tags and self.classify_value > 0.7:
            nontagger_vals.append(self.classify_label)
        self.full_tags = set(
            nontagger_vals + self.manual_tags +
            self.external_tags_list + self.simple_auto_tags_list + self.filtered_new_tags)
        
        self.full_tags = set([t for t in self.full_tags if t not in self.rejected_tags or t in self.manual_tags])

    def get_prefiltered_full_tags(self):
        """
        return the full tag as if there was no filter
        """
        full_tags = []

        if self.classify_label in kept_classify_tags and self.classify_value > 0.7:
            full_tags.append(self.classify_label)

        #manual
        for tag in self.manual_tags:
            if tag not in full_tags:
                full_tags.append(tag)

        # external tags
        for tag in self.external_tags_list:
            if tag not in full_tags and tag not in self.rejected_manual_tags:
                full_tags.append(tag)

        # auto tags
        for tag in self.simple_auto_tags_list:
            if tag not in full_tags and tag not in self.rejected_manual_tags:
                full_tags.append(tag)

        return full_tags

    def init_image_dict(self, image_dict, fast_load=False):
        """
        it will work, with an image dict containing only the path, md5 or anything else
        will replace auto tags or external tags items if identical name/key
        Args:
            fast_load: set to True if you are sure all the data is present
            image_dict:
        """
        #if not fast_load:
        new_keys = image_dict.keys()
        update_simple_tags = False
        if "md5" in new_keys:
            self.md5 = image_dict["md5"]
        if "original_md5" in new_keys:
            self.original_md5 = image_dict["original_md5"]
        elif "original_md5" not in new_keys and not self.original_md5 and "md5" in new_keys:
            self.original_md5 = self.md5
        if "path" in new_keys:
            self.path = image_dict["path"]
        # Auto Tags
        if "auto_tags" in new_keys:
            if isinstance(image_dict["auto_tags"], dict):
                for key, value in image_dict["auto_tags"].items():
                    self.add_auto_tags_key(key, value)
                update_simple_tags = True

        # legacy code convert for database old auto tags storage
        if "caformer_auto_tags" in new_keys:
            self.auto_tags["Caformer"] = image_dict["caformer_auto_tags"]
            update_simple_tags = True
        if "swinv2_auto_tags" in new_keys:
            self.auto_tags["Swinv2v3"] = image_dict["swinv2_auto_tags"]
            update_simple_tags = True

        # Manual Tags
        if "manual_tags" in new_keys:
            self.manual_tags = image_dict["manual_tags"]
        if "rejected_manual_tags" in new_keys:
            self.rejected_manual_tags = image_dict["rejected_manual_tags"]

        # Filtered tags
        if "filtered_new_tags" in new_keys:
            self.filtered_new_tags = image_dict["filtered_new_tags"]
        if "filtered_rejected_tags" in new_keys:
            self.filtered_rejected_tags = image_dict["filtered_rejected_tags"]
        if "resolved_conflicts" in new_keys:
            self.resolved_conflicts = image_dict["resolved_conflicts"]

        # Secondary Cleaning
        if "secondary_rejected_tags" in new_keys:
            self.secondary_rejected_tags = image_dict["secondary_rejected_tags"]
        if "secondary_new_tags" in new_keys:
            self.secondary_new_tags = image_dict["secondary_new_tags"]

        # Other Tags
        if "external_tags" in new_keys:
            if isinstance(image_dict["external_tags"], dict):
                for key, value in image_dict["external_tags"].items():
                    self.add_external_tags_key(key, value)
                update_simple_tags = True
        if "from_txt_tags" in new_keys:
            if image_dict["from_txt_tags"]:
                self.external_tags["legacy_from_txt"] = {"tags": image_dict["from_txt_tags"]}
                update_simple_tags = True
        if "sentence_description" in new_keys:
            self.sentence_description = image_dict["sentence_description"]
        self.rejected_tags = self.get_rejected_tags()
        if update_simple_tags:
            self.update_simple_auto_tags()

        # no need to get the full tags
        self.update_full_tags()

        # States
        if "manually_reviewed" in new_keys:
            self.manually_reviewed = image_dict["manually_reviewed"]
        # Scores, Classification, and Media
        if "score_label" in new_keys:
            self.score_label = image_dict["score_label"]
        if "score_value" in new_keys:
            self.score_value = image_dict["score_value"]
        if "classify_label" in new_keys:
            self.classify_label = image_dict["classify_label"]
        if "classify_value" in new_keys:
            self.classify_value = image_dict["classify_value"]

    def add_auto_tags_key(self, name, auto_tags_list_tuples):
        self.auto_tags[name] = auto_tags_list_tuples

    def add_external_tags_key(self, name, external_tags_list):
        self.external_tags[name] = external_tags_list

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
        if self.auto_tags and isinstance(self.auto_tags, dict):
            result["auto_tags"] = self.auto_tags
        else:
            error = True
        if self.external_tags and isinstance(self.external_tags, dict):
            result["external_tags"] = self.external_tags
        else:
            error = True
        if self.manual_tags and isinstance(self.manual_tags, list):
            result["manual_tags"] = self.manual_tags
        else:
            error = True
        if self.rejected_manual_tags and isinstance(self.rejected_manual_tags, list):
            result["rejected_manual_tags"] = self.rejected_manual_tags
        else:
            error = True
        if self.sentence_description and isinstance(self.sentence_description, str):
            result["sentence_description"] = self.sentence_description
        else:
            error = True
        if isinstance(self.manually_reviewed, bool):
            result["manually_reviewed"] = self.manually_reviewed
        else:
            error = True
        if self.filtered_new_tags and isinstance(self.filtered_new_tags, list):
            result["filtered_new_tags"] = self.filtered_new_tags
        else:
            error = True
        if self.filtered_rejected_tags and isinstance(self.filtered_rejected_tags, list):
            result["filtered_rejected_tags"] = self.filtered_rejected_tags
        else:
            error = True
        if self.resolved_conflicts and isinstance(self.resolved_conflicts, list):
            result["resolved_conflicts"] = self.resolved_conflicts
        else:
            error = True
        if self.secondary_new_tags and isinstance(self.secondary_new_tags, list):
            result["secondary_new_tags"] = self.secondary_new_tags
        else:
            error = True
        if self.secondary_rejected_tags and isinstance(self.secondary_rejected_tags, list):
            result["secondary_rejected_tags"] = self.secondary_rejected_tags
        else:
            error = True
        if self.score_label and isinstance(self.score_label, str):
            result["score_label"] = self.score_label
        else:
            error = True
        if self.score_value and isinstance(self.score_value, float):
            result["score_value"] = self.score_value
        else:
            error = True
        if self.classify_label and isinstance(self.classify_label, str):
            result["classify_label"] = self.classify_label
        else:
            error = True
        if self.classify_value and isinstance(self.classify_value, float):
            result["classify_value"] = self.classify_value
        else:
            error = True
        # todo: return error
        return result

    def create_txt_file(self, add_backslash_before_parenthesis=False, keep_tokens_separator: str="|||",  main_tags: list[str]=[], secondary_tags: list[str]=[], use_aesthetic_score=False, score_trigger=True, use_sentence=False, sentence_in_trigger=False, remove_tags_in_sentence=True):
        """
        create the txt files, need a keep token separator option
        currently the trigger tags are removed if they are in a sentence
        """
        self.update_full_tags()
        tags = list(self.full_tags)
        np.random.shuffle(tags)

        if use_aesthetic_score and not score_trigger:
            tags.append(self.score_label)

        if use_sentence and remove_tags_in_sentence and self.sentence_description:
            k=0
            while k < len(tags):
                if tags[k] in self.sentence_description:
                    tags.pop(k)
                else:
                    k+=1

        if add_backslash_before_parenthesis:
            tags = [tag.replace('(', '\\(').replace(')', '\\)') for tag in tags]

        kept_tags = []
        if main_tags or secondary_tags:
            primary_kept_tags = []
            secondary_kept_tags = []

            for main_tag in main_tags:
                if "*" in main_tag:
                    striped_main_tag = main_tag.replace("*","")
                    indexes_to_remove = []

                    for k in range(len(tags)):
                        if striped_main_tag in tags[k]:
                            primary_kept_tags.append(tags[k])
                            indexes_to_remove.append(k)
                    indexes_to_remove.sort()

                    # remove the found tags from the sequence
                    while len(indexes_to_remove)>0:
                        pop_index = len(indexes_to_remove)-1
                        del tags[indexes_to_remove[pop_index]]
                        del indexes_to_remove[pop_index]
                else:
                    if main_tag in tags:
                        primary_kept_tags.append(main_tag)
                        tags.remove(main_tag)

            for secondary_tag in secondary_tags:
                if "*" in secondary_tag:
                    striped_main_tag = secondary_tag.replace("*", "")
                    indexes_to_remove = []

                    for k in range(len(tags)):
                        if striped_main_tag in tags[k]:
                            secondary_kept_tags.append(tags[k])
                            indexes_to_remove.append(k)
                    indexes_to_remove.sort()

                    # remove the found tags from the sequence
                    while len(indexes_to_remove) > 0:
                        pop_index = len(indexes_to_remove) - 1
                        del tags[indexes_to_remove[pop_index]]
                        del indexes_to_remove[pop_index]
                else:
                    if secondary_tag in tags:
                        secondary_kept_tags.append(secondary_tag)
                        tags.remove(secondary_tag)

            if len(secondary_kept_tags)>1:
                np.random.shuffle(secondary_kept_tags)

            kept_tags = primary_kept_tags+secondary_kept_tags

        if sentence_in_trigger and self.sentence_description:
            kept_tags.append(self.sentence_description)
        elif self.sentence_description:
            tags.append(self.sentence_description)

        if use_aesthetic_score and score_trigger:
            kept_tags.insert(0, self.score_label)

        if keep_tokens_separator and kept_tags:
            kept_tags.append(keep_tokens_separator)

        if kept_tags:
            return ', '.join(kept_tags+tags)
        else:
            return ', '.join(tags)

    def append_resolved_conflict(self, sub_category):
        if sub_category not in self.resolved_conflicts:
            self.resolved_conflicts.append(sub_category)

    def append_manual_tags(self, tags: list[str]):
        self.manual_tags.extend([tag for tag in tags if tag not in self.manual_tags and tag != ""])

    def remove_manual_tags(self, tags: list[str]):
        self.manual_tags = [tag for tag in self.manual_tags if tag not in tags]

    def remove_rejected_manual_tags(self, tags: list[str]):
        self.rejected_manual_tags = [tag for tag in self.rejected_manual_tags if tag not in tags]

    def append_rejected_manual_tags(self, tags: list[str]):
        self.rejected_manual_tags.extend([tag for tag in tags if tag not in self.rejected_manual_tags])

    def append_secondary_tags(self, tags: list[str]):
        self.secondary_new_tags.extend([tag for tag in tags if tag not in self.secondary_new_tags])

    def append_secondary_rejected(self, tags: list[str]):
        self.secondary_rejected_tags.extend([tag for tag in tags if tag not in self.secondary_rejected_tags])

    def filter(self):
        self.filtered_new_tags = []
        self.filtered_rejected_tags = []
        self.filtered_review = {}
        full_tags = self.get_prefiltered_full_tags()

        # add HIGH tags if we find associated tags from TAG and LOW:
        filtered_tags = [x for x in full_tags if x in resources.tag_categories.TAG2HIGH_KEYSET]
        
        # Always rejected tags
        rejected = [x for x in self.simple_auto_tags_list+self.external_tags_list if x in resources.tag_categories.REJECTED_TAGS]
        full_tags = [x for x in full_tags if x not in rejected]

        new_tags = [t for x in filtered_tags for t in resources.tag_categories.TAG2HIGH[x] if t not in resources.tag_categories.REJECTED_TAGS]
        full_tags.extend(new_tags)

        rejected_remove_series = []
        if parameters.PARAMETERS["filter_remove_series"]:
           rejected_remove_series = [x for x in full_tags if x in resources.tag_categories.SERIES_TAGS]

        rejected_remove_metadata = []
        if parameters.PARAMETERS["filter_remove_metadata"]:
           rejected_remove_metadata = [x for x in full_tags if x in resources.tag_categories.METADATA_TAGS]

        rejected_remove_characters = []
        if parameters.PARAMETERS["filter_remove_characters"]:
           rejected_remove_characters = [x for x in full_tags if x in resources.tag_categories.CHARACTERS_TAG]


        #filter out tags in low if another tag in TAGS is in the full_tags
        filtered_tags = [low for low in full_tags if low in resources.tag_categories.LOW2TAGS_KEYSET]
        rejected.extend([low for low in filtered_tags if any(x in full_tags for x in resources.tag_categories.LOW2TAGS[low])])
        rejected.extend(rejected_remove_series)
        rejected.extend(rejected_remove_metadata)
        rejected.extend(rejected_remove_characters)

        # removing duplicates and adding to self
        self.filtered_new_tags = list(set(new_tags))
        self.filtered_rejected_tags = list(set(rejected))
        # by this stage we're done with programmatically fixing/filtering tags

        # update the unresolved
        self.update_review_tags()
        self.update_full_tags()

    def filter_sentence(self):
        """
        Not yet implemented, will replace words from the caption/sentence to other things that are decided somewhere else
        Returns:

        """
        return

    def refresh_unsafe_tags(self, all_accepted_tags):
        external_keys = list(self.external_tags.keys())
        for key in external_keys:
            new_accepted = []
            if "rejected" in key:
                for tag in self.external_tags[key]:
                    if tag in all_accepted_tags:
                        new_accepted.append(tag)
                self.add_external_tags_key(key[len("rejected")+1:], new_accepted)

        
    def update_review_tags(self):
        # here we lay out the conflicts:
        # here we will only use the dict made with exclusive categories
        self.filtered_review={}
        self.update_full_tags()
        full_tag_set = set(self.full_tags)
        resolved = self.resolved_conflicts
        # check for multiple overlaps per category and append if we find any
        for tag_category, tag_set in resources.tag_categories.TAG_CATEGORIES_EXCLUSIVE.items():
            # basically get (all tags within a category in full) - rejected
            intersect = full_tag_set.intersection(tag_set) # .difference(set(self.get_rejected_tags()))
            if len(intersect) > 1 and tag_category not in resolved:
                self.filtered_review[tag_category] = list(intersect)

    def get_image_object(self, max_size: tuple[int, int]=None):
        """
        return a Qt image object, a thumbnail of the given size
        Args:
            max_size:

        Returns:

        """
        if not self.image_object:
            self.load_image_object(max_size)
        return ImageQt.ImageQt(self.image_object)

    def load_image_object(self, max_size: tuple[int, int]=None):
        if self.image_object is None:
            self.image_object = Image.open(self.path)
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

    def update_token_length(self):
        self.full_tags_token_length = len(tokenize(", ".join(self.full_tags), context_length=500, truncate=True).nonzero()) - 2

    def update_sentence_token_length(self):
        if self.sentence_description:
            self.sentence_token_length = len(tokenize(self.sentence_description, context_length=500, truncate=True).nonzero()) - 2
        else:
            self.sentence_token_length = 0

    def get_sentence_token_length(self):
        self.update_sentence_token_length()
        return self.sentence_token_length

    def get_token_length(self):
        self.update_token_length()
        return self.full_tags_token_length

    def get_qt_thumbnail(self):
        return ImageQt.ImageQt(self.image_object)

    def get_rejected_tags(self):
        """
        recalculate the full rejected tags, and both update it and return it
        Returns:
        """
        self.rejected_tags = set(self.rejected_manual_tags + self.filtered_rejected_tags + self.secondary_rejected_tags)
        return self.rejected_tags

    def get_full_tags(self):
        """
        recalculate the full rejected tags, and both update it and return it
        Returns:

        """
        self.update_full_tags()
        return self.full_tags
    
    def get_full_tags_over_confidence(self, confidence = 0.7):
        """
        recalculate and update the full rejected tags, return a copy minus the autotags under confidence
        Returns:

        """
        self.update_full_tags()
        
        # build merged confidence if it wasn't made
        if not self.auto_tags_merged_confidence: 
            for _, tags in self.auto_tags.items():
                for (tag, confidence) in tags:
                    if tag not in self.auto_tags_merged_confidence:
                        self.auto_tags_merged_confidence[tag] = confidence
                    else: # take the higher confidence
                        if self.auto_tags_merged_confidence[tag] < confidence:
                            self.auto_tags_merged_confidence[tag] = confidence        
                
        autotag_below_thresh = [k for k, v in self.auto_tags_merged_confidence.items() if v < confidence and k not in  self.manual_tags]
        tags = [t for t in self.full_tags if t not in autotag_below_thresh]
        return tags
        

    def get_unresolved_conflicts(self):
        """
        return the filter conflicts minus resolved conflicts
        Returns: dict

        """
        return {k:v for k, v in self.filtered_review.items() if k not in self.resolved_conflicts}
        
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
        self.sentence_description = text.strip()

    def get_recommendations(self):
        """
        return the recommendations, and calculates it each time (assumes the full tags are calculated beforehand)
        Returns:
            recommendations: a list of recommended tags
        """
        recommendations = []
        for recommended_tag, triggers in tag_categories.TAGS_RECOMMENDATIONS.items():
            for x in range(len(triggers)):
                if recommended_tag not in recommendations and recommended_tag not in self.full_tags and all([y in self.full_tags for y in triggers[x] if y[0] != "-" or len(y)<4]) and all([y[1:] not in self.full_tags for y in triggers[x] if y[0] == "-" and len(y)>3]):
                    recommendations.append(recommended_tag)
        return recommendations

    def get_character_conflicts_len(self) -> int:
        """
        return the number of characters in an image tags that appear in the conflicts
        """
        x = 0
        if "KNOWN CHARACTERS 1" in self.filtered_review.keys():
            x += len(self.filtered_review["KNOWN CHARACTERS 1"])
        if "KNOWN CHARACTERS 2" in self.filtered_review.keys():
            x += len(self.filtered_review["KNOWN CHARACTERS 2"])
        return x
    
    def get_character_count(self) -> int:
        """
        return the number of characters in an image tags
        """
        x = 0
        for tag in self.full_tags:
            if tag in tag_categories.CHARACTERS_TAG.keys():
                x+=1
        return x

    def auto_tag_confidence(self, tag: str, *, tagger_name="") -> float:
        if tag in self.simple_auto_tags_list:
            for name in self.auto_tags.keys():
                if not tagger_name or name == tagger_name:
                    for tag_tuple in self.auto_tags[name]:
                        if tag_tuple[0] == tag:
                            return tag_tuple[1]
        return 0.0

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

    def round_and_crop_to_bucket(self, x:float, reso_step=64) -> int:
        x = int(x+0.5) # round to nearest int
        return x - x%reso_step # crop to nearest multiple of reso_step
        
    
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
        max_area = base_height * base_width
        if self.image_width* self.image_height > max_area: # we need to rescale the image down
            # explanation of the sqrt in kohya's code:
            # (w, h) is the image resolution, s is the scale factor needed to resize the image
            # (w_res, h_res) is the resolution used for the max area
            # max_area = w_res * h_res and AR (aspect ratio) = w/h
            # the max area is also equal to s*w * s*h, because the rescaled image needs to fit in the max area
            # the goal is to find either s*w or s*h, which is one of the rescaled sizes 
            # so we do s*w = sqrt(max_area * AR) = sqrt(s*w * s*h * w/h) = sqrt(s^2 * w^2)
            
            resized_width = math.sqrt(max_area * self.image_ratio)
            resized_height = max_area / resized_width
            assert abs(resized_width / resized_height - self.image_ratio) < 1e-2, "aspect is illegal"
        
            # at this point, resized_width and height are floats and we need to get the closest int value
            
            # bucket resolution by clipping based on width
            b_width_rounded = self.round_and_crop_to_bucket(resized_width)
            b_height_in_wr = self.round_and_crop_to_bucket(b_width_rounded / self.image_ratio)
            ar_width_rounded = b_width_rounded / b_height_in_wr
            
            # bucket resolution by clipping based on height
            b_height_rounded = self.round_and_crop_to_bucket(resized_height)
            b_width_in_hr = self.round_and_crop_to_bucket(b_height_rounded * self.image_ratio)
            ar_height_rounded = b_width_in_hr / b_height_rounded
            
            # check the error between the aspect ratio and choose the one that's smallest
            # most times the resulting bucket size would be the same
            if abs(ar_width_rounded - self.image_ratio) < abs(ar_height_rounded - self.image_ratio):
                resized_size = (b_width_rounded, int(b_width_rounded / self.image_ratio + 0.5))
            else:
                resized_size = (int(b_height_rounded * self.image_ratio + 0.5), b_height_rounded)
            
        else:
            resized_size = (self.image_width, self.image_height)
        
        # remove any outer pixels from the bottom and right of the image that doesn't match the bucket steps (usualy 64)
        bucket_width = resized_size[0] - resized_size[0] % bucket_steps
        bucket_height = resized_size[1] - resized_size[1] % bucket_steps
        
        bucketed_resolution = (bucket_width, bucket_height)
        
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
                    if center_diff > 0.1: # if center is significatly brighter than the surroundings
                        contrast = center_diff
                    elif top_bottom_diff > 0.1: # if upper is significatly brighter than lower
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
        if self.score_label in tag_categories.QUALITY_LABELS:
            to_return = tag_categories.QUALITY_LABELS.index(self.score_label) + 1
        return to_return, self.score_value

    def get_unknown_tags_count(self) -> int:
        key_dict = tag_categories.COLOR_DICT.keys()
        return len([tag for tag in self.full_tags if tag not in key_dict])

    def get_external_tag_origin(self, tag) -> list[str]:
        result = []
        for name in self.external_tags.keys():
            if "rejected" not in name and tag in self.external_tags[name]:
                result.append(name)
        return result

    def get_auto_tag_origin(self, tag) -> list[str]:
        result = []
        for name in self.simple_auto_tags.keys():
            if "rejected" not in name and tag in self.simple_auto_tags[name]:
                result.append(name)
        return result

    def get_search_tags(self) -> set[str]:
        manual_source = {"source_manual"} if len(self.manual_tags) else {}
        group_names = {"group_"+x for x in self.group_names} if self.group_names else {}
        full_tags = self.get_full_tags().union({"source_"+x for x in self.external_tags.keys()}, {"source_"+x for x in self.auto_tags.keys()}, manual_source, group_names)
        return full_tags

    def cleanup_rejected_manual_tags(self):
        k = 0
        while k < len(self.rejected_manual_tags):
            if self.rejected_manual_tags[k] not in self.manual_tags+self.external_tags_list+self.simple_auto_tags_list+self.secondary_new_tags:
                self.rejected_manual_tags.pop(k)
            else:
                k+=1

    def get_rare_tags_count(self):
        return self.rare_tags_count

          
def percentile_to_label(percentile):
    mapping = tag_categories.QUALITY_LABELS_MAPPING
    for label, threshold in sorted(mapping.items(), key=lambda x: (-x[1], x[0])):
        if percentile >= threshold:
            return label
    return "WORST"
