from __future__ import annotations
# annotation used for type hinting and self forward referencing

from resources import parameters

import re
from collections import defaultdict

import cloudscraper
import numpy as np

from resources import tag_categories, wiki_info
from clip import tokenize

from tools.images import overlapping_area, overlapping_area_ratio

curr_wiki_info = wiki_info.load_wiki_info()
def load_wiki_info():
    global curr_wiki_info
    parameters.log.info("Reloading wiki info")
    curr_wiki_info = wiki_info.load_wiki_info()


# todo : add correct error codes to raise default error codes:
# https://docs.python.org/3/library/exceptions.html#exception-hierarchy

class RectElement:
    def __init__(self, name="rect", top=0, left=0, width=0, height=0, confidence=1, color=""):
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        # this is 1 for manual entries, this is adjusted for detection model results
        self.confidence = confidence
        self.name = name

        # Tags Values
        self.sentence_description: SentenceElement = SentenceElement()
        self.auto_tags: TagsLists = TagsLists(name="auto_tags")
        self.manual_tags: TagsList = TagsList(name="manual_tags")
        self.rejected_manual_tags: TagsList = TagsList(name="rejected_manual_tags")

        # Virtuals/Not Saved
        self.rejected_tags: TagsList = TagsList(name="rejected_tags")
        self.filtered_new_tags: TagsList = TagsList(name="filtered_new_tags")
        self.filtered_rejected_tags: TagsList = TagsList(name="filtered_rejected_tags")
        self.full_tags: TagsList = TagsList(name="full_tags")

        # Future values:
        self.color: str = color #Hexadecimal color value of the rect

    def __copy__(self):
        return self.get_copy()

    def apply_from_dict(self, save_dict):
        """
        loads data fromsave dict, this also return a reference to self
        """
        saved_keys = save_dict.keys()
        apply_filter = False
        if "name" in saved_keys:
            self.name = save_dict["name"]
        if "color" in saved_keys:
            self.color = save_dict["color"]
        if "coordinates" in saved_keys:
            (self.top, self.left, self.width, self.height) = save_dict["coordinates"]
        if "confidence" in saved_keys:
            self.confidence = save_dict["confidence"]
        if "sentence" in saved_keys:
            self.sentence_description.sentence = save_dict["sentence"]
        if "auto_tags" in saved_keys:
            self.auto_tags.overwrite(save_dict["auto_tags"])
            apply_filter = True
        if "manual_tags" in saved_keys:
            self.manual_tags = TagsList(tags=save_dict["manual_tags"], name="manual_tags")
            apply_filter = True
        if "rejected_manual_tags" in saved_keys:
            self.rejected_manual_tags = TagsList(tags=save_dict["rejected_manual_tags"], name="rejected_manual_tags")
            apply_filter = True
        if apply_filter:
            self.filter()
        return self

    def apply_coordinates(self, top: int, left: int, width: int, height: int):
        """
        Overwrite the coordinates of the Rectangle Element to the name required
        Args:
            top:
            left:
            width:
            height:
        """
        self.top = top
        self.left = left
        self.width = width
        self.height = height

    def update_confidence(self, new_confidence):
        self.confidence = new_confidence
 
    def save(self):
        result = {
            "name": self.name,
            "coordinates": (self.top, self.left, self.width, self.height),
            "confidence": self.confidence
        }
        if self.sentence_description:
            result["sentence"] = self.sentence_description.save()
        if self.color:
            result["color"] = self.color
        if self.auto_tags:
            result["auto_tags"] = self.auto_tags.save()
        if self.manual_tags:
            result["manual_tags"] = self.manual_tags.save()
        if self.rejected_manual_tags:
            result["rejected_manual_tags"] = self.rejected_manual_tags.save()
        return result

    def add_new_tags(self, tags):
        """
        Add tags were is needed (manual tags only)
        Args:
            tags: str, list[str] or TagElement or list[TagElement]
        """
        self.manual_tags += tags
        self.rejected_manual_tags -= tags
        self.filter()

    def remove_tags(self, tags):
        """
        Remove tags were is needed (manual tags only)
        Args:
            tags: str, list[str] or TagElement or list[TagElement]
        """
        self.rejected_manual_tags += tags
        self.manual_tags -= tags
        self.filter()

    # The functions that are almost a copy/paste from ImageDatabase
    def update_full_tags(self):
        # manual + from txt + auto tags + filtered tags +secondary tags
        self.full_tags.clear()
        self.full_tags = self.full_tags + self.auto_tags + self.filtered_new_tags
        self.full_tags -= self.get_rejected_tags()
        self.full_tags += self.manual_tags

    def get_prefiltered_full_tags(self):
        """
        only used by the filter
        return the full tag as if there was no filter, except for manually rejected tags
        """
        # manual + from txt + auto tags + filtered tags +secondary tags
        full_tags = TagsList(name="full_tags")
        full_tags = full_tags + self.auto_tags - self.rejected_manual_tags + self.manual_tags
        return full_tags

    def filter(self):
        self.filtered_new_tags.clear()
        self.filtered_rejected_tags.clear()
        full_tags = self.get_prefiltered_full_tags()

        # add HIGH tags if we find associated tags from TAG and LOW:
        filtered_tags = full_tags.to_high()

        # Always rejected tags
        rejected = full_tags.hard_rejected_tags()
        full_tags -= rejected

        new_tags = filtered_tags.not_hard_rejected_tags()
        full_tags += new_tags

        # filter out tags in low if another tag in TAGS is in the full_tags
        filtered_tags = full_tags.has_low()
        rejected += filtered_tags

        # removing duplicates and adding to self
        self.filtered_new_tags += new_tags - self.rejected_manual_tags
        self.filtered_rejected_tags += rejected - self.manual_tags

        # by this stage we're done with programmatically fixing/filtering tags

        # update the unresolved
        self.update_full_tags()

    def get_rejected_tags(self):
        """
        recalculate the full rejected tags, and both update it and return it
        Returns:
        """
        self.rejected_tags.clear()
        self.rejected_tags += self.rejected_manual_tags + self.filtered_rejected_tags
        return self.rejected_tags

    def get_full_tags(self):
        """
        recalculate the full tags, and both update it and return it
        Returns:

        """
        self.update_full_tags()
        return self.full_tags
    
    def get_full_only_tags(self):
        """
        update full tags and return only the string version of tags
        """
        return [tag.tag for tag in self.get_full_tags()]

    def get_coords(self): 
        """Returns: (top, left, width, height)
        """
        return (self.top, self.left, self.width, self.height)
    
    def get_area(self):
        return self.width * self.height
    
    def get_overlapping_area(self, coords):
        # coords is the same  format as (top, left, width, height)
        # math is easier if the rectangle is defined with (minX, minY) and (MaxX, MaxY)
        return overlapping_area(self.get_coords(), coords)
    
    def get_overlapping_area_ratio(self, coords):
        # coords is the same format as (top, left, width, height)
        return overlapping_area_ratio(self.get_coords(), coords)
        
    def get_copy(self):
        r = RectElement()
        save_dict = self.save()
        r.apply_from_dict(save_dict)
        return r
    
    def create_output(self, add_backslash_before_parenthesis=False, keep_tokens_separator: str= "|||", 
                      main_tags: list[str]=[], secondary_tags: list[str]=[], use_sentence=True, shuffle_tags=True):
        result = ""
        if use_sentence:
            segments = self.sentence_description.get_output_info()
        else:
            segments = ["#full_tags"]

        for segment in self.sentence_description.get_output_info():
            if segment == "#full_tags":
                tags = self.get_full_only_tags()
                if shuffle_tags:
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
                            tags.remove(main_tag)
                            identified_main_tags.append(main_tag)
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
                            tags.remove(secondary_tag)
                            identified_secondary_tags.append(secondary_tag)

                temp_tags = []
                if identified_main_tags:
                    temp_tags += identified_main_tags
                if identified_secondary_tags:
                    if shuffle_tags:
                        np.random.shuffle(identified_secondary_tags)
                    temp_tags += identified_secondary_tags

                if len(segments) == 1 and keep_tokens_separator: #todo: improves all requirements
                    temp_tags.append(keep_tokens_separator)

                tags = temp_tags + tags
                result += ", ".join(tags)
            else: # when it's simple text
                result += segment

        if add_backslash_before_parenthesis:
            result = result.replace('(', '\\(').replace(')', '\\)')

        return result


