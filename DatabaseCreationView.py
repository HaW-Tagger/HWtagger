import os

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

import CustomWidgets
from classes.class_database import Database
from interfaces import databaseCreationTab
from resources import parameters
from tools import files


class DatabaseCreationView(QWidget, databaseCreationTab.Ui_Form):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		# connect buttons, the only important aspects
		self.pushButton_load_database.clicked.connect(self.load_database_button)
		self.pushButton_create_database.clicked.connect(self.create_database_button)
		self.pushButton_save_database.clicked.connect(self.save_database_button)
		self.pushButton_add_new_images.clicked.connect(self.add_images_to_database_button)
		self.pushButton_reapply_to_database.clicked.connect(self.reapply_to_database_button)
		self.db: Database = None

	@Slot()
	def load_database_button(self):
		if not os.path.exists(os.path.join(self.lineEdit_path.text(), parameters.DATABASE_FILE_NAME)):
			parameters.log.error(f"Database doesn't exist in {self.lineEdit_path.text()}")
			return
		parameters.log.info("Loading Database")
		self.db = Database(self.lineEdit_path.text())
		parameters.log.info(f"Loaded Database with {len(self.db.images)} images")

	@Slot()
	def save_database_button(self):
		if not self.db:
			parameters.log.error("Database not loaded")
			return False
		self.db.save_database()

	@Slot()
	def create_database_button(self):
		folder = self.lineEdit_path.text()


		if self.checkBox_offline_tags.isChecked() and '.' not in self.lineEdit_offline_extension_tags.text():
			parameters.log.error(f"The extension name for offline tags should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_tags.isChecked() and '.' not in self.lineEdit_offline_extension_caption.text():
			parameters.log.error(f"The extension name for offline captions should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_tags.isChecked() and not self.lineEdit_offline_name_tags.text().strip():
			parameters.log.error(f"The offline name should always be specified when using tags.")
			return False


		if self.checkBox_danbooru.isChecked() or self.checkBox_gelbooru.isChecked() or self.checkBox_rule34.isChecked():
			if not CustomWidgets.confirmation_dialog(self, text=f"Checking for online tags can take a long time depending on multiple factors like your internet connection or the amount of images in your dataset, do you wish to continue ?"):
				return False

		if os.path.exists(os.path.join(folder, parameters.DATABASE_FILE_NAME)):
			files.backup_database_file(folder)
			parameters.log.error(f"Database exists in {folder}, database is backed")
		images_paths = files.get_all_images_in_folder(folder)
		self.db = Database(folder)
		self.db.add_images_to_db(images_paths, move_dupes=self.checkBox_move_duplicates_out_of_folder.isChecked(), grouping_from_path=self.checkBox_groups_from_folders.isChecked())

		if self.checkBox_use_taggers.isChecked():
			self.db.auto_tag_all_images()
		if self.checkBox_use_aesthetic_scorer.isChecked():
			self.db.score_all_images()
		if self.checkBox_use_classifier.isChecked():
			self.db.classify_all_images()

		if self.checkBox_offline_tags.isChecked():
			self.db.add_offline_tags_all_images(is_sentence=False, do_search_complete_name=self.checkBox_both_names_tags.isChecked(), extension_name=self.lineEdit_offline_extension_tags.text().strip(), source_name=self.lineEdit_offline_name_tags.text().strip())
		if self.checkBox_offline_captions.isChecked():
			self.db.add_offline_tags_all_images(is_sentence=True, do_search_complete_name=self.checkBox_both_names_captions.isChecked(), extension_name=self.lineEdit_offline_extension_caption.text().strip(), source_name="nothing")

		if self.checkBox_danbooru.isChecked():
			self.db.retrieve_danbooru_tags_all_images()
		if self.checkBox_gelbooru.isChecked():
			self.db.retrieve_gelbooru_tags_all_images(unsafe=self.checkBox_unsafe_gelbooru.isChecked())
		if self.checkBox_rule34.isChecked():
			self.db.retrieve_rule34_tags_all_images(unsafe=self.checkBox_unsafe_rule34.isChecked())

		if self.checkBox_rename_to_md5.isChecked():
			self.db.rename_all_images_to_md5()

		if self.checkBox_rename_to_png.isChecked():
			self.db.rename_all_images_to_png()

		if self.checkBox_filter_all_images.isChecked():
			self.db.filter_all()

		parameters.log.info("Finished Creating Database")


	@Slot()
	def add_images_to_database_button(self):
		if not self.db:
			parameters.log.error("Database not loaded")
			return False


		if self.checkBox_offline_tags.isChecked() and '.' not in self.lineEdit_offline_extension_tags.text():
			parameters.log.error(f"The extension name for offline tags should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_tags.isChecked() and '.' not in self.lineEdit_offline_extension_caption.text():
			parameters.log.error(f"The extension name for offline captions should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_tags.isChecked() and not self.lineEdit_offline_name_tags.text().strip():
			parameters.log.error(f"The offline name should always be specified when using tags.")
			return False


		if self.checkBox_danbooru.isChecked() or self.checkBox_gelbooru.isChecked() or self.checkBox_rule34.isChecked():
			if not CustomWidgets.confirmation_dialog(self, text=f"Checking for online tags can take a long time depending on multiple factors like your internet connection or the amount of images in your dataset, do you wish to continue ?"):
				return False

		images_paths = files.get_all_images_in_folder(self.db.folder)
		new_paths = self.db.add_images_to_db(
											images_paths,
		                                    move_dupes=self.checkBox_move_duplicates_out_of_folder.isChecked(),
		                                    grouping_from_path=self.checkBox_groups_from_folders.isChecked()
											)
		if not new_paths:
			return False

		if self.checkBox_use_taggers.isChecked():
			self.db.tag_images(new_paths)
		if self.checkBox_use_aesthetic_scorer.isChecked():
			self.db.score_images(new_paths)
		if self.checkBox_use_classifier.isChecked():
			self.db.classify_images(new_paths)

		if self.checkBox_offline_tags.isChecked():
			self.db.add_offline_tags(new_paths, is_sentence=False, do_search_complete_name=self.checkBox_both_names_tags.isChecked(), extension_name=self.lineEdit_offline_extension_tags.text().strip(), source_name=self.lineEdit_offline_name_tags.text().strip())
		if self.checkBox_offline_captions.isChecked():
			self.db.add_offline_tags(new_paths, is_sentence=True, do_search_complete_name=self.checkBox_both_names_captions.isChecked(), extension_name=self.lineEdit_offline_extension_caption.text().strip(), source_name="nothing")

		new_indexes = [self.db.index_of_image_by_image_path(new_path) for new_path in new_paths]

		if self.checkBox_danbooru.isChecked():
			self.db.retrieve_danbooru_tags(new_indexes)
		if self.checkBox_gelbooru.isChecked():
			self.db.retrieve_gelbooru_tags(new_indexes,unsafe=self.checkBox_unsafe_gelbooru.isChecked())
		if self.checkBox_rule34.isChecked():
			self.db.retrieve_rule34_tags(new_indexes,unsafe=self.checkBox_unsafe_rule34.isChecked())

		if self.checkBox_rename_to_md5.isChecked():
			self.db.rename_images_to_md5(new_indexes)

		if self.checkBox_rename_to_png.isChecked():
			self.db.rename_images_to_png(new_indexes)

		if self.checkBox_filter_all_images.isChecked():
			self.db.filter_all()

		parameters.log.info("Finished Adding New Images")

	@Slot()
	def reapply_to_database_button(self):
		if not self.db:
			parameters.log.error("Database not loaded")
			return False


		if self.checkBox_offline_tags.isChecked() and '.' not in self.lineEdit_offline_extension_tags.text():
			parameters.log.error(f"The extension name for offline tags should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_tags.isChecked() and '.' not in self.lineEdit_offline_extension_caption.text():
			parameters.log.error(f"The extension name for offline captions should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_tags.isChecked() and not self.lineEdit_offline_name_tags.text().strip():
			parameters.log.error(f"The offline name should always be specified when using tags.")
			return False


		if self.checkBox_danbooru.isChecked() or self.checkBox_gelbooru.isChecked() or self.checkBox_rule34.isChecked():
			if not CustomWidgets.confirmation_dialog(self, text=f"Checking for online tags can take a long time depending on multiple factors like your internet connection or the amount of images in your dataset, do you wish to continue ?"):
				return False

		images_paths = files.get_all_images_in_folder(self.db.folder)
		if not images_paths:
			return False

		if self.checkBox_use_taggers.isChecked():
			self.db.auto_tag_all_images()
		if self.checkBox_use_aesthetic_scorer.isChecked():
			self.db.score_all_images()
		if self.checkBox_use_classifier.isChecked():
			self.db.classify_all_images()

		if self.checkBox_offline_tags.isChecked():
			self.db.add_offline_tags_all_images(is_sentence=False, do_search_complete_name=self.checkBox_both_names_tags.isChecked(), extension_name=self.lineEdit_offline_extension_tags.text().strip(), source_name=self.lineEdit_offline_name_tags.text().strip())
		if self.checkBox_offline_captions.isChecked():
			self.db.add_offline_tags_all_images(is_sentence=True, do_search_complete_name=self.checkBox_both_names_captions.isChecked(), extension_name=self.lineEdit_offline_extension_caption.text().strip(), source_name="nothing")


		if self.checkBox_danbooru.isChecked():
			self.db.retrieve_danbooru_tags_all_images()
		if self.checkBox_gelbooru.isChecked():
			self.db.retrieve_gelbooru_tags_all_images(unsafe=self.checkBox_unsafe_gelbooru.isChecked())
		if self.checkBox_rule34.isChecked():
			self.db.retrieve_rule34_tags_all_images(unsafe=self.checkBox_unsafe_rule34.isChecked())

		if self.checkBox_rename_to_md5.isChecked():
			self.db.rename_all_images_to_md5()

		if self.checkBox_rename_to_png.isChecked():
			self.db.rename_all_images_to_png()

		if self.checkBox_filter_all_images.isChecked():
			self.db.filter_all()

		parameters.log.info("Finished Reapplying")
