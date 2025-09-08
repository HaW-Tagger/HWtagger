import json
import os
import shutil

from PySide6 import QtCore
from PySide6.QtCore import Slot, Signal, Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from tqdm import tqdm

from classes.class_elements import GroupElement
from resources import tag_categories, parameters
import CustomWidgets
from classes.class_image import ImageDatabase
from interfaces import global_database_view
from classes.class_database import Database
from tools import files


class GlobalDatabaseFrame(QWidget, global_database_view.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.databases_item: list[tuple[CustomWidgets.GlobalDatabaseItem, Database]] = []
        self.validated_images: dict[str: list[ImageDatabase]] = {}
        self.search_path = ""

        self.pushButton_search.clicked.connect(self.search_button)
        self.pushButton_validate_choice.clicked.connect(self.validate_button)
        self.pushButton_images_existence.clicked.connect(self.images_existence_button)
        self.pushButton_merge_datasets.clicked.connect(self.merged_datasets_button)
        self.pushButton_create_metacap.clicked.connect(self.create_metacap_button)


    def search_button(self):
        # set up the scrollArea
        scroll_layout = QVBoxLayout()
        widget = QWidget()



        self.databases_item: list[tuple[CustomWidgets.GlobalDatabaseItem, Database]] = []
        path = self.lineEdit_global_folder_path.text().strip()
        if not os.path.isdir(path):
            parameters.log.error("The input path is not a directory")
            return
        all_databases_paths = [x for x in files.get_all_databases_folder(path) if os.path.abspath(x) != os.path.abspath(path)]
        if len(all_databases_paths) == 0:
            parameters.log.error("No databases in the directory")
            return
        # path is valid
        self.search_path = path

        for k in range(len(all_databases_paths)):
            parameters.log.info(f"Loading {k+1}/{len(all_databases_paths)}: {all_databases_paths[k]}")
            database = Database(all_databases_paths[k])
            if self.checkBox_presearch_existence_of_images.isChecked():
                database.check_existence_images()
            db_widget = CustomWidgets.GlobalDatabaseItem(database)
            self.databases_item.append((db_widget, database))
            scroll_layout.addWidget(db_widget)

        widget.setLayout(scroll_layout)
        self.scrollArea_databases.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea_databases.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_databases.setWidgetResizable(True)
        self.scrollArea_databases.setWidget(widget)

    def validate_button(self):
        self.validated_images: dict[str: list[ImageDatabase]] = {}
        restricted = self.checkBox_import_best_great.isChecked()
        for db_widget, db in self.databases_item:
            relative_folder = os.path.relpath(db.folder, start=self.search_path)
            if not db_widget.checked_database():
                continue
            validated_groups = db_widget.checked_group_names()
            if not validated_groups:
                self.validated_images[relative_folder] = [x for x in db.images if (not restricted) or x.score_label in tag_categories.QUALITY_LABELS[-3:]] # if it's quality restricted use good categories only
                continue
            self.validated_images[relative_folder] = []
            for group in validated_groups:
                if group == "ungrouped":
                    self.validated_images[relative_folder].extend([db.images[x] for x in db.get_ungrouped_images() if (not restricted) or db.images[x] in tag_categories.QUALITY_LABELS[-3:]])
                else:
                    images_md5 = db.index_of_images_by_md5(db.groups[group].md5s)
                    self.validated_images[relative_folder].extend([db.images[x] for x in images_md5 if db.images[x] not in self.validated_images[relative_folder] and ((not restricted) or db.images[x] in tag_categories.QUALITY_LABELS[-3:])])

    def images_existence_button(self):
        if not self.validated_images:
            return

        empty_images = []
        for image_list in self.validated_images.values():
            i = 0
            while i < len(image_list):
                if not os.path.exists(image_list[i].path):
                    empty_images.append(image_list.pop(i))
                else:
                    i+=1
        parameters.log.error(f"{len(empty_images)} images were not found and have been removed from the validated images.")

    def merged_datasets_button(self):
        if not self.validated_images:
            return
        if not CustomWidgets.confirmation_dialog(self, "If if you don't select 'save databases origins as groups' but select reorganize all folders, then all images will be in the main folder.\nRenames the image files to their md5 value.\nRemoves the database.json of the main folder (if it exists)."):
            return

        save_database_as_group = self.checkBox_save_databases_as_groups.isChecked()

        if os.path.exists(os.path.join(self.search_path, parameters.DATABASE_FILE_NAME)):
            os.remove(os.path.join(self.search_path, parameters.DATABASE_FILE_NAME))
        # the code to create the new database
        merged_database = Database(self.search_path)
        for group in self.validated_images.keys():
            for image in self.validated_images[group]:
                merged_database.images.append(image)
                if save_database_as_group:
                    if group not in merged_database.groups.keys():
                        merged_database.groups[group] = GroupElement(group_name=group, md5s=[])
                    merged_database.groups[group].add_item(image.md5)
        merged_database.save_database()

        if self.checkBox_reorganize_folder.isChecked():
            backup_path = os.path.join(os.path.dirname(self.search_path), "BACKUP-"+os.path.basename(self.search_path))
            os.makedirs(backup_path)
            for temp_path in os.listdir(self.search_path):
                if parameters.DATABASE_FILE_NAME != temp_path:
                    shutil.move(src=os.path.join(self.search_path, temp_path), dst=os.path.join(backup_path, temp_path))

            md5_groups_link: dict[str: str] = {}
            if merged_database.groups:
                for group in merged_database.groups.values():
                    os.makedirs(os.path.join(self.search_path, group.group_name.replace('\\', '_')))
                    for image_md5 in merged_database.groups[group.group_name].md5s:
                        md5_groups_link[image_md5] = group.group_name

            for image in tqdm(merged_database.images):
                src_path = os.path.join(backup_path, os.path.relpath(image.path, start=self.search_path))
                new_md5 = files.get_md5(src_path)
                new_basename = new_md5 + os.path.splitext(os.path.basename(image.path))[1]
                if image.md5 in md5_groups_link.keys():
                    merged_database.groups[md5_groups_link[image.md5]][image.md5] = new_md5
                    dst_path = os.path.join(self.search_path,  md5_groups_link[image.md5].replace('\\', '_'), new_basename)
                    shutil.copy2(src=src_path, dst=dst_path)
                    image.path = dst_path
                    image.relative_path = os.path.relpath(image.path, start=self.search_path)
                    image.md5 = new_md5
                else:
                    dst_path = os.path.join(self.search_path, new_basename)
                    shutil.copy2(src=src_path, dst=dst_path)
                    image.path = dst_path
                    image.relative_path = os.path.relpath(image.path, start=self.search_path)
                    image.md5 = new_md5
        merged_database.save_database()

    def create_metacap_button(self):
        """
        no keep token separator used, always using the quality tags, and they are first
        Returns:
        """
        if not self.validated_images:
            return
        image_dict = {}
        for group in self.validated_images.keys():
            for image in self.validated_images[group]:
                to_write = image.create_output(add_backslash_before_parenthesis=False,
                                               keep_tokens_separator=False,
                                               main_tags=[],
                                               secondary_tags=[],
                                               use_aesthetic_score=True,
                                               score_trigger=True,
                                               use_sentence=False,
                                               sentence_in_trigger=False,
                                               remove_tags_in_sentence=False
                                               )
                image_dict[image.path] = {}
                image_dict[image.path]["tags"] = to_write
        with open(os.path.join(self.search_path, "meta_cap.json"), 'w') as f:
            json.dump(image_dict, f, indent=4)
        parameters.log.info("Created json for exporting data for checkpoint")




