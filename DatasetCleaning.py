from interfaces import dataset_cleaning
import PySide6.QtGui as QtGui
from PySide6.QtWidgets import QWidget
import PySide6.QtCore as QtCore
from PySide6.QtCore import Slot

#import database
from classes.class_database import Database

from collections import Counter
import os
import pandas as pd
from resources import parameters
from resources.tag_categories import COLOR_DICT, EMOJI_5KPLUS, EMOJI_MINOR, EMOJI_10KPLUS, SERIES_BLACKLIST, SERIES_EXCEPTION, REJECTED_TAGS, TAG_CATEGORIES

SERIES_EXCEPTION_SET = set(list(SERIES_EXCEPTION) + [k for k in COLOR_DICT.keys() if any(s in k for s in SERIES_BLACKLIST)])

file_phrase=[
]
secondary_tag=[
]

def print_char_overlap():
    char_list = TAG_CATEGORIES["CHARACTERS"]["KNOWN CHARACTERS 1"]["tags"] + TAG_CATEGORIES["CHARACTERS"]["KNOWN CHARACTERS 2"]["tags"]
    
    subset_dict = {}
    for char in char_list:
        if False:
            char_name = char.split()
            common_char = [c for c in char_list if all(cp in c for cp in char_name) and c != char]
            if common_char:
                subset_dict[char] = common_char
        if True:
            if "(cosplay)" in char:
                parameters.log.info(char)
    
    for k, v in subset_dict.items():
        parameters.log.info((k,", ", ", ".join(v)))
            

    
#print_char_overlap()


if len(file_phrase) != len(secondary_tag):
    parameters.log.info("BAD!, check file phrases")

#not used, but might be useful if needed to separate some elements with a smaller font
w_font_font = parameters.PARAMETERS['font_name'] 
w_font_size = int(parameters.PARAMETERS['font_size'])
base_font = "font: {w_font_font}; font-size: {w_font_size};"

def make_combination(modifiers, base_tag):
    sub_category = [c + " " + cloth for cloth in base_tag for c in modifiers]
    base_category = [cloth for cloth in base_tag for _ in modifiers]
    return sub_category, base_category

def filter_tags(tags, filter_set, remove_set):
    """
    :param tags: 
    :param filtered_set: check for tags in this list
    :param remove_set: removes tags in this list if the matching pair in filter_set also exists
    :return: filtered tag list
    """
    filtered_words = []
    for f, r in zip(filter_set, remove_set):
        if f in tags and r in tags:
            filtered_words.append(r)
    filtered_words = list(set(filtered_words))
    return filtered_words

class DatabaseTagFrequencyView(QtCore.QAbstractListModel):
    def __init__(self, sorted_tagcount_tuple, color_dict, grouping=False, parent=None):
        """
        :param sorted_tagcount_tuple: list of ("tag", frequency) pairs
        :param color_dict: a dictionary that maps the tag to an associated color
        :param grouping: indicator if sorting based on tag groups is enabled
        :return: class instance
        """
        super().__init__(parent)
        self.sorted_tags = sorted_tagcount_tuple
        self.counter_len = len(sorted_tagcount_tuple)
        self.color_dict = color_dict
        self.grouping=grouping

    def rowCount(self, parent):
        return self.counter_len

    def data(self, index, role):
        # return different data depending on the role
        tag = self.sorted_tags[index.row()]
        if role == QtGui.Qt.ItemDataRole.DisplayRole:
            return str(tag[0]) + ", " + str(tag[1])

        if role == QtGui.Qt.ItemDataRole.ForegroundRole:
            # return a preselected color for a tag or return the default color
            brush = QtGui.QBrush()
            tag_val = tag[0]
            if self.grouping and "," in tag_val:
                
                tag_val = tag_val.split(",")[-1]
                tag_val = tag_val.strip()
                
            if tag_val in self.color_dict:
                (red, green, blue, alpha) = self.color_dict[tag_val]
                brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
            else:
                
                brush.setColor(QtGui.QColor.fromRgb(255,255,255,255))
            return brush

        if role == QtGui.Qt.ItemDataRole.BackgroundRole and tag[1] == 0: 
            # show a red background it the count is 0
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor.fromRgb(230,20,20,255))
            return brush
        
        if role == QtGui.Qt.ItemDataRole.FontRole and tag[1] == 0:
            font = QtGui.QFont()
            font.setBold(True)
            font.setStrikeOut(True)
            return font