class SentenceElement:
    def __init__(self, sentence="", sentence_splitter=","):
        if isinstance(sentence, str):
            self.sentence = sentence
        elif isinstance(sentence, SentenceElement):
            self.sentence = sentence.sentence
        self.token_length: int = 0
        self.sentence_length: int = 0
        # nor normal langauge it's a period, but for tagging purpose we use the default comma
        self.splitter = sentence_splitter

    def __bool__(self):
        return bool(self.sentence)

    def __str__(self):
        return self.sentence

    def __eq__(self, other):
        if self.sentence == other.sentence:
            return True
        return False

    def __iadd__(self, other): # handles the += operator
        splitter = " " if self.sentence.endswith(self.splitter) else self.splitter
        if isinstance(other, SentenceElement) and other.sentence:
            self.sentence+= splitter + other.sentence
        elif isinstance(other, str) and other:
            self.sentence+= splitter + other
        else:
            raise TypeError(f"Unsupported type, trying to add {type(self)} with {type(other)}")
        return self
    
    def __add__(self, other):
        new_sen = SentenceElement(sentence=self.sentence, sentence_splitter=self.splitter)
        splitter = " " if new_sen.sentence.endswith(new_sen.splitter) else new_sen.splitter
        if isinstance(other, SentenceElement) and other.sentence:
            new_sen.sentence+= splitter + other.sentence
        elif isinstance(other, str) and other:
            new_sen.sentence+= splitter + other
        return new_sen
        
    def get_token_length(self):
        if self.sentence:
            self.token_length: int = len(tokenize(self.sentence, context_length=500, truncate=True).nonzero()) - 2
        else:
            self.token_length = 0
        return self.token_length
    
    def get_sentence_length(self):
        if self.sentence:
            self.sentence_length: int = len(self.sentence)
        else:
            self.sentence_length = 0
        return self.sentence_length
            
    def save(self):
        return self.sentence

    def get_output_info(self):
        """
        Output a modified version of the sentence that permits the output of a list of items in order
        - ##FTAGS## for full_tags
        - ##SCORE## for score_label
        - ##RECT:rect_name## for the sentence of rects (will call this one again)
        Returns: list of elements or element keys
        """
        if not self.sentence:
            return ["#full_tags"]
        result = []
        temp_result = self.sentence.split("##")
        for segment in temp_result:
            if segment.strip() == "FTAGS":
                result.append("#full_tags")
            elif segment.strip() ==  "SCORE":
                result.append("#score_label")
            elif "RECT:" in segment:
                rect_name = segment.split(":", maxsplit=1)[1].strip()
                result.append(("RECT", rect_name))
            else:
                result.append(segment)

        return result


