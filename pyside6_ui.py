import os
import sys

os.environ["XFORMERS_FORCE_DISABLE_TRITON"] = "1"
def _ignore_xformers_triton_message_on_windows():
    import logging
    logging.getLogger("xformers").addFilter(
        lambda record: 'triton is not available' not in record.getMessage())
    # the following didn't work, but it's the right warning message
    class TritonFilter(logging.Filter):
        def filter(self, record):
            if record.levelname == 'WARNING' and "Triton is not available, some optimizations will not be enabled." in record.getMessage():
                return False
            return True
    #logger = logging.getLogger("xformers")
    #logger.addFilter(TritonFilter())
# In order to be effective, this needs to happen before anything could possibly import xformers.
_ignore_xformers_triton_message_on_windows()

import DatabaseCreationView
from classes.class_elements import GroupElement

import concurrent.futures
import time

import CustomWidgets
from resources import parameters, tag_categories
tag_categories.check_categories()

import GlobalDatabaseView
import DatasetCleaning
import StatisticsTab
import DatabaseViewBase
import ImageTools
from interfaces import interface
from tools import files, safetensors_metadata

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont

from classes.class_database import Database
import qdarkstyle
#tag_categories.check_definitions_and_recommendations()

class AddTags(QMainWindow, interface.Ui_MainWindow):
    def __init__(self):
        super(AddTags, self).__init__()
        self.setupUi(self)

        #with open("metadata.txt", 'w') as file:
        #    file.write(','.join([x for x in tag_categories.METADATA_TAGS.keys()]))

        #############################
        # PRE INIT
        self.basic_database: Database = None
        self.checkpoint_database: Database = None

        #############################
        # Setup Output

        self.widget_to_output.createTxtFiles.connect(self.create_txt_files_button)
        self.widget_to_output.createJsonTagFile.connect(self.create_meta_cap_button)
        self.widget_to_output.createSampleToml.connect(self.create_sample_toml_button)
        self.widget_to_output.createJsonLFile.connect(self.create_jsonL)

        self.widget_to_output.editedMainTriggerTag.connect(self.update_main_trigger_tags)
        self.widget_to_output.editedSecondaryTriggerTag.connect(self.update_secondary_trigger_tags)

        #############################
        # DATABASE TOOLS

        # TOP BAR:
        self.pushButton_load_database.clicked.connect(self.load_database_button)
        self.pushButton_open_path_edit.clicked.connect(self.open_path_edit_button)
        self.pushButton_save_database.clicked.connect(self.save_database_button)

        # LEFT:
        
        # Preprocessing tools
        self.pushButton_convert_images_to_png.clicked.connect(self.convert_images_to_png_button)
        self.pushButton_rename_images_md5.clicked.connect(self.rename_images_md5_button)
        
        # Database validation tools
        self.pushButton_images_existence.clicked.connect(self.images_existence_button)
        self.pushButton_filter_images.clicked.connect(self.filter_images_button)
        self.pushButton_reautotags.clicked.connect(self.reautotags_button)
        self.pushButton_rescores.clicked.connect(self.rescore_button)
        self.pushButton_reclassify.clicked.connect(self.reclassify_button)
        self.pushButton_rehash.clicked.connect(self.rehash_button)
        self.pushButton_redetect_person.clicked.connect(self.redetect_person)
        self.pushButton_redetect_head.clicked.connect(self.redetect_head)
        self.pushButton_redetect_hand.clicked.connect(self.redetect_hand)
        
        # Group Management Tools
        self.pushButton_move_files_groupings.clicked.connect(self.move_files_groupings_button)
        self.pushButton_rebuild_groups.clicked.connect(self.rebuild_groups_button)
        
        self.pushButton_load_and_merge_secondary.clicked.connect(self.merge_secondary_database)
        
        # RIGHT:
        self.pushButton_print_unknown_tags.clicked.connect(self.print_unknown_tags_button)
        

        # checkpoint and misc TOOLS TAB
        self.pushButton_rename_all.clicked.connect(self.rename_bad_names_to_md5)
        self.pushButton_open_path_tools.clicked.connect(self.open_path_tools_button)
        self.pushButton_export_npz.clicked.connect(self.export_for_checkpoint)
        
        
        self.pushButton_open_safetensor.clicked.connect(self.open_path_safetensor_button)
        self.pushButton_inspect_safetensor.clicked.connect(self.inspect_safetensor)
        self.pushButton_remove_files_button.clicked.connect(self.remove_file_type)

        #############################
        # DATABASE CREATION TAB
        self.database_creation_tab = DatabaseCreationView.DatabaseCreationView()
        self.tabWidget_2.insertTab(0, self.database_creation_tab, "Database Creation Tool")
        self.tabWidget_2.setCurrentIndex(0)

        #############################
        # VIEW DATABASE TAB
        self.pushButton_view_database.clicked.connect(self.view_database_button)
        self.pushButton_open_view_database_path.clicked.connect(self.open_view_database_path_button)
        self.databaseTabWidget.tabCloseRequested.connect(self.view_database_close_requested)


        ##############################
        # DATASET CLEANING TAB
        self.dataset_cleaning_tab = DatasetCleaning.DatasetCleaningView()
        self.tabWidget.insertTab(2, self.dataset_cleaning_tab, "Dataset Cleaning")

        ##############################
        # GLOBAL DATASET TAB
        self.global_dataset_tab = GlobalDatabaseView.GlobalDatabaseFrame()
        self.tabWidget.insertTab(3, self.global_dataset_tab, "Global Database")

        #############################
        # LORA TOOLS

        ##############################
        # STATISTICS TAB
        self.statistics_tab = StatisticsTab.StatisticsView()
        self.tabWidget.insertTab(4, self.statistics_tab, "Statistics")

        ##############################
        # IMAGE TOOLS TAB
        self.image_tools_tab = ImageTools.ImageToolsView()
        self.tabWidget.insertTab(4, self.image_tools_tab, "Image Tools")

        #############################
        # SETTINGS TAB
        self.init_settings()



   
    # button functions used in multiple sections:
    @Slot()
    def open_path_edit_button(self):
        path = CustomWidgets.path_input_dialog(self)
        self.lineEdit_database_folder.setText(path)

    # Setup Output functions:
    @Slot()
    def create_txt_files_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        self.basic_database.create_txt_files(
            use_trigger_tags=self.widget_to_output.use_trigger_tags(),
            token_separator=self.widget_to_output.use_token_separator(),
            use_aesthetic_score=self.widget_to_output.use_aesthetic_score(),
            use_sentence=self.widget_to_output.use_sentence(),
            sentence_in_trigger=self.widget_to_output.use_sentence_in_token_separator(),
            remove_tags_in_sentence=self.widget_to_output.remove_tag_in_sentence(),
            score_trigger=self.widget_to_output.use_aesthetic_score_in_token_separator(),
            shuffle_tags=self.widget_to_output.shuffle_tags()
            )

    @Slot()
    def create_meta_cap_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        self.basic_database.create_json_file(
            use_trigger_tags=self.widget_to_output.use_trigger_tags(),
            token_separator=self.widget_to_output.use_token_separator(),
            use_aesthetic_score=self.widget_to_output.use_aesthetic_score(),
            use_sentence=self.widget_to_output.use_sentence(),
            sentence_in_trigger=self.widget_to_output.use_sentence_in_token_separator(),
            remove_tags_in_sentence=self.widget_to_output.remove_tag_in_sentence(),
            score_trigger=self.widget_to_output.use_aesthetic_score_in_token_separator(),
            shuffle_tags=self.widget_to_output.shuffle_tags()
            )

    @Slot()
    def create_sample_toml_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        selected_resolution = self.widget_to_output.toml_resolution()
        resolution_dict = {
      		"SDXL":	(1024, 1024, 64), 
			"SD1.5":(768, 768, 64), 
			"SD1.0":(512,512, 64), 
			"Custom":(parameters.PARAMETERS['custom_export_width'], 
						parameters.PARAMETERS['custom_export_height'], 
						parameters.PARAMETERS['custom_export_bucket_steps'])
        }
        if selected_resolution in resolution_dict:
            res_info = resolution_dict[selected_resolution]
        else:
            parameters.log.error("Resolution string not found")
            res_info = resolution_dict["SDXL"]

        self.basic_database.create_sample_toml(res_info[0], res_info[1], res_info[2])    

    @Slot()
    def create_jsonL(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        self.basic_database.create_jsonL_file(
            use_trigger_tags=self.widget_to_output.use_trigger_tags(),
            token_separator=self.widget_to_output.use_token_separator(),
            use_aesthetic_score=self.widget_to_output.use_aesthetic_score(),
            use_sentence=self.widget_to_output.use_sentence(),
            sentence_in_trigger=self.widget_to_output.use_sentence_in_token_separator(),
            remove_tags_in_sentence=self.widget_to_output.remove_tag_in_sentence(),
            score_trigger=self.widget_to_output.use_aesthetic_score_in_token_separator(),
            shuffle_tags=self.widget_to_output.shuffle_tags()
            )

    @Slot(str)
    def update_main_trigger_tags(self, text: str):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        tags = [tag.strip() for tag in text.split(",")]
        self.basic_database.trigger_tags["main_tags"] = tags

    @Slot(str)
    def update_secondary_trigger_tags(self, text: str):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        tags = [tag.strip() for tag in text.split(",")]
        self.basic_database.trigger_tags["secondary_tags"] = tags

    #############################
    # DATABASE TOOLS
    # TOP BAR button functions:
    @Slot()
    def load_database_button(self):
        if not os.path.exists(os.path.join(self.lineEdit_database_folder.text(), parameters.DATABASE_FILE_NAME)):
            parameters.log.error(f"Database doesn't exist in {self.lineEdit_database_folder.text()}")
            return
        parameters.log.info("Loading Database")
        self.basic_database = Database(self.lineEdit_database_folder.text())
        self.widget_to_output.set_trigger_tags(", ".join(self.basic_database.trigger_tags["main_tags"]), ", ".join(self.basic_database.trigger_tags["secondary_tags"]))
        parameters.log.info(f"Loaded Database with {len(self.basic_database.images)} images")
    
    @Slot()
    def save_database_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        self.basic_database.save_database()
    
    # LEFT:  
    # Preprocessing tools
    @Slot()
    def convert_images_to_png_button(self,*, folder: str="", images_paths: list[str]=None) -> bool:
        if images_paths:
            parameters.log.info("Converting images to .png format")
            start_time = time.time()
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
            files.to_png_from_images_paths(images_paths, pool)
            pool.shutdown(wait=True)
            parameters.log.info(f"Images converted to png in {round(time.time() - start_time, 3)} seconds")
            return True
        if not folder:
            folder = self.lineEdit_database_folder.text()
        if not os.path.isdir(folder):
            parameters.log.info(("Invalid folder path: ",folder))
            return False
        parameters.log.info("Converting images to .png format")
        start_time = time.time()
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
        files.to_png(folder, pool)
        pool.shutdown(wait=True)
        parameters.log.info(f"Images converted to png in {round(time.time() - start_time, 3)} seconds")
        return True

    @Slot()
    def rename_images_md5_button(self,*, folder: str="") -> bool:
        if not folder:
            folder = self.lineEdit_database_folder.text()
        if not os.path.isdir(folder):
            parameters.log.error(("Invalid folder path: ",folder))
            return False
        parameters.log.info("Converting images to MD5 filename.")
        start_time = time.time()
        files.to_md5(folder)
        parameters.log.info(f"Images converted to md5 filename in {round(time.time() - start_time, 3)} seconds")
        return True

    # Database validation tools
    @Slot()
    def images_existence_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        parameters.log.info("checking image existance, updating path if necessaryß")
        self.basic_database.check_existence_images()

    @Slot()
    def filter_images_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.filter_all()

    @Slot()
    def reautotags_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.re_call_models(tag_images=True)

    @Slot()
    def rescore_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.re_call_models(score_images=True)

    @Slot()
    def reclassify_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.re_call_models(classify_images=True)

    @Slot()
    def rehash_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.reapply_md5()
        parameters.log.info("Updated MD5 of images")

    @Slot()
    def redetect_person(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.re_call_models(detect_people=True)
    
    @Slot()
    def redetect_head(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.re_call_models(detect_head=True)

    @Slot()
    def redetect_hand(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.re_call_models(detect_hand=True)

    # Group Management Tools
    @Slot()
    def move_files_groupings_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.organise_image_paths_groups()

    @Slot()
    def rebuild_groups_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.remove_groups()
        self.basic_database.add_image_to_groups_by_path([x.path for x in self.basic_database.images])
        parameters.log.info("Groups are rebuilt based on the path")

    def merge_secondary_database(self): # load and merge database method
        # load old db and transfer data for files with matching md5
        
        db_path = self.lineEdit_secondary_db_folder.text().strip()
        parameters.log.info("Loading and transfering tags from secondary database")
        # check for any errors:
        if not self.basic_database:
            parameters.log.error("No Primary database loaded")
            return
        elif not db_path:
            parameters.log.error("No secondary database location entered")
            return
        elif not files.check_database_exist(db_path):
            parameters.log.error("Secondary database location doesn't have a database file") 
            return
        
        # we passed the errors and load secondary db and start the tag transfer
        sec_db = Database(db_path)
        update_counter = 0
        sec_md5s = [img.md5 for img in sec_db.images]
        
        # notify user if secondary database has trigger tags that they might want to know.
        if sec_db.trigger_tags["main_tags"] or sec_db.trigger_tags["secondary_tags"]:
            parameters.log.info("Secondary database had the following trigger tags, but they're merged as regular tags, update primary database's trigger tags if needed")
            parameters.log.info(f"PRIMARY: {sec_db.trigger_tags['main_tags']}, SECONDARY: {sec_db.trigger_tags['secondary_tags']}")
            

        primary_md5 = [img.md5 for img in self.basic_database.images]
        md5_intersect = set(primary_md5).intersection(set(sec_md5s))
        
        # make a set of md5s preassigned in a group and use it to see if we need to add it to a new group
        md5_preassigned_to_group = []
        if self.basic_database.groups:
            # check if primary db has the database and get a list of md5s that has a group
            for group_name, group_content in self.basic_database.groups.items():
                md5_preassigned_to_group += [md5_hash for md5_hash in group_content.md5s if md5_hash in md5_intersect]
        md5_preassigned_to_group = set(md5_preassigned_to_group) # making a set for faster check
        md5_not_assigned = [m for m in md5_intersect if m not in md5_preassigned_to_group]
        
        if md5_not_assigned and sec_db.groups: # if any md5 is unassigned and groups exists in secondary db
            for group_name, group_content in sec_db.groups.items():
                if group_content.md5s: #check if this secondary group is not empty
                    
                    if not group_name in self.basic_database.groups.keys(): # check if the group name exists
                        self.basic_database.groups[group_name] =  GroupElement(group_name=group_name)
                        
                    self.basic_database.groups[group_name].md5s += [m for m in group_content.md5s if m in md5_not_assigned]
             
        if md5_intersect:
            parameters.log.info(f"starting tag transfering for {len(md5_intersect)}")
        # loop for transfering content one by one
        for md5 in md5_intersect:
            
            # find the two indexes that have matching md5
            i = self.basic_database.index_of_image_by_md5(md5)
            sec_i = sec_db.index_of_image_by_md5(md5)
            
            # How the merge/export works: 
            # before overwriting, save some values we might want to keep in temp variables
            # then load the image data_dict that stores all the img data from secondary to primary, 
            # then overwrite specific sections, like path, from the temp variable back into primary
            
            # temp variable that might be need overwriting
            primary_full_path = self.basic_database.images[i].path
            
            primary_score_value = self.basic_database.images[i].score_value
            primary_score_label = self.basic_database.images[i].score_label
            primary_class_value = self.basic_database.images[i].classify_label
            primary_class_label = self.basic_database.images[i].classify_value
            primary_completeness_label = self.basic_database.images[i].completeness_label
            primary_completeness_value = self.basic_database.images[i].completeness_value
          
            # temp original md5 and bool if it's the same with the base md5
            primary_original_md5 = self.basic_database.images[i].original_md5
            primary_two_md5 = self.basic_database.images[i].md5 != primary_original_md5
            
            data_dict = sec_db.images[sec_i].get_saving_dict()
            #print(data_dict)
            # update non-tags
            self.basic_database.images[i].init_image_dict(data_dict)
            
            # at this stage basic database has the new values from the secondary database
            
            # update path
            self.basic_database.images[i].path = primary_full_path
         
            # update score if necessary
            sec_score_value = self.basic_database.images[i].score_value
            if ((primary_score_label and not self.basic_database.images[i].score_label) or 
                (sec_score_value > primary_score_value and 1 >= primary_score_value > 0)):
                # if secondary doesn't have scores, use primary's scores
                # OR
                # lecagy, use the score that has the new values [0~1] if found
                self.basic_database.images[i].score_label = primary_score_label
                self.basic_database.images[i].score_value = primary_score_value
            
            # update class label if necessary 
            if primary_class_label and not self.basic_database.images[i].classify_label:
                self.basic_database.images[i].classify_label = primary_class_value
                self.basic_database.images[i].classify_value = primary_class_label 

            if primary_completeness_label and not self.basic_database.image[i].completeness_label:
                self.basic_database.images[i].completeness_label = primary_completeness_label
                self.basic_database.images[i].completeness_value = primary_completeness_value
                
            # update md5 if necessary, very rare, but if primary has older md5 and secondary doesn't have older md5
            if primary_two_md5 and self.basic_database.images[i].original_md5 == self.basic_database.images[i].md5:
                self.basic_database.images[i].original_md5 = primary_original_md5
            else:
                pass
                # ignore the case if both primary and secondary have md5 != original_md5 because 
                # there's no way of knowing which is the original. So we assume the secondary, which
                # is intended to be the older database, to have the true original
     
            
            update_counter+=1
        
        parameters.log.info(f"Updated {update_counter} images in primary database from secondary database")

    # RIGHT:
    @Slot()
    def print_unknown_tags_button(self):
        unk_tags = []
        known_tags = set(tag_categories.COLOR_DICT.keys()).union(tag_categories.REJECTED_TAGS)

        import numpy as np
        from resources.tag_categories import KAOMOJI

        
        #ca_dict = files.get_caformer_tags()
        
        #ca_list = [ca_dict[str(k)].replace("_", " ") if len(ca_dict[str(k)]) > 3 else ca_dict[str(k)] for k in
        #           range(12546 + 1)]
        #ca_list = [ca for ca in ca_list if ca not in known_tags]
        #ca_set = set(ca_list)
        
        
        tags_df = files.get_pd_swinbooru_tag_frequency()
        
        tags_df = tags_df.sort_values(by=['count'], ascending=False)
        name_series = tags_df["name"]
        name_series = name_series.map(lambda x: x.replace("_", " ") if len(x) > 3 and x not in KAOMOJI else x)
        tag_names = name_series.tolist()
        general_indexes = list(np.where(tags_df["category"] == 0)[0])
        general_tag = [tag_names[i] for i in general_indexes]
        gt_list = [gt for gt in general_tag if gt not in known_tags]

        #parameters.log.info(", ".join(ca_list))
        #parameters.log.info(", ".join([gt for gt in gt_list if gt not in ca_set]))

        if self.basic_database:
            for image in self.basic_database.images:
                for tag in image.get_full_tags():
                    if tag not in known_tags and tag not in unk_tags:
                        unk_tags.append(tag)
            parameters.log.info(unk_tags)

    # checkpoint and misc TOOLS TAB
    def rename_bad_names_to_md5(self):
        confirmation = CustomWidgets.confirmation_dialog(self, text="Do you wish to convert all file names to their MD5 Hash (and update related json)?\nMake sure MD5 didn't update")
        db_folder = self.lineEdit_database_folder.text()
        db_exists = os.path.exists(os.path.join(db_folder, parameters.DATABASE_FILE_NAME))
        if not db_exists:
            parameters.log.error("No database found, exiting procedure")
        if confirmation and db_exists:
            #files.to_md5(db_folder)
            if not self.checkpoint_database:
                self.checkpoint_database = Database(db_folder)
            else: #if a different database is in the textfield
                if self.checkpoint_database.folder != db_folder:
                    parameters.log.info("Using database in the text field")
                    self.checkpoint_database = Database(db_folder)
            
            def has_special_char(text: str) -> bool: # this checks for non alpha numeric and ignores whitespace
                return any(char for char in text if not (char.isascii() and (char.isalnum() or char in "_-( )")))
            
            renamed_pair = []
            for img_path in self.checkpoint_database.get_all_paths():
                # get directory, filename, and img extension
                dir_name = os.path.dirname(img_path)
                f_name, f_ext = os.path.splitext(os.path.basename(img_path))
                sp_char = has_special_char(f_name)
                if sp_char:
                    md5_hash = files.get_md5(img_path)
                    old_dir_f_name = os.path.join(dir_name, f_name)
                    new_dir_f_name = os.path.join(dir_name, md5_hash)
                    parameters.log.info((sp_char, img_path))
                    
                    db_i = self.checkpoint_database.index_of_image_by_image_path(img_path)
                    old_path = old_dir_f_name+f_ext
                    new_path = new_dir_f_name+f_ext
                    
                    self.checkpoint_database.images[db_i].path = new_path
                
                    # update file
                    os.rename(old_path, new_path)
                    
                    # update npz (only if in same directory)
                    if os.path.exists(old_dir_f_name+".npz"):
                        os.rename(old_dir_f_name+".npz", new_dir_f_name+".npz")
                    
                    # update txt file (only if in same directory)
                    if os.path.exists(old_dir_f_name+".txt"):
                        os.rename(old_dir_f_name+".txt", new_dir_f_name+".txt")
                    
                    renamed_pair.append((old_path, new_path))
            
            if True: # if any file names were updated, save db and update other json
                self.checkpoint_database.save_database()
                import json
                
                def update_kohya_json(renamed_pair, json_path):
                    if os.path.exists(json_path):
                        parameters.log.info(f"Modifying filenames stored in {json_path}")
                        with open(json_path, 'r') as f:
                            old_db = json.load(f)
                        old_len = len(old_db)
                        bad_folder = 0
                        updated_db = {}
                        renamed_file_dict = dict(renamed_pair)
                        
                        old_keys = old_db.keys()
                        for old_k in old_keys:
                            if "DISCARDED" in old_k:
                                parameters.log.info(old_k)
                            if all(bad_folders not in old_k for bad_folders in parameters.PARAMETERS["discard_folder_name_from_search"]):
                                if old_k in renamed_file_dict:
                                    updated_db[renamed_file_dict[old_k]] = old_db[old_k]                     
                                else:
                                    updated_db[old_k] = old_db[old_k]
                            else:
                                bad_folder+=1

                        updated_len = len(updated_db)
                        if old_len!=updated_len:
                            parameters.log.error(f"Different output len {old_len} --> {updated_len}, diff {bad_folder}")
                        with open(json_path, 'w') as f:
                            json.dump(updated_db, f, indent=4)
                    else:
                        parameters.log.info(f"Skipping {json_path}")
                
                for json_name in ["meta_cap.json", "meta_lat.json"]:
                    update_kohya_json(renamed_pair, os.path.join(db_folder, json_name))

    @Slot()
    def open_path_tools_button(self):
        path = CustomWidgets.path_input_dialog(self)
        self.lineEdit_dataset_folder.setText(path)
                    
    def export_for_checkpoint(self):
        # used to convert dataset for paperspace
        default_name = "meta_lat.json"
        new_head_path = "dataset" # previously was ""
        export_for_linux = True
        db_dir = None
        if self.lineEdit_dataset_folder.text():
            parameters.log.info("No DB loaded, using path in text")
            db_dir = self.lineEdit_dataset_folder.text()
            if not os.path.exists(db_dir):
                parameters.log.error("Invalid path for exporting json")
                db_dir = None
        
        if db_dir:
            import json
            machine_type = "Linux" if export_for_linux else "Windows"
            parameters.log.info(f"Updating file structure in meta_lat to match a {machine_type} system.")
            json_path = os.path.join(db_dir, default_name)
            npz_paths = files.get_all_images_in_folder(db_dir, image_ext=".npz")
            current_head = db_dir
            if "\\" in current_head or "/" in current_head: # we only want the extreme end folder name
                current_head = os.path.split(current_head)[1] + "_npz"
            parameters.log.debug(npz_paths)
            npz_paths = [npz for npz in npz_paths if not current_head in npz]
            parameters.log.debug(npz_paths)
            files.export_images(npz_paths, db_dir, current_head)
            
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    old_db = json.load(f)
                
                
            db_dir_len = len(db_dir) 
            new_head = os.path.join(new_head_path, current_head)
            
            def convert_path(keys):
                if db_dir in keys:
                    new_path = keys[db_dir_len:]
                    if new_path[0] == "\\":
                        new_path = new_path[1:]
                    new_path = os.path.join(new_head, new_path)
                    parameters.log.debug(new_head, new_path)
                    if export_for_linux:
                        new_path = new_path.replace('\\', '/')
                    return new_path

                if export_for_linux:
                    keys = keys.replace('\\', '/')
                    if "\\notebook\\dataset" in keys: # this is to fix bad previous setups
                        keys = keys.replace("\\notebook\\dataset", "dataset")
                    elif "/notebook/dataset" in keys:
                        keys = keys.replace("/notebook/dataset", "dataset")
                return keys
                    
                    
            new_db = {}
            # update json here
            try:
                for keys in old_db.keys():
                    new_db[convert_path(keys)] = old_db[keys]
                
                with open(json_path, 'w') as f:
                    json.dump(new_db, f, indent=4)
            except Exception as e:
                parameters.log.exception("Didn't overwrite json, met an error", exc_info=e)
    
            parameters.log.info("Completed moving npz and updating json")
            
        else:
            parameters.log.error("No work for exporting for checkpoint")

    @Slot()
    def open_path_safetensor_button(self):
        path_tuple = CustomWidgets.file_input_dialog(self)
        path = path_tuple[0] # path tuple stores the file name and the selected option
        self.lineEdit_safetensor_path.setText(path)

    def inspect_safetensor(self):
        path = self.lineEdit_safetensor_path.text()
        if path and path.endswith(".safetensors"):
            safetensors_metadata.print_metadata2(path)
        else:
            parameters.log.error("No file found")
   
    def remove_file_type(self):
        ftypes = self.lineEdit_remove_files_type.text()
        ftype = [t.strip().lower() for t in ftypes.split(",")]
        accepted_values = [".txt", "txt", ".npz", "npz"]
        type_check = all([f in accepted_values for f in ftype])
        db_folder = self.lineEdit_dataset_folder.text().strip()
        
        # check for errors
        if not type_check:
            parameters.log.error(f"entered wrong values, we only accept the following values: {accepted_values}")
            return
        if not db_folder:
            parameters.log.error("no folder selected, enter a folder in the checkpoint section")
            return
        
        
        remove_files = []
        for f in ftype:
            if f in ["txt", ".txt"]:
                remove_files.extend(files.get_all_images_in_folder(db_folder, image_ext=(".txt")))
            elif f in [".npz", "npz"]:
                remove_files.extend(files.get_all_images_in_folder(db_folder, image_ext=(".npz")))
        
        if remove_files:
            message = f"This will delete {len(remove_files)} files, are you sure?"
            confirmation = CustomWidgets.confirmation_dialog(self, message)
            if confirmation:
                parameters.log.info(f"Deleting {len(remove_files)} files")
                for p in remove_files:
                    os.remove(p)
                parameters.log.info("Finished deleting files")
        else:
            parameters.log.error("No files to delete")
            
        
            
            
        
    # DATABASE CREATION TAB
    ###################
    # VIEW DATABASE TAB
    def add_db_tab_widget(self, db):
            main_widget = DatabaseViewBase.DatabaseViewBase(db)
            #main_widget = DatabaseTags.DatabaseFrame(db)
            self.databaseTabWidget.addTab(main_widget, db.folder)
    
    @Slot()
    def view_database_button(self):
        folder_path = self.lineEdit_view_database_path.text().strip()
        if not os.path.exists(os.path.join(folder_path,parameters.DATABASE_FILE_NAME)):
            parameters.log.warning("No valid path entered.")
            return False
        temp_db = Database(folder_path)
        temp_db.check_existence_images()
        self.add_db_tab_widget(temp_db)

    @Slot()
    def open_view_database_path_button(self):
        path = CustomWidgets.path_input_dialog(self)
        self.lineEdit_view_database_path.setText(path)
        self.view_database_button()

    @Slot(int)
    def view_database_close_requested(self, index):
        close_tab = self.databaseTabWidget.widget(index)
        self.databaseTabWidget.removeTab(index)
        close_tab.close()

    # Other tabs (DATASET CLEANING, GLOBAL DATASET, LORA, STATISTICS) ...
    
    # init settings code:
    @Slot()
    def init_settings(self):
        # remove wheel event
        list_of_widget_to_have_their_wheel_event_removed = [
            self.spin_font_size, self.spin_image_load_size, self.spin_swinv2_thresh, self.spin_swinv2_chara_thresh,
            self.spin_swinv2_chara_count, self.check_swinv2_chara, self.spin_caformer_thresh, self.spin_max_batch_size,
            self.spin_max_images_loader_thread, self.spin_max_4k_pixels_save_multiplier, self.spin_similarity_thresh,
            self.comboBox_click_option, self.spinBox_custom_height, self.spinBox_custom_width, self.spinBox_custom_bucket_steps,
            self.spinBox_sample_count, self.spin_max_amount_of_backups, self.spinBox_detection_resolution, self.spin_wdeva02_large_threshold
        ]
        for x in list_of_widget_to_have_their_wheel_event_removed:
            x.wheelEvent = lambda event: None
        
        self.spin_font_size.setValue(parameters.PARAMETERS["font_size"])
        self.lineEdit_external_image_editor_path.setText(parameters.PARAMETERS["external_image_editor_path"])
        self.spin_image_load_size.setValue(parameters.PARAMETERS["image_load_size"])
        self.lineEdit_automatic_tagger.setText(",".join([x.name for x in parameters.PARAMETERS["automatic_tagger"]]))
        self.spin_swinv2_thresh.setValue(parameters.PARAMETERS["swinv2_threshold"])
        self.spin_wdeva02_large_threshold.setValue(parameters.PARAMETERS["wdeva02_large_threshold"])
        self.spin_swinv2_chara_thresh.setValue(parameters.PARAMETERS["swinv2_character_threshold"])
        self.spin_swinv2_chara_count.setValue(parameters.PARAMETERS["swinv2_character_count_threshold"])
        self.check_swinv2_chara.setChecked(parameters.PARAMETERS["swinv2_enable_character"])
        self.checkBox_enable_image_tooltip.setChecked(parameters.PARAMETERS["database_view_tooltip"])
        self.checkBox_hide_sentence_in_view.setChecked(parameters.PARAMETERS["hide_sentence_in_view"])
        self.spin_caformer_thresh.setValue(parameters.PARAMETERS["caformer_threshold"])
        self.spin_max_batch_size.setValue(parameters.PARAMETERS["max_batch_size"])
        self.lineEdit_keep_token_tag_separator.setText(parameters.PARAMETERS["keep_token_tags_separator"])
        self.check_remove_transparency_from_images.setChecked(parameters.PARAMETERS["remove_transparency_from_images"])
        self.spin_max_images_loader_thread.setValue(parameters.PARAMETERS["max_images_loader_thread"])
        self.spin_max_4k_pixels_save_multiplier.setValue(parameters.PARAMETERS["max_4k_pixel_save_multiplier"])
        self.spin_max_amount_of_backups.setValue(parameters.PARAMETERS["max_databases_view_backup"])
        self.spin_similarity_thresh.setValue(parameters.PARAMETERS["similarity_threshold"])
        self.spinBox_detection_resolution.setValue(parameters.PARAMETERS["detection_small_resolution"])
        
        #self.comboBox_click_option.addItems(["Single Click", "Double Click"])
        self.comboBox_click_option.setCurrentText("Double Click" if parameters.PARAMETERS["double_click"] else "Single Click")

        self.check_filter_remove_characters.setChecked(parameters.PARAMETERS["filter_remove_characters"])
        self.check_filter_remove_metadata.setChecked(parameters.PARAMETERS["filter_remove_metadata"])
        self.check_filter_remove_series.setChecked(parameters.PARAMETERS["filter_remove_series"])
         
        # settings for custom toml creation
        self.spinBox_custom_height.setValue(parameters.PARAMETERS["custom_export_height"])
        self.spinBox_custom_width.setValue(parameters.PARAMETERS["custom_export_width"])
        self.spinBox_custom_bucket_steps.setValue(parameters.PARAMETERS["custom_export_bucket_steps"])
        self.spinBox_sample_count.setValue(parameters.PARAMETERS["toml_sample_max_count"])

        self.checkBox_load_images_thumbnail.setChecked(parameters.PARAMETERS["view_load_images"])
        self.checkBox_double_images_thumbnail_size.setChecked(parameters.PARAMETERS["doubling_image_thumbnail_max_size"])
        self.check_deactivate_filter.setChecked(parameters.PARAMETERS["deactivate_filter"])
        self.checkBox_activate_danbooru_tag_wiki_lookup.setChecked(parameters.PARAMETERS["danbooru_tag_wiki_lookup"])

        self.pushButton_save_settings.clicked.connect(self.save_settings_button)
        self.pushButton_cancel_settings.clicked.connect(self.init_settings)
        self.pushButton_reload_default.clicked.connect(self.init_default_settings)

    @Slot()
    def init_default_settings(self):
        self.spin_font_size.setValue(parameters.default_parameters['Interface']["font_size"])
        self.lineEdit_external_image_editor_path.setText(parameters.default_parameters['General']["external_image_editor_path"])
        self.spin_image_load_size.setValue(parameters.default_parameters['Interface']["image_load_size"])
        self.lineEdit_automatic_tagger.setText(",".join([x.name for x in parameters.default_parameters['Taggers']["automatic_tagger"]]))
        self.spin_swinv2_thresh.setValue(parameters.default_parameters['Taggers']["swinv2_threshold"])
        self.spin_wdeva02_large_threshold.setValue(parameters.default_parameters['Taggers']["wdeva02_large_threshold"])
        self.spin_swinv2_chara_thresh.setValue(parameters.default_parameters['Taggers']["swinv2_character_threshold"])
        self.spin_swinv2_chara_count.setValue(parameters.default_parameters['Taggers']["swinv2_character_count_threshold"])
        self.check_swinv2_chara.setChecked(parameters.default_parameters['Taggers']["swinv2_enable_character"])
        self.checkBox_enable_image_tooltip.setChecked(parameters.default_parameters['Interface']["database_view_tooltip"])
        self.checkBox_hide_sentence_in_view.setChecked(parameters.default_parameters['Interface']["hide_sentence_in_view"])
        self.spin_caformer_thresh.setValue(parameters.default_parameters['Taggers']["caformer_threshold"])
        self.spin_max_batch_size.setValue(parameters.default_parameters['Taggers']["max_batch_size"])
        self.lineEdit_keep_token_tag_separator.setText(parameters.default_parameters['Database']["keep_token_tags_separator"])
        self.check_remove_transparency_from_images.setChecked(parameters.default_parameters['Database']["remove_transparency_from_images"])
        self.spin_max_images_loader_thread.setValue(parameters.default_parameters['Database']["max_images_loader_thread"])
        self.spin_max_4k_pixels_save_multiplier.setValue(parameters.default_parameters['Database']["max_4k_pixel_save_multiplier"])
        self.spin_max_amount_of_backups.setValue(parameters.default_parameters['Database']["max_databases_view_backup"])
        self.spin_similarity_thresh.setValue(parameters.default_parameters['General']["similarity_threshold"])
        self.spinBox_detection_resolution.setValue(parameters.default_parameters['Taggers']["detection_small_resolution"])

        #self.comboBox_click_option.addItems(["Single Click", "Double Click"])
        self.comboBox_click_option.setCurrentText("Double Click" if parameters.default_parameters['Interface']["double_click"] else "Single Click")

        self.check_filter_remove_characters.setChecked(parameters.default_parameters['Filter']["filter_remove_characters"])
        self.check_filter_remove_metadata.setChecked(parameters.default_parameters['Filter']["filter_remove_metadata"])
        self.check_filter_remove_series.setChecked(parameters.default_parameters['Filter']["filter_remove_series"])
        
        # settings for custom toml creation
        self.spinBox_custom_height.setValue(parameters.default_parameters['Exporting']["custom_export_height"])
        self.spinBox_custom_width.setValue(parameters.default_parameters['Exporting']["custom_export_width"])
        self.spinBox_custom_bucket_steps.setValue(parameters.default_parameters['Exporting']["custom_export_bucket_steps"])
        self.spinBox_sample_count.setValue(parameters.default_parameters['Exporting']["toml_sample_max_count"])

        self.checkBox_load_images_thumbnail.setChecked(parameters.default_parameters['Interface']["view_load_images"])
        self.checkBox_double_images_thumbnail_size.setChecked(parameters.default_parameters['Interface']["doubling_image_thumbnail_max_size"])
        self.check_deactivate_filter.setChecked(parameters.default_parameters['Filter']["deactivate_filter"])
        self.checkBox_activate_danbooru_tag_wiki_lookup.setChecked(parameters.default_parameters['Interface']["danbooru_tag_wiki_lookup"])


    @Slot()
    def save_settings_button(self):
        parameters.PARAMETERS["font_size"] = self.spin_font_size.value()
        parameters.PARAMETERS["external_image_editor_path"] = self.lineEdit_external_image_editor_path.text().strip()
        parameters.PARAMETERS["database_view_tooltip"] = self.checkBox_enable_image_tooltip.isChecked()
        parameters.PARAMETERS["hide_sentence_in_view"] = self.checkBox_hide_sentence_in_view.isChecked()
        parameters.PARAMETERS["image_load_size"] = self.spin_image_load_size.value()
        parameters.PARAMETERS["automatic_tagger"] = [parameters.AvailableTaggers[t.strip().upper()] for t in self.lineEdit_automatic_tagger.text().strip().split(",")]
        parameters.PARAMETERS["swinv2_threshold"] = self.spin_swinv2_thresh.value()
        parameters.PARAMETERS["wdeva02_large_threshold"] = self.spin_wdeva02_large_threshold.value()
        parameters.PARAMETERS["swinv2_character_threshold"] = self.spin_swinv2_chara_thresh.value()
        parameters.PARAMETERS["swinv2_character_count_threshold"]=self.spin_swinv2_chara_count.value()
        parameters.PARAMETERS["swinv2_enable_character"]=self.check_swinv2_chara.isChecked()
        parameters.PARAMETERS["caformer_threshold"]=self.spin_caformer_thresh.value()
        parameters.PARAMETERS["max_batch_size"] = self.spin_max_batch_size.value()
        parameters.PARAMETERS["keep_token_tags_separator"] = self.lineEdit_keep_token_tag_separator.text().strip()
        parameters.PARAMETERS["remove_transparency_from_images"] = self.check_remove_transparency_from_images.isChecked()
        parameters.PARAMETERS["max_images_loader_thread"] = self.spin_max_images_loader_thread.value()
        parameters.PARAMETERS["max_4k_pixel_save_multiplier"] = self.spin_max_4k_pixels_save_multiplier.value()
        parameters.PARAMETERS["max_databases_view_backup"] = self.spin_max_amount_of_backups.value()
        parameters.PARAMETERS["similarity_threshold"] = self.spin_similarity_thresh.value()
        parameters.PARAMETERS["detection_small_resolution"] = self.spinBox_detection_resolution.value()
        
        parameters.PARAMETERS["double_click"] = self.comboBox_click_option.currentText() == "Double Click"

        parameters.PARAMETERS["filter_remove_characters"] = self.check_filter_remove_characters.isChecked()
        parameters.PARAMETERS["filter_remove_metadata"] = self.check_filter_remove_metadata.isChecked()
        parameters.PARAMETERS["filter_remove_series"] = self.check_filter_remove_series.isChecked()
        
        # settings for custom toml creation
        parameters.PARAMETERS["custom_export_height"] = self.spinBox_custom_height.value()
        parameters.PARAMETERS["custom_export_width"] = self.spinBox_custom_width.value()
        parameters.PARAMETERS["custom_export_bucket_steps"] = self.spinBox_custom_bucket_steps.value()
        parameters.PARAMETERS["toml_sample_max_count"] = self.spinBox_sample_count.value()


        parameters.PARAMETERS["view_load_images"] = self.checkBox_load_images_thumbnail.isChecked()
        parameters.PARAMETERS["doubling_image_thumbnail_max_size"] = self.checkBox_double_images_thumbnail_size.isChecked()
        parameters.PARAMETERS["deactivate_filter"] = self.check_deactivate_filter.isChecked()
        parameters.PARAMETERS["danbooru_tag_wiki_lookup"] = self.checkBox_activate_danbooru_tag_wiki_lookup.isChecked()

        parameters.save_config()


    def closeEvent(self, event):
        can_exit = CustomWidgets.confirmation_dialog(self)
        # do stuff
        if can_exit:
            event.accept()  # let the window close
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    qdarkstyle.load_stylesheet(qt_api="pyside6", palette=qdarkstyle.DarkPalette)

    #app.setStyleSheet(style_sheet)

    """
    with open("stylesheet.txt", 'w') as file:
        file.write(style_sheet)
    """
    with open("stylesheet.txt", 'r') as file:
        style_list = file.readlines()
    style_sheet = ''.join(style_list)

    app.setStyleSheet(style_sheet)

    custom_font = QFont(parameters.PARAMETERS["font_name"], parameters.PARAMETERS["font_size"])
    app.setFont(custom_font)
    window = AddTags()
    window.show()
    sys.exit(app.exec())