class DatasetCleaningView(QWidget, dataset_cleaning.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # setting default values
        self.temp_database = None
        self.tags_before = Counter()
        self.tags_after = Counter()
        
        # disctionary of "group name" --> counter
        self.before_group_counters = {}
        self.after_group_counters ={}
        
        self.second_list = False
        
        self.main_project_dir =parameters.MAIN_FOLDER
        self.main_resource_dir = os.path.join(self.main_project_dir, "resources")

        # this also defines some attributes store in self
        self.loaded_resources = False
        self.update_resources()
        self.loaded_resources = True
        self.before_max_len = 0
        self.after_max_len = 0
        self.filtered_view = False
        # define button's action on click
        self.comboBox_filter_method.currentTextChanged.connect(self.sort_button_pushed)
        self.comboBox_filterGroups.currentTextChanged.connect(self.filter_groups)
        
        self.built_groups = False
        
        self.pushButton_load_dataset.clicked.connect(self.load_database_button)
        self.pushButton_cleanup_tags.clicked.connect(self.clean_tags)
        self.pushButton_reload_resources.clicked.connect(self.update_resources)
        self.pushButton_apply_change.clicked.connect(self.apply_changes)
        self.lineEdit_search_tags.textChanged.connect(self.show_search_result)
        self.pushButton_filter_with_conditional.clicked.connect(self.filter_view)
        
        
        
        self.slider_activation_thresh.valueChanged.connect(self.update_slider_activation_label)
        self.slider_prob_thresh.valueChanged.connect(self.update_slider_prob_label)


    def show_visual_list(self, sorted_list, grouping=False, left=True):
        if left:
            self.listView_dataset_cleaning.setModel(DatabaseTagFrequencyView(sorted_list, self.color_dict, grouping=grouping))
        if not left and self.second_list:
            self.listView_2_dataset_cleaning.setModel(DatabaseTagFrequencyView(sorted_list, self.color_dict, grouping=grouping))
        elif not left and not self.second_list: #empty right list
            self.listView_2_dataset_cleaning.setModel(None)

    def replace_texts(self, tags, full_filter_tags, filter_tags, replace_tags, debugBool=False):
        remove_words = [t for t in tags if t in full_filter_tags]
        replace_words = []
        for f, r in zip(filter_tags, replace_tags):
            if f in remove_words and r in remove_words:
                replace_words.append(f)
                if debugBool:
                    parameters.log.info(f"Removed {f} bc of {r}")
        return [t for t in tags if t not in replace_words]
    
    def get_tags_sorted_thresh(self, img):
        return sorted(img.auto_tags, key=lambda x: float(x[1]), reverse=True)

    @Slot()
    def update_slider_activation_label(self):
        curr_val = str(self.slider_activation_thresh.value())
        self.slider_activation_label.setText(curr_val)
        
    @Slot()
    def update_slider_prob_label(self):
        curr_val = self.slider_prob_thresh.value()
        self.slider_prob_label.setText(f"{curr_val}%")

    @Slot()
    def show_search_result(self):
        sorted_list = []
        search_string = self.lineEdit_search_tags.text()
        if search_string and len(search_string)>0:
            search_string = search_string.split(",")
            if self.second_list:
                sorted_list = [(k, self.tags_after[k]) for k in self.tags_after.keys() if all(word in k for word in search_string)]
            else:
                sorted_list = [(k, self.tags_before[k]) for k in self.tags_before.keys() if all(word in k for word in search_string)]
                
            if sorted_list:
                sorted_list = sorted(sorted_list, key=lambda item: (item[1], item[0]), reverse=True)
                self.listView_searched_tags.setModel(DatabaseTagFrequencyView(sorted_list, self.color_dict, grouping=False))
            else:
                sorted_list = [(0, "No Results")]
                self.listView_searched_tags.setModel(DatabaseTagFrequencyView(sorted_list, {}, grouping=False))
        else:
            sorted_list = [(0, "No Results")]
            self.listView_searched_tags.setModel(DatabaseTagFrequencyView(sorted_list, {}))

    @Slot()
    def filter_view(self):
        filter_phrases = self.lineEdit_filter_phrase.text()
        if filter_phrases:
            self.filtered_view = True
            filter_phrases = filter_phrases.split(",")
            # updating the Before list
            self.tags_before = Counter()  
            for img in self.temp_database.images:
                tags = img.get_full_tags()
                if all([phrase in tags for phrase in filter_phrases]):
                    self.tags_before.update(tags)
            if self.second_list: #if the second list is showing, refresh list
                self.clean_tags()
            self.sort_button_pushed()

        elif self.filtered_view: #show the default view for empty conditional
            self.filtered_view = False
            self.tags_before = Counter()
            for img in self.temp_database.images:
                tags = img.get_full_tags()
                self.tags_before.update(tags)
            if self.second_list: #if the second list is showing, refresh list
                self.clean_tags()
            self.sort_button_pushed()
    @Slot()
    def update_dataset_counter(self):
        self.label_dataset_cleaning.setText(f"Before:  [Unique tag count: {len(self.tags_before)} , Max tag length: {self.before_max_len}]")
        if self.second_list:
            self.label_2_dataset_cleaning.setText(f"After:  [Unique tag count: {len(self.tags_after)} , Max tag length: {self.after_max_len}]")
        else:
             self.label_2_dataset_cleaning.setText("After:")

    @Slot()
    def update_resources(self):
        #update filter data
        if self.loaded_resources:
            parameters.log.info("Reloading filter and tag resources")

        df = pd.read_csv(os.path.join(self.main_resource_dir, "filtertags.csv"), index_col=False)
        self.keeptags = list(df["keep"])
        self.removetags = list(df["remove"])
        
        if True: # enable this to update filtertags so it filters out things that are already in the tag categories
            from resources.tag_categories import LOW2TAGS, LOW2TAGS_KEYSET, TAG2HIGH_KEYSET, TAG2HIGH
            new_keep = []
            new_remove = []
            for k, r in zip(self.keeptags, self.removetags):
                if (r in LOW2TAGS_KEYSET and k in LOW2TAGS[r]) or (r in TAG2HIGH_KEYSET and k in TAG2HIGH[r]) or (k in LOW2TAGS_KEYSET and r in LOW2TAGS[k]) or (k in TAG2HIGH_KEYSET and r in TAG2HIGH[k]):
                    parameters.log.info(f"Removing, {k}, {r}")
                else:
                    new_keep.append(k)
                    new_remove.append(r)
            new_df = pd.DataFrame({
                "keep": new_keep,
                "remove":new_remove
            })
            new_df.to_csv(os.path.join(self.main_resource_dir, "filtertags.csv"), index=False)        
        
        # update the color reference dict
        self.color_dict = COLOR_DICT

        questionable = ["instant loss"]

        self.only_color =  ["red", "blue", "green", "black", "white", "grey", "gray","beige", "brown", 
                        "pink", "orange", "gold", "blonde", "yellow", "purple", "aqua"]
        self.bow_keep = [c + " bowtie" for c in self.only_color] + ["hair bow","bowtie", "hair ribbon", "hair bow"] 
        self.bow_keep+= [c + " necktie" for c in self.only_color] + [c + " bowtie" for c in self.only_color]
        self.bow_remove = [c + " bow" for c in self.only_color] + ["bow", "bow","ribbon", "hair ribbon"] 
        self.bow_remove+= [c + " tie" for c in self.only_color] + ["bow" for _ in self.only_color]
        
        def Merge(dict1, dict2): # | syntax only available for >= python   3.9
            res = dict1 | dict2
            return res 

        self.emoji = Merge(Merge(EMOJI_MINOR, EMOJI_5KPLUS), EMOJI_10KPLUS)

        
        
        self.blacklist = REJECTED_TAGS

        description_tags = ["red", "blue", "green", "black", "white", "gray", "grey", "brown", "pink", 
                            "orange", "yellow","multicolored","purple", "aqua",
                            "naked", "open","closed","plaid", "pleated", "striped","loose", "mini", "long", "short"
                            "fur-trimmed", "latex", "fur", "leather", "lolita"]
        general_tags = ['apron', 'armband', 'armor', 'ascot', 'bag', 'bandana', 'bathrobe', 'belt', 'bikini', 'blindfold', 
                        'bloomers', 'bodysuit', 'bow', 'bowtie', 'bra', 'buruma', 'camisole', 'cape', 'capelet', 'cardigan',
                        'cat', 'chain', 'choker', 'cloak', 'coat', 'collar', 'corset', 'dress', 'eyeliner', 'eyeshadow', 
                        'flower', 'frills', 'fur', 'garter belt', 'gloves', 'hairband', 'hakama', 'haori', 'hat', 'headband', 
                        'hoodie', 'horns', 'jacket', 'kimono', 'legwear', 'leotard', 'lips', 'neckerchief', 'necktie', 
                        'one-piece swimsuit', 'panties', 'pants', 'pantyhose', 'parka', 'ribbon', 'robe', 'rose', 
                        'sailor collar', 'sash', 'scarf', 'scrunchie', 'serafuku', 'shirt', 'shorts', 'skirt', 'socks', 
                        'sports bra', 'sweater', 'swimsuit', 'tank top', 'thighhighs', 'tiara', 'tunic', 'vest']
        
        self.sub_categ, self.base_categ = make_combination(description_tags, general_tags)

        if len(self.keeptags) != len(self.removetags):
            parameters.log.error("Mismatch length, check filtertags.csv")
        if len(self.bow_keep) != len(self.bow_remove):
            parameters.log.errpr("Mismatch length, check bows")
        if len(self.sub_categ) != len(self.base_categ):
            parameters.log.error("Mismatch length, check general tags and description modifier")

    @Slot()
    def apply_changes(self):
        parameters.log.info("Saving database")
        self.temp_database.save_database()

    @Slot()
    def reload_groups(self):
        self.built_groups = False
        self.comboBox_filterGroups.clear()
        self.comboBox_filterGroups.addItem("Main View")
        self.before_group_counters = {}
        self.after_group_counters = {}
        if self.temp_database:
            for groups in self.temp_database.groups.keys():
                    self.comboBox_filterGroups.addItem(groups)
                    self.before_group_counters[groups] = Counter()
                    self.after_group_counters[groups] = Counter()
        self.built_groups = True
              
    @Slot()
    def load_database_button(self):
        
        
        if self.lineEdit_dataset_dir.text().endswith("tags_frequency.txt"):
            parameters.log.info("Loading dataset " + str(self.lineEdit_dataset_dir.text()))
            self.reload_groups()
            self.before_max_len = 0
            self.after_max_len = 0
            self.tags_before = Counter()
            self.tags_after = Counter()
            with open(self.lineEdit_dataset_dir.text(),'r') as f:
                lines = [line for line in f]
            temp_dict = {}
            for l in lines:
                x = l.split(":", 1)
                count, tag = x[0], x[1]
                temp_dict[tag.strip()] = int(count.strip())
            
            self.tags_before = Counter(temp_dict)
            
            self.before_group_counters["Main View"] = self.tags_before
            self.after_group_counters["Main View"] = self.tags_after
            
            
            
            self.sort_visual_list(self.tags_before)
            self.second_list=False
            self.sort_visual_list(self.tags_after, left=False)
            return 0
        
        elif self.lineEdit_dataset_dir.text():
            parameters.log.info("Loading dataset " + str(self.lineEdit_dataset_dir.text()))
            self.temp_database = Database(self.lineEdit_dataset_dir.text())
            self.reload_groups()
            self.before_max_len = 0
            self.after_max_len = 0
            self.tags_before = Counter()
            self.tags_after = Counter()
            
            # create main view
            for img in self.temp_database.images:
                tags = img.get_full_tags()
                self.before_max_len = max(len(tags), self.before_max_len)
                self.tags_before.update(tags)
                
            # create sub groups

            
            for group_name, group_obj in self.temp_database.groups.items():
                md5s = group_obj.md5s
                for md5 in md5s:
                    
                    img_index = self.temp_database.index_of_image_by_md5(md5)
                   
                    tags = self.temp_database.images[img_index].get_full_tags()
                    self.before_group_counters[group_name].update(tags)
                    
                
            self.before_group_counters["Main View"] = self.tags_before
            self.after_group_counters["Main View"] = self.tags_after
            
            self.sort_visual_list(self.tags_before)
            self.second_list=False
            self.sort_visual_list(self.tags_after, left=False) # refresh second list
            
            self.update_dataset_counter()
            parameters.log.info(f"Loaded database with {len(self.temp_database.images)} imgs")
        else:
            parameters.log.error("No Valid Directory Entered")
          
    @Slot()
    def filter_groups(self):
        if self.built_groups:
            group_name = self.comboBox_filterGroups.currentText()
            self.changed_views = False
            
            self.tags_before = self.before_group_counters[group_name]
            self.tags_after = self.after_group_counters[group_name]
            
            self.sort_button_pushed()

              
    @Slot()
    def sort_button_pushed(self):
        self.sort_visual_list(self.tags_before)
        if self.second_list:
            self.sort_visual_list(self.tags_after, left=False)

    @Slot()
    def sort_visual_list(self, counter_ref, left=True):
        dropdown = self.comboBox_filter_method.currentIndex()
        
        bf_key = self.tags_before.keys()
        af_key = self.tags_after.keys()
        tag_list = []
        grouping=False
        match dropdown:
            case 0: # frequnecy desc
                tag_list += [(k,v) for (k,v) in counter_ref.most_common()]
                if not left:
                    tag_list += [(zero_key, 0) for zero_key in bf_key if zero_key not in af_key]
            case 1: # frequency Asc
                if not left:
                    tag_list += [(zero_key, 0) for zero_key in bf_key if zero_key not in af_key]
                tag_list += list(reversed([(k,v) for (k,v) in counter_ref.most_common()]))
            case 2: # Alphabetical Desc
                if left:
                    tag_list += sorted(counter_ref.items())
                else:
                    tag_list += sorted([(k, counter_ref[k]) for k in bf_key])
            case 3: # Alphabetical Asc
                if left:
                    tag_list += sorted(counter_ref.items(), reverse=True)
                else:
                    tag_list += sorted([(k, counter_ref[k]) for k in bf_key], reverse=True)
                    
            case 4: # by grouping
                # first sort by Alphabetical order
                from resources import tag_categories
                TAG_CATEGORIES = tag_categories.TAG_CATEGORIES
                grouping=True
                tag_keys = counter_ref.keys()
                temp_sorted_tags = sorted(counter_ref.items())
                completed_tags = []
                 # sort main and subcategory by alphabetical order 
                for main_category, values in sorted(TAG_CATEGORIES.items()):
                    for sub_category, details in sorted(values.items()):
                        for tag in details["tags"] + details["low"] + details["high"]:
                            if tag in tag_keys: # we show the main category and subcategory and the tags
                                tag_list.append((", ".join([main_category, sub_category, tag]), counter_ref[tag]))
                                completed_tags.append(tag)
                tag_list+=[kv_pair for kv_pair in temp_sorted_tags if kv_pair[0] not in completed_tags] 
            case 5: # by token length
                from clip import tokenize
                tag_keys = list(counter_ref.keys())
                known_text = tokenize(tag_keys, context_length=77)
                token_dict = {}
                for tag, tokens in zip(tag_keys, known_text):
                    token_dict[tag] = len([int(tk) for tk in tokens[tokens.nonzero()[1:-1]]])
                
                tag_list += sorted(token_dict.items(), key=lambda item: item[1], reverse=True)
            
        self.show_visual_list(tag_list, grouping=grouping, left=left)
      
    @Slot()
    def clean_tags(self):
        remove_arching_set = self.checkBox_use_tag_csv.isChecked()
        filter_bows = self.checkBox_filter_bow.isChecked()
        replace_symbolic_tags = self.checkBox_symbolic_tag.isChecked()
        extra_solo_checks = self.checkBox_solo_check.isChecked()
        filter_special = self.checkBox_filter_special.isChecked()
        filter_phrases = self.lineEdit_filter_phrase.text()
        agg_act_thresh = int(self.slider_activation_thresh.value()) # default is 100
        agg_prob_thresh = float(self.slider_prob_thresh.value())/100 # default is 60%

        parameters.log.info(f"Using {agg_act_thresh} for tag threshold and {agg_prob_thresh} for prob threshold for any aggresive filter")

        if self.filtered_view:
            filter_phrases = filter_phrases.split(",")
        parameters.log.info("Cleaning up tags")
        def filter_for_colors(tags, auto_tags, multicolor, check_thresh, check_rare):
            bad_tags = []
            # exit if hair is allowed to be multicolored
            for mulcol in multicolor:
                if mulcol in tags:
                    return bad_tags
            # except for the highest threshold colored tag, put it into bad
            bad_tags += [t for i, t in enumerate([x[0] for x in auto_tags if x[0] in check_thresh]) if i]
            # keep the rare colored tags and put the regular one in the bad category
            for (base_tag, rare_tag) in check_rare:
                if base_tag in tags and rare_tag in tags:
                    bad_tags.append(base_tag)
            return bad_tags
        
        underwear_prefix = ["bow", "lace-trimmed", "frilled", "vertical-striped", "striped", "diagonal-striped"] + self.only_color
        underwear_check = len(underwear_prefix)
        x_panties = [x + " panties" for x in underwear_prefix]
        x_bra = [x + " bra" for x in underwear_prefix]
        x_underwear = [x + " underwear" for x in underwear_prefix]
        x_background = [x + " background" for x in self.only_color]
        
        only_color = ["red", "blue", "green", "black", "white", "grey", "gray", "blonde", "brown", "orange", "pink"]
        rare_color_pair = [("green", "light green"), ("blue", "aqua"), ("purple", "light purple"), 
                           ("brown", "light brown"), ("blue", "dark blue"), ("green", "aqua")]
        multicolor_hair = ["striped hair","rainbow hair","multicolored hair", "two-tone hair", 
                           "gradient hair","streaked hair", "colored inner hair"]
        multicolor_eyes = ["multicolored eyes","extra eyes","gradient eyes",
                           "two-tone eyes", "rainbow eyes", "heterochromia"]
        potential_hair_tags = [c + " hair" for c in only_color]
        rare_hair_tags = [(a[0] + " hair", a[1]+ " hair") for a in rare_color_pair]
        potential_eye_tags = [c + " eyes" for c in only_color]
        rare_eye_tags = [(a[0] + " eyes", a[1]+ " eyes") for a in rare_color_pair]
        
        # these are used to condense tags in imgs with absurdly large token counts > 200
        bukkake_tags = ["cum on body", "cum on breasts", "cum on hair", "cum on face", "cum on ass", "cum on stomach", "cum on legs", "cum on arms", "cum on clothes"]
        cum_drip_tags = ["cum in pussy", "overflow"]
        only_colors = ["red", "blue", "green", "black", "white", "gray", "grey", "brown", "pink", "orange", "yellow","purple", "aqua"]
        clothes_removal_general = ["dress", "shirt", "skirt", "gloves", "kimono", "thighhighs", "jacket", "coat", "pants", "bow", 
                                   "ribbon", "bowtie", "leotard", "apron", "vest"]
        clothes_full_removal_general = ["headwear", "footwear"]
        remove_matching_body = ["bare shoulders", "collarbone", "midriff", "stomach", "looking at viewer", "cleavage", "thighs", "navel", "armpits", "breasts out"]
        remove_partial_matching = ["sleeves"]
        clothes_removal_category = [set(make_combination(only_colors, [cloth])[0]) for cloth in clothes_removal_general]
        clothes_full_removal_category = [set(make_combination(only_colors, [cloth])[0]) for cloth in clothes_full_removal_general]
        clothes_match_remove = ["hair ornament"]
        # both girl and boys
        animal_girl_type = ["fox", "dog", "wolf", "cat", "tiger", "rabbit", "dragon"]
        animal_girls = [ag + " girl" for ag in animal_girl_type] + [ag + " boy" for ag in animal_girl_type]
        animal_girls_parts = [[animal + p for p in [" tail", " ears"]] for animal in animal_girl_type] +  [[animal + p for p in [" tail", " ears"]] for animal in animal_girl_type]
        
        manual_counter = Counter()
        simplify_uniform = True
        tag_lengths = []
        # check for global threshold
        img_count = len(self.temp_database.images)
        
        group_name = self.comboBox_filterGroups.currentText()
        
        if isinstance(self.temp_database, Database):
            self.tags_after = Counter()
            self.temp_database.tokenize_all_images()
            for img in self.temp_database.images:
                use_img = True
                img.secondary_rejected_tags = []
                #img.secondary_rejected_tags = [t for t in img.secondary_rejected_tags if t not in self.blacklist]
                full_tags = img.get_full_tags()
                full_tag_len = len(full_tags)
                tags = full_tags + img.rejected_tags
                
                
                if self.filtered_view: #early skip based on condition
                    if not (all([phrase in tags for phrase in filter_phrases])):
                        use_img = False
                
                if use_img:
                    # filter logics
                    filtered_tags = []
                    if filter_special:
                        #filtered_tags += [t for t in tags if t in self.blacklist]
                        if "back tattoo" in tags and not any([a in tags for a in ["from behind", "back", "nape", "on stomach"]]):
                            filtered_tags.append("back tattoo")
                        if "realistic" in tags and "3d" not in tags:
                            img.append_secondary_tags(["3d"])
                        if "very dark skin" in tags and "dark-skinned male" in tags and "dark-skinned female" not in tags:
                            filtered_tags+=["very dark skin"] 
                        for series in SERIES_BLACKLIST:
                            filtered_tags += [t for t in tags if series in t and t not in SERIES_EXCEPTION_SET]
                        if "ganguro" in tags:
                            kv_conflicts = img.get_unresolved_conflicts()
                            ganguro_manual = []
                            
                            # multi-colored hair:
                            mc_hair = "multi-colored hair"
                            if "HAIR MULTICOLOR" in kv_conflicts and mc_hair in kv_conflicts["HAIR MULTICOLOR"]:
                                ganguro_manual.append(mc_hair)
                                filtered_tags += [t for t in kv_conflicts["HAIR MULTICOLOR"] if t != mc_hair]
                        
                            if "nose ring" in tags:
                                ganguro_manual.append("nose ring")
                            if "nose piercing" in tags:
                                ganguro_manual.append("nose piercing")
                            img.append_secondary_tags(ganguro_manual)
                        if full_tag_len > 65:
                            if "open mouth" in tags and "tongue out" in tags and "tongue" in tags:
                                filtered_tags.append("tongue")
                            # check for mergable underwear
                            for i in range(underwear_check):
                                if x_panties[i] in tags and x_bra[i] in tags:
                                    parameters.log.info((x_panties[i], x_bra[i], x_underwear[i]))
                                    filtered_tags += [x_panties[i], x_bra[i]]
                                    img.append_secondary_tags([x_underwear[i]])
                            
                            for background in x_background:
                                if background in tags and "simple background" in tags:
                                    filtered_tags.append("simple background")
                        
                        if full_tag_len > agg_act_thresh and img.full_tags_token_length > 210:
                            if "multiple girls" in tags or "multiple boys" in tags: # remove hair and eye color for multiple chars
                                filtered_tags += [t for t in tags if t in potential_hair_tags]
                                filtered_tags += [t for t in tags if t in potential_eye_tags]
                            else: # 1 or 2 characters
                                pass
                                
                            # remove tags under threshold
                            sorted_tags = [v for v in img.auto_tags if v[0] in full_tags and v[0] not in filtered_tags]
                            sorted(sorted_tags, key=lambda x: x[1], reverse=True)
                            if len(sorted_tags)> agg_act_thresh and img.full_tags_token_length > 210:
                                to_removed = sorted_tags[agg_act_thresh:]
                                filtered_tags += [v[0] for v in to_removed]
                            
                            
                            #filtered_tags += [v[0] for v in img.auto_tags if v[1] > agg_prob_thresh]
                                
                        if img.full_tags_token_length > 210 or full_tag_len > min(70, agg_act_thresh):
                            # condense cum tags
                            if "bukkake" in tags:
                                filtered_tags+= [t for t in tags if t in bukkake_tags]
                            if "cumdrip" in tags:
                                filtered_tags+= [t for t in tags if t in cum_drip_tags]
                            if True:#"multiple girls" in tags or "multiple boys" in tags: # remove colored clothes for imgs with a lot of characters
                                add_in = []
                                
                                filtered_tags += [bp for bp in remove_matching_body if bp in tags]
                                
                                filtered_tags += [t for pm in remove_partial_matching for t in tags if pm in t]
                                
                                # simplifies animal girls if it exists
                                for ag, ag_parts in zip(animal_girls, animal_girls_parts):
                                    if ag in tags:
                                        removed_parts = [p for p in ag_parts if p in full_tags]
                                        filtered_tags += removed_parts
                                
                                # this downgrades all with matching string
                                for gen_t in clothes_match_remove:
                                    filtered_tags += [t for t in full_tags if gen_t in t]
                                    add_in.append(gen_t)
                                
                                for general_tag, category in zip(clothes_removal_general, clothes_removal_category):
                                    filtered_clothes = [t for t in full_tags if t in category]
                                    if filtered_clothes:
                                        add_in.append(general_tag)
                                    filtered_tags += filtered_clothes
                                    
                                for category in clothes_full_removal_category: # remove colored headwear and footwear
                                    filtered_tags += [t for t in full_tags if t in category]
                                    
                                img.append_manual_tags(add_in)
                                
                        if ("kogal" in tags) and ("ganguro" not in tags) and ("school uniform" not in tags):
                            # remove kogal
                            filtered_tags.append("kogal")
                        if "2girls" in full_tags and "multiple girls" in full_tags and ("3girls" not in tags or "4girls" not in tags or "5girls" not in tags or "6+girls" not in tags):
                            filtered_tags.append("multiple girls")
                            
                        if "2boys" in full_tags and "multiple boys" in full_tags and ("3boys" not in tags or "4boys" not in tags):
                            filtered_tags.append("multiple boys")
                        
                        
                        manual_append = [ftag for fname, ftag in zip(file_phrase, secondary_tag) if fname in os.path.basename(img.path)]
                        manual_counter.update(manual_append)
                        img.append_secondary_tags(manual_append)
                    if remove_arching_set:
                        filtered_tags += filter_tags(tags, self.sub_categ, self.base_categ)
                        filtered_tags += filter_tags(tags, self.keeptags, self.removetags)
                    if extra_solo_checks:
                        # second check that it's only 1 person or thing
                        if "solo" in tags and 1 == sum([a in tags for a in ["1girl", "1boy", "1other"]]):
                            auto_tags = [t for t in self.get_tags_sorted_thresh(img)]
                            filtered_tags += filter_for_colors(tags, auto_tags, multicolor_hair, potential_hair_tags, rare_hair_tags)
                            filtered_tags += filter_for_colors(tags, auto_tags, multicolor_eyes, potential_eye_tags, rare_eye_tags)
                        if "solo" in tags and "male focus" in tags and "1boy" not in tags:
                            filtered_tags.append("male focus")
                    if filter_bows:
                        filtered_tags += filter_tags(tags, self.bow_keep, self.bow_remove)
                    if replace_symbolic_tags:
                        emoji_tags = [t for t in tags if t in self.emoji.keys()]
                        add_to_tags = []
                        for emoji in emoji_tags:
                            for additional_tag in self.emoji[emoji]:
                                if additional_tag not in tags:
                                    add_to_tags.append(additional_tag)
                        img.append_secondary_tags(add_to_tags)
                        filtered_tags += emoji_tags
                    if simplify_uniform:
                        #filtered_tags += [t for t in tags if (len(t) > 3 and "uniform" in t)]
                        filtered_tags += [t for t in tags if (t != "school uniform" and "school uniform" in t)]
                        filtered_tags += [t for t in tags if (t != "military uniform" and "military uniform" in t)]
                    img.append_secondary_rejected(filtered_tags)
                    img.update_review_tags()
                    
                    tags = img.get_full_tags()
                    if self.filtered_view:
                        if all([phrase in tags for phrase in filter_phrases]):
                            tag_lengths.append(len(tags))
                            self.tags_after.update(tags)
                            for group_name in img.group_names:
                                self.after_group_counters[group_name].update(tags)
                    else:
                        tag_lengths.append(len(tags))
                        self.tags_after.update(tags)
                        for group_name in img.group_names:
                            self.after_group_counters[group_name].update(tags)

            self.second_list = True
            self.after_max_len = max(tag_lengths) if tag_lengths else 0
            self.sort_visual_list(self.tags_before, left=True)
            self.sort_visual_list(self.tags_after, left=False)
            self.update_dataset_counter()
            parameters.log.info("Dataset cleaned")
            for k, v in manual_counter.most_common():
                parameters.log.info(f"Manually added: {k}, {v}")
            def get_statistics(tag_lengths):
                tag_series = pd.Series(tag_lengths)
                parameters.log.info("Printing statistics for new tags, tag count > 75 is iffy")
                parameters.log.info(tag_series.describe())
            get_statistics(tag_lengths)

        else:
            parameters.log.error("No valid database loaded, skipping opperations.")          