class GroupElement:
    def __init__(self, *, group_name: str="", md5s: list[str] | set[int] =[]):
        """
        stores md5s that are in this group
        """
        self.group_name: str = group_name
        # todo update to use sets?
        self.md5s: set[str] = set(md5s)

    def __len__(self):
        return len(self.md5s)
        
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.md5s[self.md5s.index(key)] or key == self.group_name
        elif isinstance(key, int):
            return self.md5s[key]

    def __setitem__(self, key, value):
        if isinstance(key, str) and key not in self.md5s:
            self.md5s.append(value)
            return
        elif isinstance(key, str):
            self.md5s[self.md5s.index(key)] = value
            return
        parameters.log.info(f"printing for checking, used to set groups: {type(key)}, {type(value)}")
        self.md5s[key] = value
    
    def __bool__(self):
        return bool(self.md5s)
    
    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.group_name
        elif isinstance(other, type(self)):
            if len(self) != len(other):
                return False
            if all(md5 in self.md5s for md5 in other.md5s):
                return True
        elif isinstance(other, list):
            if all(md5 in self.md5s for md5 in other):
                return True
        return False
    
    def __sub__(self, other): # add is not impliemented bc it's not required for now
        if isinstance(other, GroupElement):
            return self.md5s - other.md5s
        elif isinstance(other, set):
            return self.md5s - other
        elif isinstance(other, list):
            return self.md5s - set(other)
        elif isinstance(other, str):
            return self.md5s - {other}
        
    def __contain__(self, md5):
        return md5 in self.md5s

    def __iter__(self):
        return iter(self.md5s)
    
    def add_item(self, item: str | list[str] | set[str]):
        if isinstance(item, str) and item not in self.md5s:
            self.md5s.add(item)
        elif isinstance(item, list) or isinstance(item, set):
            for i in item:
                if isinstance(i, str) and i not in self.md5s:
                    self.md5s.add(i)

    def remove_item(self, item: str | list[str] | set[str]):
        if isinstance(item, str) and item in self.md5s:
            self.md5s.remove(item)
        elif isinstance(item, list) or isinstance(item, set):
            for i in item:
                if isinstance(i, str) and i not in self.md5s:
                    self.md5s.remove(i)

    def save(self):
        result = {"images": list(self.md5s)}
        return result

