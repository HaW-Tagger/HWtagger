import DatabaseCreationView


def _ignore_xformers_triton_message_on_windows():
    import logging
    logging.getLogger("xformers").addFilter(
        lambda record: 'triton is not available' not in record.getMessage())

# In order to be effective, this needs to happen before anything could possibly import xformers.
_ignore_xformers_triton_message_on_windows()




import concurrent.futures
import os, sys
import time
os.environ["XFORMERS_FORCE_DISABLE_TRITON"] = "1"
import CustomWidgets
from resources import parameters, tag_categories
tag_categories.check_categories()

import GlobalDatabaseView
import DatasetCleaning
import StatisticsTab
import DatabaseViewBase
import ImageTools
from interfaces import interface
from tools import files, images, main

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QFont, QPalette, QColor, Qt

from classes.class_database import Database
import qdarkstyle
#tag_categories.check_definitions_and_recommendations()

class AddTags(QMainWindow, interface.Ui_MainWindow):
    def __init__(self):
        super(AddTags, self).__init__()
        self.setupUi(self)
        #with open("metdata.txt", 'w') as file:
        #    file.write(','.join([x for x in tag_categories.METADATA_TAGS.keys()]))

        #############################
        # PRE INIT
        self.basic_database: Database = None
        self.checkpoint_database: Database = None

        #############################
        # DATABASE TOOLS

        # left
        self.pushButton_load_database.clicked.connect(self.load_database_button)
        self.pushButton_save_database.clicked.connect(self.save_database_button)

        self.pushButton_create_txt_files.clicked.connect(self.create_txt_files_button)
        self.pushButton_create_sample_toml.clicked.connect(self.create_sample_toml_button)

        self.pushButton_images_existence.clicked.connect(self.images_existence_button)
        self.pushButton_filter_images.clicked.connect(self.filter_images_button)
        self.pushButton_reautotags.clicked.connect(self.reautotags_button)
        self.pushButton_rescores.clicked.connect(self.rescore_button)
        self.pushButton_reclassify.clicked.connect(self.reclassify_button)

        self.pushButton_move_files_groupings.clicked.connect(self.move_files_groupings_button)
        self.pushButton_rebuild_groups.clicked.connect(self.rebuild_groups_button)
        self.pushButton_rehash.clicked.connect(self.rehash_button)

        self.pushButton_print_unknown_tags.clicked.connect(self.print_unknown_tags_button)
        self.pushButton_convert_images_to_png.clicked.connect(self.convert_images_to_png_button)
        self.pushButton_rename_images_md5.clicked.connect(self.rename_images_md5_button)

        # checkpoint TOOLS TAB
        self.pushButton_rename_all.clicked.connect(self.rename_bad_names_to_md5)
        self.pushButton_create_meta_cap.clicked.connect(self.create_meta_cap_button)
        self.pushButton_export_npz.clicked.connect(self.export_for_checkpoint)

        #############################
        # DATABASE CREATION TAB
        self.database_creation_tab = DatabaseCreationView.DatabaseCreationView()
        self.tabWidget_2.insertTab(0, self.database_creation_tab, "Database Creation Tool")
        self.tabWidget_2.setCurrentIndex(0)

        #############################
        # VIEW DATABASE TAB
        self.pushButton_view_database.clicked.connect(self.view_database_button)
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
        # DATASET CLEANING TAB
        self.statistics_tab = StatisticsTab.StatisticsView()
        self.tabWidget.insertTab(4, self.statistics_tab, "Statistics")

        ##############################
        # IMAGE TOOLS TAB
        self.image_tools_tab = ImageTools.ImageToolsView()
        self.tabWidget.insertTab(4, self.image_tools_tab, "Image Tools")

        #############################
        # SETTINGS TAB
        self.init_settings()



    @Slot()
    def load_database_button(self):
        if not os.path.exists(os.path.join(self.lineEdit_database_folder.text(), parameters.DATABASE_FILE_NAME)):
            parameters.log.error(f"Database doesn't exist in {self.lineEdit_database_folder.text()}")
            return
        parameters.log.info("Loading Database")
        self.basic_database = Database(self.lineEdit_database_folder.text())
        self.lineEdit_main_trigger_tags.setText(", ".join(self.basic_database.trigger_tags["main_tags"]))
        self.plainTextEdit_secondary_trigger_tags.setPlainText(", ".join(self.basic_database.trigger_tags["secondary_tags"]))
        parameters.log.info(f"Loaded Database with {len(self.basic_database.images)} images")

    @Slot()
    def save_database_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        self.basic_database.save_database()

    @Slot()
    def create_database_button(self):
        parameters.log.info("Creating database")
        database_folder = self.lineEdit_database_folder.text()
        if self.checkBox_convert_to_png.isChecked():
            if not self.convert_images_to_png_button(folder=database_folder):
                return False
        if self.settings_is_rename_all_files_to_md5.isChecked():
            if not self.rename_images_md5_button(folder=database_folder):
                return False

        self.basic_database = Database(database_folder)
        self.basic_database.add_images_to_db(files.get_all_images_in_folder(database_folder),
                                            autotag=self.checkBox_auto_tag.isChecked(),
                                            score=self.checkBox_auto_score.isChecked(),
                                            classify=self.checkBox_auto_classification.isChecked(),
                                            from_txt=self.checkBox_tags_from_txt.isChecked(),
                                            grouping_from_path=self.checkBox_group_add.isChecked(),
                                            move_dupes=self.checkBox_remove_duplicates.isChecked()
                                            )
        if self.checkBox_apply_filtering.isChecked():
            self.basic_database.filter_all()
        self.lineEdit_main_trigger_tags.setText(", ".join(self.basic_database.trigger_tags["main_tags"]))
        self.plainTextEdit_secondary_trigger_tags.setPlainText(", ".join(self.basic_database.trigger_tags["secondary_tags"]))
        parameters.log.info("Created database")

    @Slot()
    def add_new_images_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        existing_paths = [x.path for x in self.basic_database.images]
        images_paths = [x for x in files.get_all_images_in_folder(self.lineEdit_database_folder.text()) if x not in existing_paths]
        if self.checkBox_convert_to_png.isChecked():
            parameters.log.info("Converting images to .png format")
            start_time = time.time()
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
            files.to_png_from_images_paths(images_paths, pool)
            pool.shutdown(wait=True)
            parameters.log.info(f"Images loaded in {round(time.time() - start_time, 3)} seconds")
        if self.settings_is_rename_all_files_to_md5.isChecked():
            parameters.log.info("Converting images to MD5 filename.")
            files.to_md5_from_images_paths(images_paths)
        self.basic_database.add_images_to_db([x for x in files.get_all_images_in_folder(self.lineEdit_database_folder.text()) if x not in existing_paths],
                                            autotag=self.checkBox_auto_tag.isChecked(),
                                            score=self.checkBox_auto_score.isChecked(),
                                            classify=self.checkBox_auto_classification.isChecked(),
                                            from_txt=self.checkBox_tags_from_txt.isChecked(),
                                            grouping_from_path=self.checkBox_group_add.isChecked()
                                            )
        if self.checkBox_apply_filtering.isChecked():
            self.basic_database.filter_all()
        parameters.log.info("Added new images to database")

    @Slot()
    def create_txt_files_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        self.basic_database.trigger_tags["main_tags"] = [x.strip() for x in self.lineEdit_main_trigger_tags.text().split(",")]
        self.basic_database.trigger_tags["secondary_tags"] = [x.strip() for x in self.plainTextEdit_secondary_trigger_tags.toPlainText().split(",")]
        self.basic_database.create_txt_files(
            use_trigger_tags=self.checkBox_trigger_tags.isChecked(),
            token_separator=self.checkBox_token_separator.isChecked(),
            use_aesthetic_score=self.checkBox_aesthetic_score.isChecked(),
            use_sentence=self.checkBox_sentence.isChecked(),
            sentence_in_trigger=self.checkBox_sentence_in_token_separator.isChecked(),
            remove_tags_in_sentence=self.checkBox_remove_tag_in_sentence.isChecked(),
            )

    @Slot()
    def create_meta_cap_button(self):
        if not self.checkpoint_database:
            parameters.log.error("Database not loaded, attempting to load it")
            if self.lineEdit_dataset_folder.text():
                parameters.log.info("Using database folder to load database")
                self.checkpoint_database = Database(self.lineEdit_dataset_folder.text())
            else:
                parameters.log.error("Attempt failed, aborting process")
        if self.checkpoint_database:
            self.checkpoint_database.create_json_file(
                use_trigger_tags=self.checkBox_trigger_tags.isChecked(),
                token_separator=self.checkBox_token_separator.isChecked(),
                use_aesthetic_score=self.checkBox_aesthetic_score.isChecked(),
                use_sentence=self.checkBox_sentence.isChecked(),
                sentence_in_trigger=self.checkBox_sentence_in_token_separator.isChecked(),
                remove_tags_in_sentence=self.checkBox_remove_tag_in_sentence.isChecked(),
                )
        else:
            parameters.log.error("Database not loaded, aborting process, meta_cap.json not generated")

    @Slot()
    def create_sample_toml_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return False
        self.basic_database.trigger_tags["main_tags"] = [x.strip() for x in self.lineEdit_main_trigger_tags.text().split(",")]
        self.basic_database.trigger_tags["secondary_tags"] = [x.strip() for x in self.plainTextEdit_secondary_trigger_tags.toPlainText().split(",")]
        self.basic_database.create_sample_toml()

    @Slot()
    def images_existence_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
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
        self.basic_database.retag_images()

    @Slot()
    def rescore_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.rescore_images()

    @Slot()
    def reclassify_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.reclassify_images()

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

    @Slot()
    def rehash_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.reapply_md5()
        parameters.log.info("Updated MD5 of images")

    @Slot()
    def move_files_groupings_button(self):
        if not self.basic_database:
            parameters.log.error("Database not loaded")
            return
        self.basic_database.organise_image_paths_groups()

    @Slot()
    def print_unknown_tags_button(self):
        unk_tags = []
        known_tags = set(tag_categories.COLOR_DICT.keys()).union(tag_categories.REJECTED_TAGS)

        import numpy as np
        from resources.tag_categories import KAOMOJI

        
        ca_dict = files.get_caformer_tags()
        
        ca_list = [ca_dict[str(k)].replace("_", " ") if len(ca_dict[str(k)]) > 3 else ca_dict[str(k)] for k in
                   range(12546 + 1)]
        ca_list = [ca for ca in ca_list if ca not in known_tags]
        ca_set = set(ca_list)
        
        
        tags_df = files.get_pd_swinbooru_tag_frequency()
        
        tags_df = tags_df.sort_values(by=['count'], ascending=False)
        name_series = tags_df["name"]
        name_series = name_series.map(lambda x: x.replace("_", " ") if len(x) > 3 and x not in KAOMOJI else x)
        tag_names = name_series.tolist()
        general_indexes = list(np.where(tags_df["category"] == 0)[0])
        general_tag = [tag_names[i] for i in general_indexes]
        gt_list = [gt for gt in general_tag if gt not in known_tags]

        parameters.log.info(", ".join(ca_list))
        parameters.log.info(", ".join([gt for gt in gt_list if gt not in ca_set]))

        if self.basic_database:
            for image in self.basic_database.images:
                for tag in image.get_full_tags():
                    if tag not in known_tags and tag not in unk_tags:
                        unk_tags.append(tag)
            parameters.log.info(unk_tags)

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


    def merge_secondary(self): # load and merge database method
        # load old db and transfer data for files with matching md5
        db_path = self.lineEdit_secondarydata.text().strip()
        if db_path:
            sec_db = Database(db_path)
            update_counter = 0
            if sec_db and self.basic_database:
                sec_md5s = [img.md5 for img in sec_db.images]
                current_md5 = [img.md5 for img in self.basic_database.images]
                md5_intersect = set(current_md5).intersection(set(sec_md5s))
                for md5 in md5_intersect:
                    i = self.basic_database.index_of_image_by_md5(md5)
                    current_full_path = self.basic_database.images[i].path
                    current_groups = self.basic_database.images[i].group_names
                    
                    current_score_val = self.basic_database.images[i].score_value
                    current_score_label = self.basic_database.images[i].score_label
                    current_class_val = self.basic_database.images[i].classify_label
                    current_class_label = self.basic_database.images[i].classify_value
                    current_media = self.basic_database.images[i].media
                    
                    sec_i = sec_db.index_of_image_by_md5(md5)
                    data_dict = sec_db.images[sec_i].get_saving_dict()
                    
                    # update non-tags
                    self.basic_database.images[i].init_image_dict(data_dict, fast_load=True)
                    self.basic_database.images[i].path = current_full_path
                    self.basic_database.images[i].group_names = current_groups
                    
                    if current_score_label and not self.basic_database.images[i].score_label:
                        self.basic_database.images[i].score_label = current_score_label
                        self.basic_database.images[i].score_value = current_score_val
                    
                    if current_class_label and not self.basic_database.images[i].classify_label:
                        self.basic_database.images[i].classify_label = current_class_val
                        self.basic_database.images[i].classify_value = current_class_label 
                    
                    if current_media and not self.basic_database.images[i].media:
                        self.basic_database.images[i].media = current_media
                    
                    # legacy, update score to new [0~1] if found
                    old_score = self.basic_database.images[i].score_value
                    if 1 >= current_score_val > 0 and current_score_val < old_score:
                        self.basic_database.images[i].score_value = current_score_val
                    
                    update_counter+=1
                parameters.log.info(f"Updated {update_counter} images in primary database from secondary database")

            else:
                parameters.log.error("Primary or secondary db is not loaded properly")
        else:
            parameters.log.error("No secondary dataset selected")

    def export_for_checkpoint(self):
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
                    
            all_img_paths = self.checkpoint_database.get_all_paths()
            
            def has_special_char(text: str) -> bool: # this checks for non alpha numeric and ignores whitespace
                return any(char for char in text if not (char.isascii() and (char.isalnum() or char in "_-( )")))
            
            renamed_pair = []
            for img_path in all_img_paths:
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
    def view_database_button(self):
        folder_path = self.lineEdit_view_database_path.text().strip()
        if not os.path.exists(os.path.join(folder_path,parameters.DATABASE_FILE_NAME)):
            parameters.log.warning("No valid path entered.")
            return False
        temp_db = Database(folder_path)
        temp_db.check_existence_images()
        self.add_db_tab_widget(temp_db)

    def add_db_tab_widget(self, db):
        main_widget = DatabaseViewBase.DatabaseViewBase(db)
        #main_widget = DatabaseTags.DatabaseFrame(db)
        self.databaseTabWidget.addTab(main_widget, db.folder)

    @Slot(int)
    def view_database_close_requested(self, index):
        close_tab = self.databaseTabWidget.widget(index)
        self.databaseTabWidget.removeTab(index)
        close_tab.close()

    @Slot()
    def init_settings(self):
        self.spin_font_size.setValue(parameters.PARAMETERS["font_size"])
        self.lineEdit_external_image_editor_path.setText(parameters.PARAMETERS["external_image_editor_path"])
        self.spin_image_load_size.setValue(parameters.PARAMETERS["image_load_size"])
        self.lineEdit_automatic_tagger.setText(",".join([x.name for x in parameters.PARAMETERS["automatic_tagger"]]))
        self.spin_swinv2_thresh.setValue(parameters.PARAMETERS["swinv2_threshold"])
        self.spin_swinv2_chara_thresh.setValue(parameters.PARAMETERS["swinv2_character_threshold"])
        self.spin_swinv2_chara_count.setValue(parameters.PARAMETERS["swinv2_character_count_threshold"])
        self.check_swinv2_chara.setChecked(parameters.PARAMETERS["swinv2_enable_character"])
        self.checkBox_enable_image_tooltip.setChecked(parameters.PARAMETERS["database_view_tooltip"])
        self.spin_caformer_thresh.setValue(parameters.PARAMETERS["caformer_threshold"])
        self.spin_max_batch_size.setValue(parameters.PARAMETERS["max_batch_size"])
        self.lineEdit_keep_token_tag_separator.setText(parameters.PARAMETERS["keep_token_tags_separator"])
        self.check_remove_transparency_from_images.setChecked(parameters.PARAMETERS["remove_transparency_from_images"])
        self.spin_max_images_loader_thread.setValue(parameters.PARAMETERS["max_images_loader_thread"])
        self.spin_max_4k_pixels_save_multiplier.setValue(parameters.PARAMETERS["max_4k_pixel_save_multiplier"])
        self.spin_similarity_thresh.setValue(parameters.PARAMETERS["similarity_threshold"])
        
        #self.comboBox_click_option.addItems(["Single Click", "Double Click"])
        self.comboBox_click_option.setCurrentText("Double Click" if parameters.PARAMETERS["double_click"] else "Single Click")

        self.check_filter_remove_characters.setChecked(parameters.PARAMETERS["filter_remove_characters"])
        self.check_filter_remove_metadata.setChecked(parameters.PARAMETERS["filter_remove_metadata"])
        self.check_filter_remove_series.setChecked(parameters.PARAMETERS["filter_remove_series"])
         
        self.pushButton_save_settings.clicked.connect(self.save_settings_button)
        self.pushButton_cancel_settings.clicked.connect(self.init_settings)

    @Slot()
    def save_settings_button(self):
        parameters.PARAMETERS["font_size"] = self.spin_font_size.value()
        parameters.PARAMETERS["external_image_editor_path"] = self.lineEdit_external_image_editor_path.text().strip()
        parameters.PARAMETERS["database_view_tooltip"] = self.checkBox_enable_image_tooltip.isChecked()
        parameters.PARAMETERS["image_load_size"] = self.spin_image_load_size.value()
        parameters.PARAMETERS["automatic_tagger"] = [parameters.AvailableTaggers[t.strip().upper()] for t in self.lineEdit_automatic_tagger.text().strip().split(",")]
        parameters.PARAMETERS["swinv2_threshold"] = self.spin_swinv2_thresh.value()
        parameters.PARAMETERS["swinv2_character_threshold"] = self.spin_swinv2_chara_thresh.value()
        parameters.PARAMETERS["swinv2_character_count_threshold"]=self.spin_swinv2_chara_count.value()
        parameters.PARAMETERS["swinv2_enable_character"]=self.check_swinv2_chara.isChecked()
        parameters.PARAMETERS["caformer_threshold"]=self.spin_caformer_thresh.value()
        parameters.PARAMETERS["max_batch_size"] = self.spin_max_batch_size.value()
        parameters.PARAMETERS["keep_token_tags_separator"] = self.lineEdit_keep_token_tag_separator.text().strip()
        parameters.PARAMETERS["remove_transparency_from_images"] = self.check_remove_transparency_from_images.isChecked()
        parameters.PARAMETERS["max_images_loader_thread"] = self.spin_max_images_loader_thread.value()
        parameters.PARAMETERS["max_4k_pixel_save_multiplier"] = self.spin_max_4k_pixels_save_multiplier.value()
        parameters.PARAMETERS["similarity_threshold"] = self.spin_similarity_thresh.value()
        
        parameters.PARAMETERS["double_click"] = self.comboBox_click_option.currentText() == "Double Click"

        parameters.PARAMETERS["filter_remove_characters"] = self.check_filter_remove_characters.isChecked()
        parameters.PARAMETERS["filter_remove_metadata"] = self.check_filter_remove_metadata.isChecked()
        parameters.PARAMETERS["filter_remove_series"] = self.check_filter_remove_series.isChecked()
        
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
