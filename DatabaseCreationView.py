import os

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QFileDialog

import CustomWidgets
from classes.class_database import Database
from interfaces import databaseCreationTab
from resources import parameters, wiki_info, tag_categories
from tools import files
import time

class DatabaseCreationView(QWidget, databaseCreationTab.Ui_Form):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.pushButton_process_all_ckpt_images.clicked.connect(self.load_checkpoint_data)
  
		# connect buttons, the only important aspects
		self.pushButton_open_path.clicked.connect(self.open_file_dialog_button)
		self.pushButton_load_database.clicked.connect(self.load_database_button)
		self.pushButton_create_database.clicked.connect(self.create_database_button)
		self.pushButton_save_database.clicked.connect(self.save_database_button)
		self.pushButton_add_new_images.clicked.connect(self.add_images_to_database_button)
		self.pushButton_reapply_to_database.clicked.connect(self.reapply_to_database_button)
		self.pushButton_reapply_lacking.clicked.connect(self.reapply_to_lacking_database_button)
  
		self.pushButton_prune_duplicate.clicked.connect(self.filter_secondary_dir)
		#self.pushButton_B.clicked.connect(self)
		#self.pushButton_C.clicked.connect(self)
  
		self.db: Database = None

	def db_loaded(self):
		if not self.db:
			parameters.log.error("Database not loaded")
			return False
		return True

	@Slot()
	def open_file_dialog_button(self):
		path = CustomWidgets.path_input_dialog(self)
		self.lineEdit_path.setText(path)

	@Slot()
	def load_database_button(self):
		if not os.path.exists(os.path.join(self.lineEdit_path.text(), parameters.DATABASE_FILE_NAME)):
			parameters.log.error(f"Database doesn't exist in {self.lineEdit_path.text()}")
			return
		parameters.log.info("Loading Database")
		self.db = Database(self.lineEdit_path.text())
		self.db.check_existence_images()
		parameters.log.info(f"Loaded Database with {len(self.db.images)} images")

	@Slot()
	def save_database_button(self):
		if self.db_loaded():
			self.db.save_database()

	def simple_db_and_button_checks(self):
		if self.checkBox_offline_tags.isChecked() and '.' not in self.lineEdit_offline_extension_tags.text():
			parameters.log.error(f"The extension name for offline tags should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_captions.isChecked() and '.' not in self.lineEdit_offline_extension_caption.text():
			parameters.log.error(f"The extension name for offline captions should contain a '.' as it's an extension")
			return False

		if self.checkBox_offline_tags.isChecked() and not self.lineEdit_offline_name_tags.text().strip():
			parameters.log.error(f"The offline name should always be specified when using tags.")
			return False

		confirmation_message="""Checking for online tags can take a long time depending on multiple factors \
  								like your internet connection or the amount of images in your dataset,\
          						do you wish to continue?"""

		if self.checkBox_danbooru.isChecked() or self.checkBox_gelbooru.isChecked() or self.checkBox_rule34.isChecked():
			if not CustomWidgets.confirmation_dialog(self, text=confirmation_message):
				return False

		return True

	def postprocess_model_checkboxes(self, new_indices, new_paths):
		"""calls the relevant functions associated with the checkboxes

		"""
		specified_taggers = []
		if self.checkBox_swinV2.isChecked():
			specified_taggers.append(parameters.AvailableTaggers.SWINV2V3)
		if self.checkBox_caformer.isChecked():
			specified_taggers.append(parameters.AvailableTaggers.CAFORMER)
		if self.checkBox_eva02.isChecked():
			specified_taggers.append(parameters.AvailableTaggers.WDEVA02LARGEV3)

		
  
		self.db.call_models(new_paths,
                      tag_images=self.checkBox_use_taggers.isChecked(), 
                      
                      score_images=self.checkBox_use_aesthetic_scorer.isChecked(),
                      classify_images=self.checkBox_use_classifier.isChecked(),
                      grade_completeness=self.checkBox_use_completeness.isChecked(),
                      detect_people=self.checkBox_detect_people.isChecked(),
                      detect_head=self.checkBox_detect_head.isChecked(),
                      detect_hand=self.checkBox_detect_hand.isChecked(),
                      detect_text=self.checkBox_detect_text.isChecked(),
                      jpeg_artifacts=self.checkBox_detect_jpeg.isChecked(),
                      tag_image_list=specified_taggers
                      )
	
  
		if self.checkBox_offline_tags.isChecked():
			self.db.add_offline_tags(new_paths, is_sentence=False, 
                            do_search_complete_name=self.checkBox_both_names_tags.isChecked(), 
                            extension_name=self.lineEdit_offline_extension_tags.text().strip(), 
                            source_name=self.lineEdit_offline_name_tags.text().strip())
		if self.checkBox_offline_captions.isChecked():
			self.db.add_offline_tags(new_paths, is_sentence=True, 
                            do_search_complete_name=self.checkBox_both_names_captions.isChecked(), 
                            extension_name=self.lineEdit_offline_extension_caption.text().strip(), 
                            source_name="nothing")

		if self.checkBox_danbooru.isChecked():
			self.db.retrieve_danbooru_tags(new_indices)
		if self.checkBox_gelbooru.isChecked():
			self.db.retrieve_gelbooru_tags(new_indices,unsafe=self.checkBox_unsafe_gelbooru.isChecked())
		if self.checkBox_rule34.isChecked():
			self.db.retrieve_rule34_tags(new_indices,unsafe=self.checkBox_unsafe_rule34.isChecked())

		#if self.checkBox_rename_to_md5.isChecked():
		#	self.db.rename_images_to_md5(new_indices)

		if self.checkBox_rename_to_png.isChecked():
			self.db.rename_images_to_png(new_indices)

		if self.checkBox_filter_all_images.isChecked():
			self.db.filter_all()
	
	@Slot()
	def load_checkpoint_data(self):
		parameters.log.debug("Load checkpoint data button pressed")
		# this loads separate databases in the checkpoint folder and process
		folder = self.lineEdit_path.text()
		if not os.path.exists(folder) or not folder.endswith('checkpoint'):
			parameters.log.error("Invalid path or not checkpoint folder")
			return False
		confirmation = CustomWidgets.confirmation_dialog(self, text="Are all taggers checked correctly?, Proceed?")
		if not confirmation:
			return False
		finished = ["p0_p0_Background","p0_p0_SFW_effects","p0_p0_SFW_objects","p0_p2_emotions","p0_p6_clothes","p0_p7_hand_poses"] 	
		first_half = ["p0_p7_nonhuman","p1_p2_extreme_content","p1_p2_extreme_QOH","p1_p3_Accessories",
                "p1_p4_BodyModification","p1_p4_Bondage","p1_p4_Femdom","p1_p4_NSFW_fetish","p1_p4_NSFW_general",
                "p1_p4_NSFW_Netorare"]		

		check = ["p0_p2_emotions","p0_p6_clothes","p0_p7_nonhuman","p1_p2_extreme_content"]
		check = tuple(check)
  
		from collections import Counter
		global_tag_counter = Counter()
		global_rejected_counter = Counter()
		skip_processing = [] #+ finished

		#skip_processing+=first_half
		# check for the "blue skin" tag as it can be a tag introduced when the tagger had the incorrect dataloader
  
		skip_processing = tuple(skip_processing)
		folders = files.get_all_databases_folder(folder)
		ignore_folders = "previous_db"
		# check immediate folder above is checkpoint
		folders = [f for f in folders if os.path.basename(os.path.dirname(f)) == "checkpoint"]
		skipped = [f for f in folders if f.endswith(ignore_folders) or f.endswith(skip_processing)]
		print("skipped",len(skipped) , skipped)
		#folders = [f for f in folders if f not in skipped]
		folders = [f for f in folders if f.endswith(check)]
  
		print("working on",len(folders) , folders)
		
		
		re_tag_char = False
		check_tags = True
		check_caformer = False
		high_token = []
		remove_char_from_rejected = False
		# for each minidatabase, check image existance, rebuild database, then add new images, save, repeat
		# pause if there's any error
		blue_skin_db = []
		t0 = time.time()
		char_tags = set(tag_categories.CHARACTERS_TAG.keys())
		#print(	char_tags) # a set of character names
		#print("yasu (umineko)" in char_tags) # was True
		
		for f in folders:
			parameters.log.info(f"Loading {f}")
			self.db = Database(f)
			self.db.check_existence_images()
			self.db.recheck_image_paths()
			db_counter = Counter()
			# remove and rebuild groups
			self.db.remove_groups()
			self.db.add_image_to_groups_by_path([x.path for x in self.db.images])
			images_paths = files.get_all_images_in_folder(self.db.folder)
			
			if check_caformer:
				# we check for images that are missing caformer tags
				caformer_tag = []
				for img in self.db.images:
					if "Caformer" not in img.auto_tags.names():
						caformer_tag.append(img.path)
				parameters.log.info(f"Missing caformer tags for {len(caformer_tag)} images")
				if caformer_tag:
					self.db.multi_tagger_call(caformer_tag, ["Caformer"])

			# remove rejected characters from rejected, cause for some reason they were removed?
			if remove_char_from_rejected:
				for img in self.db.images:
					subtract_char = [t for t in img.rejected_manual_tags if t in char_tags]
					if subtract_char:
						parameters.log.info(f"Removing {subtract_char}")
						img.rejected_manual_tags -= subtract_char
			
    
				
   
			if re_tag_char:
				tag_char_paths = []
				for img in self.db.images:
					# check if character(s) are tagged
					full_tags = img.get_full_tags().simple_tags()
					if not any([t in tag_categories.CHARACTERS_TAG for t in full_tags]):
						tag_char_paths.append(img.path)
				self.db.multi_tagger_call(tag_char_paths, ["Swinv2v3", "Eva02_largev3"])

   
			if images_paths:
				new_paths = self.db.add_images_to_db(images_paths, grouping_from_path=True, 
                             				move_dupes=True, rename_to_md5=True)
				if new_paths:
					idx_dict = self.db.get_img_path_index_dict()
					new_indexes = [idx_dict[new_path] for new_path in new_paths]
					self.postprocess_model_checkboxes(new_indexes, new_paths)
			
			self.db.check_duplicate_tags_in_manual_rejected()
			self.db.re_apply_threshold()
			self.db.filter_all()
			if check_tags:
				for img in self.db.images:
					#db_counter.update(img.get_full_tags().simple_tags())
					#global_tag_counter.update(img.get_full_tags().simple_tags())
					#global_rejected_counter.update(img.get_rejected_tags().simple_tags())
					global_tag_counter.update(img.full_tags.simple_tags())
     
				#if "blue skin" in db_counter:
				#	blue_skin_db.append((f,db_counter["blue skin"]))
   
			_, report_dict = self.db.generate_report()
   
			if report_dict["token_max"] >= 223:
				high_token.append((f,report_dict["token_max"]))
   
   
			self.db.save_database()
			parameters.log.info(f"Saved Database {f}")
			
		t1 = time.time()
		parameters.log.info("Finished Loading Checkpoint Data")
		parameters.log.info(f"Time taken: {t1-t0}")

		if blue_skin_db:
			parameters.log.info("The following databases have blue skin tag")
			for db, count in blue_skin_db:
				parameters.log.info(f"{db}, {count}")

		if high_token:
			parameters.log.info("The following databases have high token count")
			for db, count in high_token:
				parameters.log.info(f"{db}, {count}")
  
		if check_tags and False:
			# first filter out caformer tags that have a danbooru definition
			total_counter = 0
			for tag, count in global_rejected_counter.most_common():
				if tag in tag_categories.CHARACTERS_TAG:
					#parameters.log.info(f"Character tag in rejected: {tag}, {count}")
					total_counter += count
			parameters.log.info(f"Total count of character tags in rejected: {total_counter}")
			parameters.log.info("*"*10)
			parameters.log.info("Tags without definition")
			wiki_dict = wiki_info.load_wiki_info()
			no_definition = [(tag, count) for tag, count in global_tag_counter.most_common() if tag not in wiki_dict and count > 10]
			for tag, count in no_definition:
				if tag in db_counter:# todo: check if tag is accepted as a tag and not replaced or rejected
					parameters.log.info(f"{tag}, {count}")
			parameters.log.info("*"*10)
		if True:
			# update wiki info
			#t2 = time.time()
			parameters.log.info("Updating wiki info")
			# remove characters
			tag_dict = {tag:count for tag, count in global_tag_counter.most_common() if count > 10}

			tag_txt_filename = "tag_frequency.txt"
			with open(os.path.join(folder, tag_txt_filename), 'w') as f:
				for tag, count in tag_dict.items():
					f.write(f"{count}:{tag}\n")
   
			#wiki_info.save_wiki_info(wiki_info.add_wiki_info(tag_dict.keys(), wiki_info.load_wiki_info()))
			#t3 = time.time()
			#parameters.log.info(f"Time taken (wiki updating): {t3-t2}")
		


	@Slot()
	def create_database_button(self):
		parameters.log.debug("Create database button pressed")
		if not self.simple_db_and_button_checks():
			return False
		folder = self.lineEdit_path.text()
		if not folder:
			parameters.log.error("No folder selected")
			return False
		if not os.path.exists(folder):
			parameters.log.error("Invalid folder path")
			return False
		images_paths = set(files.get_all_images_in_folder(folder, image_ext=parameters.ALL_IMAGES_EXT))
		
		
		

  
		if not images_paths:
			return False
		non_ascii = [p for p in images_paths if not p.isascii()]
		long_paths = [p for p in images_paths if len(p) > 255] # checks for paths longer than 256 cause error on windows
		webp = [p for p in images_paths if p.endswith(".webp")]
		jpe = [p for p in images_paths if p.endswith(".jpe")]
		heavy_processing = [self.checkBox_use_taggers.isChecked(), self.checkBox_use_aesthetic_scorer.isChecked(),
                      self.checkBox_use_classifier.isChecked(),self.checkBox_use_completeness.isChecked(),
                      self.checkBox_detect_people.isChecked(),self.checkBox_detect_head.isChecked(),
                      self.checkBox_detect_hand.isChecked(),self.checkBox_detect_text.isChecked(),
                      self.checkBox_detect_jpeg.isChecked()]		
		if long_paths and any(heavy_processing) and not self.checkBox_rename_to_md5.isChecked():
			parameters.log.error(f"First process file names with MD5 or check filenames. {len(long_paths)} paths exceed 256 char Ex: {long_paths[:min(10, len(long_paths))]}")
			return
		if non_ascii and self.checkBox_detect_jpeg.isChecked():
			parameters.log.error(f"The detect jpeg function uses open CV2 and cannot process non-ascii paths, please rename file to md5 or some simple wording first {non_ascii[:min(10, len(non_ascii))]}")
			return
		if os.path.exists(os.path.join(folder, parameters.DATABASE_FILE_NAME)):
			files.backup_database_file(folder)
			parameters.log.error(f"Database exists in {folder}, database is backedup")
		if webp:
			parameters.log.error(f"{len(webp)} webp image detected, converted to png")
			renamed_webp, new_name_webp, error_webp = files.ext_to_ext(webp, ".webp", ".png")
			images_paths-=set(renamed_webp + error_webp)
			images_paths.update(new_name_webp)
			files.export_images(error_webp, folder)
		if jpe:
			parameters.log.error(f"{len(jpe)} images has the .jpe extension, conveerting to .jpeg")
			renamed_jpe, new_name_jpe, error_jpe = files.ext_to_ext(jpe, ".jpe", ".jpeg")
			images_paths-=set(renamed_jpe + error_jpe)
			images_paths.update(new_name_jpe)
			files.export_images(error_jpe, folder)
		parameters.log.info(f"Creating Database in {folder} with {len(images_paths)} images")
		self.db = Database(folder)
		self.db.add_images_to_db(images_paths, 
                           move_dupes=self.checkBox_move_duplicates_out_of_folder.isChecked(), 
                           grouping_from_path=self.checkBox_groups_from_folders.isChecked(),
                           rename_to_md5=self.checkBox_rename_to_md5.isChecked()
                           )

		all_paths = self.db.get_all_paths()
		new_indexes = self.db.get_all_image_indices()
		
		self.postprocess_model_checkboxes(new_indexes, all_paths)
		parameters.log.info("Finished Creating Database")

	@Slot()
	def add_images_to_database_button(self):
		parameters.log.debug("Add imgs to database button pressed")
		if not (self.simple_db_and_button_checks() and self.db_loaded()):
			return False
		images_paths = files.get_all_images_in_folder(self.db.folder)
		if not images_paths:
			return False
  
		current_paths_set = set(self.db.get_all_paths())
		parameters.log.info(f"Found {len(current_paths_set)} images in database")
		images_paths = [path for path in images_paths if path not in current_paths_set]
		parameters.log.info(f"Adding {len(images_paths)} new images to database")
		new_paths = self.db.add_images_to_db(images_paths,
									move_dupes=self.checkBox_move_duplicates_out_of_folder.isChecked(),
									grouping_from_path=self.checkBox_groups_from_folders.isChecked(),
        							rename_to_md5=self.checkBox_rename_to_md5.isChecked()
        )
		if not new_paths:
			parameters.log.info("No new images added to database")
			return False

		idx_dict = self.db.get_img_path_index_dict()
		new_indexes = [idx_dict[new_path] for new_path in new_paths]

		self.postprocess_model_checkboxes(new_indexes, new_paths)
		parameters.log.info("Finished Adding New Images")

	@Slot()
	def reapply_to_database_button(self):
		parameters.log.debug("reapply database button pressed")
  
		if not (self.simple_db_and_button_checks() and self.db_loaded()):
			return False

		images_paths = files.get_all_images_in_folder(self.db.folder)
		if not images_paths:
			return False

		all_paths = self.db.get_all_paths()
		new_indexes = self.db.get_all_image_indices()
  
		self.postprocess_model_checkboxes(new_indexes, all_paths)
		parameters.log.info("Finished Reapplying")

	@Slot()
	def reapply_to_lacking_database_button(self):
		parameters.log.debug("checking database for untagged images, reapplying model on lacking data")
		if not (self.simple_db_and_button_checks() and self.db_loaded()):
			return False
		images_paths = files.get_all_images_in_folder(self.db.folder)
		if not images_paths:
			return False
		all_paths = self.db.get_all_paths()
		new_indexes = self.db.get_all_image_indices()
		self.postprocess_model_checkboxes(new_indexes, all_paths)
		parameters.log.info("Finished Reapplying")
  
	@Slot()
	def filter_secondary_dir(self):
		parameters.log.debug("Add imgs to database button pressed")
		if not (self.simple_db_and_button_checks() and self.db_loaded()):
			return False

		provided_path = str(self.lineEdit_secondary_dir.text())

		parameters.log.info(f"moving dupes from {provided_path}")
		images_paths = files.get_all_images_in_folder(provided_path)
		if not images_paths:
			return False
  
		current_paths_set = set(self.db.get_all_paths())
		images_paths = [path for path in images_paths if path not in current_paths_set]
		parameters.log.info("checking for exact dupes")
		db_md5_hashes = set(self.db.get_all_original_md5() + self.db.get_all_md5())

		# this checks for near dupes
		all_paths = images_paths + list(current_paths_set)
		
		parameters.log.info("checking for near dupes")
		near_dupes = files.find_near_duplicates(all_paths) # list of 3-valued tuple
		parameters.log.info(f"found {len(near_dupes)} near dupes")
		close_dupes = []
		dupe_pairs = []
		set_path = set(images_paths)
		for res in near_dupes:
			if res[0] in set_path and res[1] in set_path:
				dupe_pairs.append(res[0])
				dupe_pairs.append(res[1])
			elif res[0] in set_path:
				close_dupes.append(res[0])
			elif res[1] in set_path:
				close_dupes.append(res[1])
		close_dupes = set(close_dupes)
		dupe_pairs = [dp for dp in dupe_pairs if dp not in close_dupes]
		print(f"{len(close_dupes)}")
		
		dupe_pair_paths = []
		hard_duplicate_paths = []
		soft_duplicate_paths = []
		for image_path in images_paths:
			image_md5 = files.get_md5(image_path)
			if image_md5 in db_md5_hashes:
				hard_duplicate_paths.append(image_path)
			elif image_path in close_dupes:
				soft_duplicate_paths.append(image_path)
			elif image_path in dupe_pairs:
				dupe_pair_paths.append(image_path)
			else: # don't do anything
				db_md5_hashes.add(image_md5)
	
		if hard_duplicate_paths:
			parameters.log.info("moving hard duplicates found in primary")
			files.export_images(hard_duplicate_paths, provided_path, "DUPLICATES")
		if soft_duplicate_paths:
			parameters.log.info("moving soft duplicate matches found in primary")
			files.export_images(soft_duplicate_paths, provided_path, "SOFT_DUPLICATES")
		if dupe_pair_paths:
			parameters.log.info("moving dupe pairs, similar images in secondary dir, not in primary")
			files.export_images(dupe_pair_paths, provided_path, "DUPLICATE_PAIRS")
		parameters.log.info("finished moving dupes")
	