class TagsLists:
    """
    Exists for external_tags, auto_tags
    """
    def __init__(self, tags_list=None, *, name: str=""):
        if tags_list is None:
            tags_list = []
        self.tags_lists: list[TagsList] = tags_list
        self.name: str = name
        self.merged_tags: TagsList = TagsList(name="merged tag list")

    def __repr__(self):
        return "TagsLists("+str(self.tags_lists)+", name="+self.name+")"

    def __bool__(self):
        return any([bool(x) for x in self.tags_lists])

    def __len__(self):
        return len(self.tags_lists)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            if len(self.names()) != len(other.names()):
                return False
            if all(self[name] == other[name] for name in self.names()):
                return True
        return False

    def __getitem__(self, key):
        """

        Args:
            key: can be the name of the tags_list or the key in the list

        Returns:

        """
        if isinstance(key, int):
            return self.tags_lists[key]
        elif isinstance(key, str):
            return self.tags_lists[self.name_index(key)]
        else:
            raise KeyError("Unknown type used as index")

    def __setitem__(self, key, value):
        """
        Will apply the item, or add it if the key doesn't exist in case of a name key
        Args:
            key: can be the index in the tags_lists or the name of a TagsList
            value: can be a list or a TagsList

        Returns:

        """
        if isinstance(key, str):
            if key in self.names():
                key = self.name_index(key)
            else:
                if isinstance(value, TagsList):
                    self.tags_lists.append(value)
                elif isinstance(value, list):
                    self.tags_lists.append(TagsList(tags=value, name=key))
                return
        if isinstance(value, TagsList):
            self.tags_lists[key] = value
        elif isinstance(value, list):
            self.tags_lists[key] = TagsList(tags=value, name=self.tags_lists[key].name)
        else:
            raise TypeError("unknown key-value pair used to set item")

    def overwrite(self, other):
        """
        Add a new tags_lists, or overwrite it if it's the same name
        Args:
            other: a dict of a new thing to add, {"name":[[tag, 0.5]]}
        """
        if isinstance(other, dict):
            for key, tag_pair in other.items():
                if key not in self.names():
                    self.tags_lists.append(TagsList(tags=tag_pair, name=key))
                else:
                    self.tags_lists[self.name_index(key)]=TagsList(tags=tag_pair, name=key)            
        elif isinstance(other, TagsList):
            if other.name not in self.names():
                self.tags_lists.append(other)
            else:
                self[other.name] = other
        elif isinstance(other, list):
            # this is probably a legacy system where tags were all merged and stored
            # ex: [[tag1, prob], [tag2, prob]]
            parameters.log.info(f"skipping adding tags to {self.name}, tag stored in legacy list")
        else:
            # uncomment to check parent item containing this img dict
            #print(f"{self.name}, {self.tags_lists}")
            #import gc
            #refs = gc.get_referrers(self)
            #from classes.class_image import ImageDatabase
            #for ref in refs:
            #    print("Found parent Images instance:", ref)
            raise TypeError(f"unknown type for other: {type(other)}, {other}")

    def add_data(self, other):
        """add data, doesn't overwrite if it's the same name, just add missing data

        Args:
            other (dict, TagsList, TagsList):  a dict of a new thing to add, {"name":[[tag, 0.5]]}
        """
        if isinstance(other, dict):
            for key, tag_pair in other.items():
                if key not in self.names(): #easy, new data add to list
                    self.tags_lists.append(TagsList(tags=tag_pair, name=key))
                else: # overlapping names, add new data from other onto self
                    self.tags_lists[self.name_index(key)]+=tag_pair
        elif isinstance(other, TagsLists): # for each taglist, used to merge tagslists in merge_databases
            for tl in other.tags_lists:
                if tl.name in self.names():
                    self.tags_lists[self.name_index(tl.name)]+=tl
                else:
                    self.tags_lists.append(TagsList(tags=tl.save(), name = tl.name))
        elif isinstance(other, TagsList): # either update taglist with same name or add a new taglist
            if other.name in self.names():
                self.tags_lists[self.name_index(other.name)]+=other
            else:
                self.tags_lists.append(TagsList(tags=other.save(), name = other.name))
        else:
            raise TypeError("Unknown type ti add to self")
            
    def name_index(self, key):
        return self.names().index(key)
    
    def names(self):
        return [tags_list.name for tags_list in self.tags_lists]

    def save(self):
        result = defaultdict(lambda: [])
        for tags_list in self.tags_lists:
            result[tags_list.name] = tags_list.save()
        return result

    def save_tuple(self):
        result = defaultdict(lambda: [])
        for tags_list in self.tags_lists:
            result[tags_list.name] = tags_list.save_tuple()
        return result

    def simple_tags(self):
        """merge all tagslist into one and return a combined tagslist"""
        simple_tags = TagsList()
        simple_tags += self.tags_lists
        return simple_tags.simple_tags() #convert to list of strings

    def refresh_unsafe_tags(self, all_accepted_tags):
        for tags_list in self.tags_lists:
            if "rejected" in tags_list.name: # all the tags that came from rule34 or gelbooru
                new_accepted = tags_list.all_tags_in(all_accepted_tags)
                if new_accepted:
                    new_accepted.name = tags_list.name[len("rejected") + 1:]
                    self[tags_list.name[len("rejected") + 1:]] = new_accepted
                else:
                    new_accepted = TagsList(name=self[len("rejected") + 1:].name, tags=[])
                    self[tags_list.name[len("rejected") + 1:]] = new_accepted

    def build_merged_tags(self):
        for tlist in self.tags_lists:
            self.merged_tags+=tlist

    def tags_over_confidence(self, confidence: float) -> TagsList:
        # build merged confidence if it wasn't made
        if not self.merged_tags:
            self.build_merged_tags()
        return self.merged_tags.tags_over_confidence(confidence)

    def tags_under_confidence(self, confidence: float) -> TagsList:

        # build merged confidence if it wasn't made
        if not self.merged_tags:
            self.build_merged_tags()
        return self.merged_tags.tags_under_confidence(confidence)

    def all_tags_in(self, other):
        """
        Args:
            other: TagsLists

        Returns: a new TagsLists that hosts the tags in common with the other TagsLists

        """
        combined = TagsLists(name=self.name)
        if isinstance(other, type(self)):
            for name in self.names():
                if name in other.names():
                    new_tags = self[name].all_tags_in(other[name])
                    if new_tags:
                        combined.overwrite(new_tags)
        return combined

    def common_tags(self, other):
        """
        Args:
            other: TagsLists

        Returns: a new TagsLists that hosts the tags in common, as a single TagsList inside the TagsLists
        """
        combined_tags = TagsList(name="Combined "+self.name)
        combined_tags += set([tag.tag for list_tags in self for tag in list_tags if "rejected" not in list_tags.name])
        if isinstance(other, type(self)):
            combined_tags = combined_tags.all_tags_in(set([tag.tag for list_tags in other for tag in list_tags if "rejected" not in list_tags.name]))
        combined = TagsLists([combined_tags], name=self.name)
        return combined

    def get_tags_in(self, key): # similar to get method, but adds an empty return if out of bound or not found
        if isinstance(key, int) and key < len(self.tags_lists):
            return self.tags_lists[key]
        elif isinstance(key, str) and key in self.names():
            return self.tags_lists[self.name_index(key)]
        else:
            return TagsList(name="empty")
        
    def get_tags_unique_in(self, key):
        
        if isinstance(key, int) and key < len(self.tags_lists):
            key_index = key
        elif isinstance(key, str) and key in self.names():
            key_index = self.name_index(key)
        else:
            return TagsList(name="empty")
        
        unique = TagsList(name="Unique "+self.name)
        key_tags = {tag.tag for tag in self.tags_lists[key_index]}
        non_key_tags = {tag.tag  for i, list_tags in enumerate(self.tags_lists) for tag in list_tags if i != key_index}
        unique+=(key_tags.difference(non_key_tags))
        return unique
   
    def prune_under_threshold(self, kv_pairs):
        # kv_pair is a list or iterable with ("name for tags list", threshold prob)    
        for tl in self.tags_lists:
            for k, threshold in kv_pairs:
                if tl.name == k:
                    tl.tags = [t for t in tl.tags if (t not in tag_categories.CHARACTERS_TAG and t.probability > threshold) or 
                               (t in tag_categories.CHARACTERS_TAG and t.probability > parameters.PARAMETERS["swinv2_character_threshold"])]
    
    def normalize(self):
        # clean up tagsList names, add misc checks in here
        # legacy used lowercase caformer, we now use Caformer, we also merge to Caformer if it exists
        remove_indices = []
        names = self.names()
        for i, tl in enumerate(self.tags_lists):
            if tl.name == "caformer" and "Caformer" in names:
                self["Caformer"] += tl
                remove_indices.append(i)
            elif tl.name == "caformer":
                tl.name = "Caformer"
        
        for i in sorted(remove_indices, reverse=True):
            self.tags_lists.pop(i)
                  
class TagsList:
    def __init__(self,*, tags=None, name=""):
        # manual_tags, manual_rejected_tags, rule34, rejected_rule34, Caformer, SwinV2V3, filtered_new_tags, filtered_rejected_tags
        # no probability involved, tagElement stores prob 
        if tags is None:
            tags = []
        self.tags = []
        for tag in tags:
            self.tags.append(TagElement(tag))
        self.name: str = name
        self.token_length: int = 0

    def __repr__(self):
        return "TagsList(name="+self.name+",tags="+str(self.tags)+")"

    def __iter__(self):
        return iter(self.tags)
    
    def __bool__(self):
        return bool(self.tags)

    def __iadd__(self, other): # this does the += operator, modifies in place
        if isinstance(other, type(self)):
            self.tags += [tag for tag in other.tags if tag not in self.tags]
        elif isinstance(other, (list, set)):
            for elem in other:
                
                if isinstance(elem, TagsList):
                    
                    self.tags += [tag for tag in elem if tag not in self.tags]
                elif TagElement(elem) not in self.tags: # other was list of str or list of tagelements    
                    
                    self.tags += [TagElement(elem)]
        elif isinstance(other, TagElement):
            if other not in self.tags: #only add new tags
                self.tags += [other]
        elif isinstance(other, str):
            if other not in self.simple_tags(): #only add new tags
                self.tags += [TagElement(other)]
        elif isinstance(other, TagsLists):
            for other_tag_list in other.tags_lists:
                self.tags += [tag for tag in other_tag_list if tag not in self.tags]
        elif isinstance(other, TagElement):
            self.tags += [TagElement(tag) for tag in other]
        elif other is None:
            raise TypeError("__iadd__ with none type")
        else:
            raise TypeError(f"Unsupported __iadd__ operator for {type(self)} and {type(other)}")
        return self
    
     
    def __extend__(self, other):
        """calls the iadd method since the operations are similar, return self"""
        return self.__iadd__(other)
        
    def __add__(self, other):
        new = TagsList(name=self.name, tags=self.tags)
        
        if isinstance(other, type(self)):
            
            new.tags += [tag for tag in other.tags if tag.tag not in new]
        elif isinstance(other, (list, set)):
            
            # here we have to be careful if the list contains TagElements or str
            new.tags += [TagElement(tag) for tag in other 
                         if (isinstance(tag, str) and tag not in new) or
                         (isinstance(tag, TagElement) and tag.tag not in new)]
            
        elif isinstance(other, TagElement):
            
            if other.tag not in new.tags:
                
                new.tags += [other]
        elif isinstance(other, str):
            if other not in new.tags:
                
                new.tags += [TagElement(other)]
        elif isinstance(other, TagsLists):
            # we only merge similar purposed tagslists
            # rejected + rejected
            # not rejected + not rejected
            for other_tag_list in other.tags_lists:
                if (("rejected" in self.name and "rejected" in other_tag_list.name) or
                    ("rejected" not in self.name and "rejected" not in other_tag_list.name)): 
                    # change behaviors if the taglist's purpose if for storing or filtering
                    new.tags += [tag for tag in other_tag_list if tag.tag not in new]
        else:
            raise TypeError(f"Unsupported __add__ operator for {type(self)} and {type(other)}")
        
        return new
    
    def __sub__(self, other):
        new = TagsList(name=self.name)

        if isinstance(other, type(self)):
            
            simple_other = other.simple_tags()
            new.tags = [tag for tag in self.tags if tag.tag not in simple_other]
        elif isinstance(other, (list, set)):
            
            proper_other = TagsList(tags=other)
            new.tags = [tag for tag in self.tags if tag.tag not in proper_other]
        elif isinstance(other, TagElement):
          
            new.tags = [tag for tag in self.tags if tag.tag != other.tag]
          
        elif isinstance(other, str):
            
            new.tags = [tag for tag in self.tags if tag.tag != other]
        elif isinstance(other, TagsLists):
            
            # here we don't check for similar purposed tagslist because most operations are additive
            # and removal is used only for rejected and manual fixes
            combined = TagsList()
            combined += other.tags_lists
            new.tags = [tag for tag in self.tags if tag.tag not in combined]
        else:
            raise TypeError(f"Unsupported __sub__ operator for {type(self)} and {type(other)}")
        
        return new

    def __eq__(self, other):

        if isinstance(other, type(self)):
            if len(self.tags) != len(other.tags):
                return False
            return all([tag in other.tags for tag in self.tags])
        elif isinstance(other, (list, set)):
            if len(self.tags) != len(other):
                return False
            return all([tag in other for tag in self.tags])

        return False

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.tags[key]
        elif isinstance(key, TagElement):
            return self.tags[[tag.tag for tag in self.tags].index(key.tag)]
        elif isinstance(key, str):
            return self.tags[[tag.tag for tag in self.tags].index(key)]
        else:
            raise KeyError(f"Unknown key type {type(key)}")

    def __setitem__(self, key, value):
        if isinstance(value, TagElement):
            if key in self.tags:
                self.tags[self.tags.index(key)] = value
            else:
                self.tags.append(value)
        elif isinstance(value, str|tuple|list):
            if key in self.tags:
                self.tags[self.tags.index(key)] = TagElement(value)
            else:
                self.tags.append(TagElement(value))
        else:
            raise TypeError(f"Unknown key-value pair types {type(key)}, {type(value)}")

    def __len__(self):
        return len(self.tags)

    def __contains__(self, item):
        if isinstance(item, TagElement):
            for tag in self.tags:
                if tag.tag == item.tag:
                    return True
            return False
        elif isinstance(item, str):
            for tag in self.tags:
                if tag.tag == item:
                    return True
            return False
        else:
            return False
    
    def pop(self, index):
        """
        Same behaviour as a list pop
        Args:
            index: int, str or TagElement
        Returns: TagElement
        """
        if isinstance(index, int):
            return self.tags.pop(index)
        if isinstance(index, str | TagElement):
            return self.tags.pop(self.tags.index(index))

    def get_token_length(self):
        if len(self):
            self.token_length: int = len(tokenize(", ".join([tag.tag for tag in self.tags]), context_length=500, truncate=True).nonzero()) - 2
        else:
            self.token_length = 0
        return self.token_length

    def all_tags_in(self, other):
        """
        Args:
            other:

        Returns: all tags that are in both the self and other, or None if empty

        """
        if isinstance(other, type(self)):
            new_tags = [tag for tag in self.tags if tag.tag in other.tags]
        elif isinstance(other, (list, set)):
            new_tags = [tag for tag in self.tags if tag.tag in other]
        elif isinstance(other, TagElement):
            new_tags = [tag for tag in self.tags if tag.tag == other]
        elif isinstance(other, TagsLists):
            combined = TagsList()
            combined += other.tags_lists
            new_tags = [tag for tag in self.tags if tag.tag in combined.tags]
        else:
            new_tags = []
        return TagsList(name=self.name, tags=new_tags)

    def save(self):
        return [x.save() for x in self.tags]

    def save_tuple(self):
        # saves the tag and probability (if applicable) and returns a list of items or tuples
        return [x.save_tuple() for x in self.tags]

    def simple_tags(self) -> list[str]:
        return  [x.tag for x in self.tags]
        
    def clear(self):
        self.tags = []

    def to_high(self):
        """
        Returns: all highs tags resulting from this list
        """
        result = TagsList()
        for tag in self.tags:
            if tag.tag in tag_categories.TAG2HIGH_KEYSET:
                result += tag_categories.TAG2HIGH[tag.tag]
        return result

    def to_low(self):
        """
        Returns: all low tags resulting from this list
        """
        result = TagsList()
        for tag in self.tags:
            if tag.tag in tag_categories.LOW2TAGS_KEYSET:
                result += tag_categories.LOW2TAGS[tag.tag]
        return result

    def has_low(self):
        """
        Returns: all tags that have low setting and have a tag present in the self that is in a tag_categories
        """
        result = TagsList()
        for tag in self.tags:
            if tag.tag in tag_categories.LOW2TAGS_KEYSET and any(x in self.tags for x in tag_categories.LOW2TAGS[tag.tag]):
                result += tag
        return result

    def get_low_for_tag(self, specific_tag):
        # this is ussually runed only on full tags
        result = TagsList()
        for tag in self.tags:
            
            if specific_tag in tag_categories.LOW2TAGS.get(tag.tag, []):
                result += tag
        return result
    
    def hard_rejected_tags(self):
        """
        Returns: all tags that are hard rejected in the list
        """
        return TagsList(tags=[tag for tag in self.tags if tag.tag in tag_categories.REJECTED_TAGS])

    def not_hard_rejected_tags(self):
        """
        Returns: all tags that are not hard rejected in the list
        """
        return TagsList(tags=[tag for tag in self.tags if tag.tag not in tag_categories.REJECTED_TAGS])

    def tags_over_confidence(self, confidence: float):
        return TagsList(tags=[tag for tag in self.tags if tag.probability >= confidence])

    def tags_under_confidence(self, confidence: float):
        return TagsList(tags=[tag for tag in self.tags if tag.probability <= confidence])

    def recommendations(self):
        """
        Returns: all recommended tags
        """
        recommendations = TagsList(name="recommendations")
        for recommended_tag, triggers in tag_categories.TAGS_RECOMMENDATIONS.items():
            for x in triggers:
                if (recommended_tag not in recommendations and
                        recommended_tag not in self and
                        all([y in self for y in x if y[0] != "-" or len(y) < 4]) and
                        all([y[1:] not in self for y in x if y[0] == "-" and len(y) > 3])
                ):
                    recommendations+=recommended_tag
                                 
        return recommendations

    def init_display_properties(self, highlight_tags=None):
        for tag in self.tags:
            tag.init_display_properties(
                color=tag_categories.COLOR_DICT[tag.tag] if tag.tag in tag_categories.COLOR_DICT.keys() else (255,255,255,255),
                priority=tag_categories.PRIORITY_DICT[tag.tag] if tag.tag in tag_categories.PRIORITY_DICT.keys() else 99999,
                highlight=tag.tag in highlight_tags if highlight_tags else False
            )

    def init_manual_display_properties(self, manual_tags):
        if isinstance(manual_tags, bool):
            for tag in self.tags:
                tag.manual = manual_tags
        elif isinstance(manual_tags, TagsList|list|set):
            for tag in self.tags:
                tag.manual = tag in manual_tags

    def init_rejected_display_properties(self, rejected_tags):
        if isinstance(rejected_tags, bool):
            for tag in self.tags:
                tag.rejected = rejected_tags
        elif isinstance(rejected_tags, TagsList|list|set):
            for tag in self.tags:
                tag.rejected = tag in rejected_tags

    def init_highlight_display_properties(self, highlight_tags):
        """Takes a bool or a list of tags that should be highlighted.
        All tags are highlighted if the argument is a bool.
        """
        if isinstance(highlight_tags, bool):
            for tag in self.tags:
                tag.highlight = highlight_tags
        elif isinstance(highlight_tags, TagsList|list|set):
            for tag in self.tags:
                tag.highlight = (tag in highlight_tags) or (any(u in tag for u in tag_categories.UNRELIABLE_SMALL_TAGS))

    def priority_sort(self):
        """
        Sort the tags in place so that the tag with the highest priority is first
        """
        self.tags.sort(key=lambda x: x.sort_priority, reverse=False)

    def loose_match(self, tags)->TagsList:
        """
        Args:
            tags [str|list|set|TagsList] : list of tags to match

        Returns: all tags that are in the self that are in a tag_categories
        """
        if tags:
            if isinstance(tags, str):
                tags = [tags]
            elif isinstance(tags, TagsList):
                tags = tags.simple_tags()
            elif isinstance(tags, (set, list)):
                tags = list(tags)
            return TagsList(tags=[tag for tag in self.tags if any([t in tag.tag for t in tags])])
        else:
            return TagsList()
    
    def loose_string_check(self, search_tags, require_all=True) -> bool:
        """similar to loose_match but returns a bool if a loose match is found

        Returns: bool: if tags are found
        """
        if search_tags:
            if isinstance(search_tags, str):
                search_tags = [search_tags]
            elif isinstance(search_tags, TagsList):
                search_tags = search_tags.simple_tags()
            elif isinstance(search_tags, (set, list)):
                search_tags = list(search_tags)
            
            if len(search_tags) > 1 and require_all:
                # check if all tags in the search requirement are present
                return all([any(t in tag.tag for tag in self.tags) for t in search_tags])
            else:
                return any([any([t in tag.tag for t in search_tags]) for tag in self.tags])
        else:
            return False

    def clean_empty(self):
        self.tags = [tag for tag in self.tags if tag.tag]

class TagElement:
    def __init__(self, tag: str|tuple|list, *, probability: float=0.0):
        if isinstance(tag, str):
            self.tag: str = tag
            self.probability = probability
        elif isinstance(tag, (tuple, list)):
            self.tag: str = tag[0]
            self.probability: float = tag[1]
        elif isinstance(tag, type(self)):
            self.tag = tag.tag
            self.probability = tag.probability
            if all(hasattr(tag, attr) for attr in ["highlight", "color", "sort_priority", "manual", "rejected"]):
                self.highlight = tag.highlight  # if the tag should have a background
                self.color = tag.color  # the color of the tag associated
                self.sort_priority = tag.sort_priority  # if it should be shown first or after
                self.manual = tag.manual  # if it's in a manual
                self.rejected = tag.rejected  # if it's in a manual
                if hasattr(tag, "wiki_page"):
                    self.wiki_page = tag.wiki_page
        else:
            raise TypeError(f"EXTREMELY WRONG, DON'T SAVE ANYTHING, PLEASE REPORT ANYTHING YOU DID TO COME HERE: \nUnknown type for tag: {type(tag)}")
            

    def __str__(self):
        return self.tag

    def __len__(self):
        return len(self.tag)

    def __hash__(self):
        return hash(self.tag)

    def __bool__(self):
        return bool(self.tag)

    def __repr__(self):
        return "TE(tag="+self.tag+", p="+str(self.probability)+")"

    def __float__(self):
        return self.probability

    def __contains__(self, item): # the "x in tag" operator 
        return item in self.tag
    
    def __eq__(self, other):

        if isinstance(other, type(self)):
            return self.tag == other.tag
        elif isinstance(other, str):
            return self.tag == other
        elif isinstance(other, list|tuple):
            return self.tag == other[0]

        return False

    def save(self):
        return self.tag

    def save_tuple(self):
        if self.probability:
            return [self.tag, self.probability]
        else:
            return self.tag

    def init_display_properties(self,manual=False,rejected=False, highlight = False, color=(255, 255, 255, 255), priority = 99999):
        self.highlight = highlight # if the tag should have a background
        self.color = color # the color of the tag associated
        if isinstance(priority, int):
            self.sort_priority = priority # if it should be shown first or after
        else:
            self.sort_priority = priority
            print("error: none int:",priority)
        self.manual = manual # if it's in a manual
        self.rejected = rejected # if it's in a manual

    def wiki(self):
        if hasattr(self, "wiki_page"):
            return self.wiki_page
        else:
            # check if we already have the wiki page
            if self.tag in curr_wiki_info:
                self.wiki_page = curr_wiki_info[self.tag]
                return self.wiki_page
            parameters.log.info(f"Getting wiki page for {self.tag}")
            self.wiki_page = wiki_info.get_wiki_page(self.tag)
            # updating wiki_info happens elsewhere in batches
            return self.wiki_page