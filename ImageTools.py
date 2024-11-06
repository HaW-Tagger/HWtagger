import os
import time
from pathlib import Path

import PIL
import PySide6.QtCore as QtCore
import imagesize
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Slot
from PySide6.QtGui import QPixmap, QImageReader, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QListView, QFrame
from tqdm.auto import tqdm

from classes.class_database import Database
from interfaces import image_tools
from resources import parameters
from tools import images, files

REMOVE_EXIF = False
w_font_font = parameters.PARAMETERS['font_name'] 
w_font_size = int(parameters.PARAMETERS['font_size'])
base_font = "font: {w_font}; font-size: {w_font_size};"
COMPATIBLE_IMG_TYPES = ('RGB', 'RGBA', '1', 'L', 'P')

class ImageWidget(QFrame):
    def __init__(self, img1, img2, img1_dim, img2_dim, img_path, max_dim=256,parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setStyleSheet("border: 1px solid black;") 
        self.setAcceptDrops(False)
        self.img_path = img_path
        #self.md5_hash = md5_hash
        self.checkbox = QCheckBox("Save", self)
        self.checkbox.setObjectName("SaveCheck")
        self.checkbox.setChecked(True)
        self.checkbox.setStyleSheet("border: none;")

        self.label1 = QLabel(f"Dim [WxH]: <b>{img1_dim[0]}x{img1_dim[1]}</b>")
        self.label2 = QLabel(f"Dim [WxH]: <b>{img2_dim[0]}x{img2_dim[1]}</b>")
        pixel_count1 = img1_dim[0]*img1_dim[1]
        pixel_count2 = img2_dim[0]*img2_dim[1]
        # 400000 is approximatly 512 x 768, which should be a good size, so anything smaller is in red
        
        style1 = "border: none;" if pixel_count1 < 400000 else "color: red;border: none;"
        style2 = "border: none;" if pixel_count2 < 400000 else "color: red;border: none;"
        self.label1.setStyleSheet(base_font + style1)
        self.label2.setStyleSheet(base_font + style2)

        self.img1_container = QLabel()
        self.img1_container.setMinimumSize(max_dim, max_dim)
        self.img1_container.setPixmap(img1)
        self.img2_container = QLabel()
        self.img2_container.setMinimumSize(max_dim, max_dim)
        self.img2_container.setPixmap(img2)
        # add images here

        layout.addWidget(self.checkbox, 0,0)
        layout.addWidget(self.label1, 0, 1)
        layout.addWidget(self.img1_container, 1, 1)
        layout.addWidget(self.label2, 0,2)
        layout.addWidget(self.img2_container, 1, 2)

        self.setLayout(layout)
        self.setToolTip(f"{self.img_path}") #nmd5 hash: {self.md5_hash}
       

class ImageToolsView(QWidget, image_tools.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.database = None
        self.directory = ""
        self.bad_imgs = []
        self.image_paths = []
        self.md5_hashes = []
        self.md5_to_dir = {}
        self.previous_index = -1
        self.max_length = 256
        
        self.duplicate_paths = [] # list of (new img, old img already added)
        
        # set a pixel limit
        self.pix_limit = 4000*4000*parameters.PARAMETERS["max_4k_pixel_save_multiplier"]
        self.current_pix_count = 0
        self.image_cache = dict()
        self.image_index = dict()

        self.ocr_loaded = False
        self.ocr_bboxes = dict()

        self.progress_freq = 0.2 # primt 10%, set to 1 if you don't need progress
        self.next_index = 0

        self.model = QStandardItemModel()
        self.ImageList.setViewMode(QListView.ViewMode.ListMode)
        self.ImageList.setUniformItemSizes(True)
        self.ImageList.setModel(self.model)
        self.ImageList.setFlow(QListView.Flow.LeftToRight)
        self.ImageList.setWrapping(True)
        self.ImageList.setResizeMode(QListView.ResizeMode.Adjust)


        self.LoadDirectory.clicked.connect(self.load_directory)
        self.ProcessImages.clicked.connect(self.load_images)
        self.SaveImages.clicked.connect(self.save_images)
        self.NextPage.clicked.connect(self.load_next_page)
        #self.printDupes.clicked.connect(self.print_duplicate_imgs)
        #self.deleteDupes.clicked.connect(self.delete_duplicate_imgs)
        self.checkImgSize.clicked.connect(self.check_image_size)
        self.exportSmall.clicked.connect(self.export_bad_imgs_button)
        self.checkImageType.clicked.connect(self.check_corrupted)
        self.pushButton_process_all.clicked.connect(self.process_all_images)
        #self.printSimilarImages.clicked.connect(self.find_similar_images)
        
        #todo : this is temp, for now using OCR
        #self.pushButton_fakedb.clicked.connect(self.make_fake_db)
        
    def make_fake_db(self):
        dir_text = self.DirectoryText.text()
        if dir_text and not os.path.exists(os.path.join(dir_text, parameters.DATABASE_FILE_NAME)):
            self.database = Database(dir_text)
            self.database.add_images_to_db(files.get_all_images_in_folder(dir_text))
            
            x = len(self.database.images)
            parameters.log.info(("db_len", x))
            
            from imgutils.ocr import detect_text_with_ocr
            from PIL import Image 
            
            start_time = time.time()
            mx_worker = parameters.PARAMETERS["max_images_loader_thread"]
            for img in tqdm(self.database.images):
                image = Image.open(img.path).convert("RGB")
                image.thumbnail((768, 768))
                bbox = detect_text_with_ocr(image, max_candidates=6)
                if bbox:
                    img.append_manual_tags(["bbox"+str(i) for i in range(len(bbox))])
            parameters.log.info(f"Images loaded in {round(time.time() - start_time, 3)} seconds")
            self.database.save_database()
        else:
            parameters.log.warn("This method is for when there's no database in this dir")
    
    @Slot()
    def load_directory(self):
        self.label_2.setText(f"<b>Images: (Before & After)<\b>")
        self.directory = self.DirectoryText.text()
        self.refresh_variables()
        self.duplicate_paths = []
        full_img_list = []
        self.md5_to_dir = dict()
        if self.directory:
            parameters.log.info("Loading directory")
            full_img_list = files.get_all_images_in_folder(self.directory)
            if os.path.exists(os.path.join(self.directory, parameters.DATABASE_FILE_NAME)):
                parameters.log.info("Loading database for MD5 Hashes")
                self.database = Database(self.directory)
                db_loaded = len(self.database.images)
                db_md5_list = self.database.get_all_md5()
                db_dir_list = self.database.get_all_paths()
            else:
                self.database = None
                db_loaded = False
            
            for image_path in full_img_list:
                md5_img = files.get_md5(Path(image_path))
                new_img = True
                if db_loaded:
                    if md5_img in db_md5_list:
                        db_index = db_md5_list.index(md5_img)
                        dir_in_db = db_dir_list[db_index]
                        if dir_in_db != image_path: # the dir and md5 matches so we use this one
                            if dir_in_db.lower() == image_path.lower():
                                parameters.log.info("Upper and lower mix up, save newer path")
                                self.database.images[db_index].path = image_path
                                image_ext = os.path.splitext(image_path)[1]
                            else:
                                new_img = False
                if  new_img and md5_img not in self.md5_to_dir:
                    self.md5_to_dir[md5_img] = image_path
                    self.image_paths.append(image_path)
                    self.md5_hashes.append(md5_img)
                elif md5_img in self.md5_to_dir:
                    parameters.log.debug((new_img, md5_img, image_path))
                    self.duplicate_paths.append((image_path, self.md5_to_dir[md5_img]))
                else:
                    self.duplicate_paths.append((image_path, "NA"))
            duplicate_counts = len(self.duplicate_paths)
            duplicates = [d[0] for d in self.duplicate_paths]
            files.export_images(duplicates, self.directory, "DUPLICATES")
            self.duplicate_paths = []
            if duplicate_counts > 0:
                parameters.log.info(f"Found {len(self.image_paths)} images in the loaded directory, {duplicate_counts} duplicates ignored")
            else:
                parameters.log.info(f"Found {len(self.image_paths)} images in the loaded directory")
        else:
            parameters.log.error("No directory Entered")



    @Slot()
    @images.timing
    def load_images(self):
        parameters.log.info("Processing images")
        convert_transparent = self.ConvertTransparent.isChecked()
        crop_edge = self.CropEdge.isChecked()
        crop_border = self.CropBorder.isChecked()
        highlight_cropped_text = True
        self.image_cache = dict()
        
        parameters.log.info("Loading images")

        image_paths = files.get_all_images_in_folder(self.directory)
      
        final_index = len(image_paths)-1
        
        
        
        for i, img_path in enumerate(image_paths):
            if i > self.previous_index: # we use previous index to avoid recomputation
                self.previous_index = i
                original_img, new_img, cropped, filled, bboxes = images.border_transparency(
                                    img_path, crop_empty_space=crop_edge, crop_empty_border=crop_border,
                                    fill_stray_signature=False,use_thumbnail=False)
                if cropped or filled:
                    self.image_cache[img_path] = new_img
                   
                    if False:
                        # handle making thumbnail of image pre-edit
                        image = QImageReader(img_path)
                        h, w = image.size().height(), image.size().width()
                        image_ratio = w/h
                        if image_ratio >= 1:
                            max_size = QtCore.QSize(self.max_length, self.max_length / image_ratio)
                        else:
                            max_size = QtCore.QSize(self.max_length * image_ratio, self.max_length)
                        image.setScaledSize(max_size)
                        icon = QPixmap(image.read())
                    else:
                        if bboxes: # if there's text on the img, we have a boundary box that is drawn on the original img
                            draw = PIL.ImageDraw.Draw(original_img)
                            for bbox in bboxes:
                                draw.rectangle(bbox[0], outline="red")
                          
                        o_size = original_img.size
                        w, h = o_size[0], o_size[1]
                        o_scale_factor = min(256/w, 256/h)
                        scaled_original = original_img.resize((int(w*o_scale_factor), int(h*o_scale_factor)))
                        if scaled_original.mode not in COMPATIBLE_IMG_TYPES:
                            scaled_original = scaled_original.convert("RGBA")
                        o_img = ImageQt(scaled_original)
                        icon = QPixmap.fromImage(o_img)
                        
                    # handles thumbnailing edited image
                    new_size = new_img.size # width, height, channel
                    self.current_pix_count += new_size[0] * new_size[1]
                    scale_factor = min(256/new_size[0], 256/new_size[1])
                    parameters.log.debug(scale_factor)
                    new_resized_image = new_img.resize((int(new_size[0]*scale_factor), int(new_size[1]*scale_factor)))

                    qim = ImageQt(new_resized_image)
                    new_icon = QPixmap.fromImage(qim)

                    customwidget = ImageWidget(icon, new_icon, (w, h), (new_size[0], new_size[1]), 
                                            img_path, self.max_length)
                    item = QStandardItem()
                    item.setSizeHint(customwidget.sizeHint())
                    self.model.appendRow(item)
                    self.ImageList.setIndexWidget(item.index(), customwidget)

                    # check if we need to stop processing, for memory reasons
                    if i < final_index and self.current_pix_count > self.pix_limit:
                        self.current_pix_count = 0
                        self.NextPage.setEnabled(True)
                        break
                
        self.label_2.setText(f"<b>Images: (Before & After)<\b> Showing {len(self.image_cache)} images, processed {self.previous_index+1}/{len(self.image_paths)}")

        parameters.log.info("finished loading imgs")


    @Slot()
    def refresh_model(self):
        #self.label_2.setText(f"<b>Images: (Before & After)<\b>")
        self.model.clear()
        self.ImageList.repaint()

    def refresh_variables(self):
        self.database = None
        self.refresh_model()
        self.image_paths = []
        self.md5_hashes = []
        self.md5_to_dir = {}
        self.duplicate_dir = []
        self.previous_index = -1
        self.current_pix_count = 0
        
    @Slot()
    def load_next_page(self):
        self.refresh_model()
        self.NextPage.setEnabled(False)
        self.load_images()

    @Slot()
    def save_images(self):
        parameters.log.info("Saving images")
        update_db = self.updateDB.isChecked()
        check_list = self.get_checks()
        if check_list:
            db_loaded = 0
            db_dir_list = []
            if self.database:
                db_loaded = len(self.database.images)
                db_dir_list = self.database.get_all_paths()
            parameters.log.info((db_loaded, update_db, "database loaded"))
            for img_path, check_val in tqdm(check_list):
                if check_val:
                    # a pillow object
                    img_pil = self.image_cache[img_path]
                    if self.OverrideOriginal.isChecked():
                        img_pil.save(img_path)
                        if db_loaded and update_db:
                            md5_img = files.get_md5(Path(img_path))
                            db_index = db_dir_list.index(img_path)
                            self.database.images[db_index].md5 = md5_img
                    else:
                        filename, file_ext = os.path.splitext(img_path)
                        edit_indicator = "_post_edit"
                        img_pil.save(filename + edit_indicator + file_ext)
            checks = [c[1] for c in check_list]
            
            if db_loaded and update_db:
                parameters.log.info("Saving and updating db")
                self.database.save_database()
            
            write_method = "OVERRIDE" if self.OverrideOriginal.isChecked() else "RENAME & SAVE EDIT"
            parameters.log.info(f"Done, saved {checks.count(True)} images, method: {write_method}")
            self.image_cache = []
            self.refresh_model()
            
            
        else:
            parameters.log.error("No images processed or to be saved")
    @Slot()
    def get_checks(self):
        # iterate through the current view and get the checkbox value
        check_list = []
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            custom_widget = self.ImageList.indexWidget(index)
            checkbox = custom_widget.findChild(QCheckBox, "SaveCheck")
            checkbox_value = checkbox.isChecked()
            check_list.append([custom_widget.img_path, checkbox_value])
        return check_list
    
    @Slot()
    def print_duplicate_imgs(self):
        if self.duplicate_dir: # dir is loaded, and dupes exists
            parameters.log.info("Printing duplicate image pairs:")
            for dupe_1, dupe_2 in self.duplicate_dir:
                parameters.log.info(dupe_1, dupe_2)
        elif self.directory: # no dupe, but dir is loaded
            parameters.log.info(f"No duplicates found in {self.directory}")
        else: # no dir is loaded
            parameters.log.error("No directory loaded")

    @Slot()
    def find_similar_images(self):
        if self.image_paths:
            images.similarity_example(self.image_paths)
        else:
           parameters.log.error("No image paths found") 
    
    @Slot()
    def delete_duplicate_imgs(self):
        # potentially add a dataset check for matching dir
        if self.duplicate_dir: # we have dupes
            parameters.log.info(f"Deleting duplicate images in directory: {self.directory}")
            for dupe_1, dupe_2 in self.duplicate_dir:
                os.remove(dupe_1)
                parameters.log.info(f"Deleting {dupe_1}")
        elif self.directory: # directory is loaded, but no dupes
            parameters.log.info(f"No duplicates to delete in {self.directory}")
        else: # no directory was loaded
            parameters.log.erro("No directory Loaded")
    
    def process_all_images(self):
        from CustomWidgets import confirmation_dialog
        if confirmation_dialog(self, "Process all Images in directory? This doesn't update database"):
            image_paths = files.get_all_images_in_folder(self.directory)
            crop_edge = self.CropEdge.isChecked()
            crop_border = self.CropBorder.isChecked()
            update_db = self.updateDB.isChecked()
            db_loaded = 0
            db_dir_list = []
            #if self.database:
            #    db_loaded = len(self.database.images)
            #    db_dir_list = self.database.get_all_paths()
            parameters.log.info((db_loaded, update_db, "database loaded"))
            only_cropped = 0
            only_filled = 0
            both_crop_fill = 0
            #parameters.log.info(image_paths[7099:7101])
            overwrite = self.OverrideOriginal.isChecked()
            
                
            parameters.log.info("Using (NOT) multi-thread to process images")
            start = time.time()
            #pool = concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"])
            for img_path in tqdm(image_paths):
                _, new_img, cropped, filled, _ = images.border_transparency(
                                            img_path, crop_empty_space=crop_edge, crop_empty_border=crop_border,
                                            fill_stray_signature=False,use_thumbnail=False)
                
                if cropped or filled:
                    if cropped and filled:
                        both_crop_fill+=1
                    elif cropped:
                        only_cropped+=1
                    elif filled:
                        only_filled+=1
                    
                    if overwrite:
                        new_img.save(img_path)
                        # add db stuff here
                    else:
                        filename, file_ext = os.path.splitext(img_path)
                        edit_indicator = "_post_edit"
                        new_img.save(filename + edit_indicator + file_ext)
            #pool.shutdown(wait=True)
            parameters.log.info(f"Multi-thread taken {time.time()-start} seconds")
            parameters.log.info(f"Processed {len(image_paths)}, filled {only_filled} images, cropped {only_cropped} images, applied both on {both_crop_fill} images")
            #if db_loaded and update_db:
            #    parameters.log.info("Saving and updating db")
            #    self.database.save_database()
            
    def check_image_size(self): # you can bypass the loading if you have a text in the field
        if self.directory or self.DirectoryText.text():
            self.bad_imgs = []
            self.resize_imgs = []
            small_images = []
            bad_ratio_images = []
            min_size = 768 * 1024
            
            max_size = 94844500 # value for decompression bomb warning
            index = 0
            ratio_index = 0
            directory = self.directory if self.directory else self.DirectoryText.text()
            for img_path in files.get_all_images_in_folder(directory):
                width, height = imagesize.get(img_path)
                pix_val = width*height
                hw_ratio = height/width
                wh_ratio = width/height
                thresh_ratio = 2.6
                if pix_val < min_size:
                    small_images.append([img_path, (width, height)])
                    if index < 10:
                        parameters.log.info((index, img_path, (width, height)))
                        if index == 10:
                            parameters.log.info("...")
                    index +=1
                elif thresh_ratio < hw_ratio or thresh_ratio < wh_ratio:
                    bad_ratio_images.append([img_path, (width, height)])
                    if ratio_index < 10:
                        parameters.log.info((ratio_index, img_path, (width, height)))
                        if ratio_index == 10:
                            parameters.log.info("...")
                    ratio_index +=1
                elif pix_val > max_size:
                    parameters.log.warn((index, img_path, (width, height), "potential Decompression Bomb"))
            if small_images:
                parameters.log.info(f"Found {len(small_images)} images that is below the recommended size for XL training.")
            if bad_ratio_images:
                parameters.log.info(f"Found {len(bad_ratio_images)} images that is too tall/wide for tagging")
            self.bad_imgs = small_images
            self.resize_imgs = bad_ratio_images
            if not small_images and not bad_ratio_images:
                parameters.log.info("No bad images found based on size")
        else:
            parameters.log.error("No valid directory was loaded")
    
    def export_bad_imgs_button(self):
        self.export_bad_imgs(self.bad_imgs)
        self.export_bad_imgs(self.resize_imgs, export_loc="ADJUST_RATIO")
        self.resize_imgs = []
        self.bad_imgs = []
    
    def export_bad_imgs(self, bad_imgs, export_loc="DISCARDED"):
        if bad_imgs:
            directory = self.directory if self.directory else self.DirectoryText.text()
            bad_imgs = [b[0] if (type(b) is tuple or type(b) is list) else b for b in bad_imgs]
            parameters.log.info(bad_imgs)
            files.export_images(bad_imgs, directory,export_loc)
            if self.database:
                parameters.log.info(f"Removing {len(bad_imgs)} images from database")
                self.database.remove_images_by_path(bad_imgs)
                
        else:
            parameters.log.info("No images to export")

    def check_bad_images(self, directory):
        remove_exif = REMOVE_EXIF
        bs = 8
        # first check for corrupted images
        parameters.log.info(f"Checking for bad images, using batch {bs}, loading up dataloader")
        corrupted_images = images.get_corrupted_images(directory, bs, remove_exif)
        corrupted_images = [(p, "error") for p in corrupted_images]
        if corrupted_images: # check for bad images
            parameters.log.info("Here's the list of bad images not used")
            for i, f in enumerate(corrupted_images):
                parameters.log.info(i, f)
            parameters.log.info("Cannot Identify image file --> it's probably a 32bit 4 channel image or a img type not supported by pillow, open and save on any image editing program to solve issue")
            parameters.log.info("Image file is truncated --> CHECK YOUR IMAGES, the images might end abruptly, no fix")
            parameters.log.info("Corrupted EXIF can be ignore since it doesn't affect the actual image data. There's no easy way to identify it.")
            self.export_bad_imgs(corrupted_images)
            
           
        else:
            parameters.log.info("The directory has no corrupted data")
        return corrupted_images
    
      
    def check_dupe_md5(self, dupe_paths):
        if dupe_paths: # check for duplicate md5
            self.export_bad_imgs(dupe_paths)
            if self.database:
                pass
                # todo : remove images by the list of bad paths
        return dupe_paths
        
    def lowercase_all_extensions(self, directory):
        # lowercase all image extensions and update database if needed
        file_names = files.get_all_images_in_folder(directory)
        file_name_ext = [os.path.splitext(p) for p in file_names]
        lowercased = 0
        db_ordered_paths = self.database.get_all_paths() if self.database else []
        for f, ext in file_name_ext:
            f_name = f+ext
            if ext != ext.lower():
                new_path = f+ext.lower()
                os.rename(f_name, new_path)
                lowercased +=1
                if f_name in db_ordered_paths:
                    index = db_ordered_paths.index(f_name)
                    self.database.images[index].path = new_path
                    self.database.images[index].md5 = files.get_md5(new_path)
                    image_ext = os.path.splitext(new_path)[1]
        if lowercased:
            parameters.log.info(f"Lowercased {lowercased} extensions in {directory}")
      
    def check_dupe_base_filename(self, directory):
        image_paths = files.get_all_images_in_folder(directory)
        if image_paths:
            paths_split_ext = [os.path.splitext(p) for p in image_paths]
            path_no_ext = [p[0] for p in paths_split_ext]
                # check for duplicate named files (a problem cause one txt file is gonna stay and others are overwritten)
            renamed_counter = 0
            modified_db = False
            if len(set(path_no_ext)) != len(paths_split_ext):
                dupes = files.get_duplicate_string(path_no_ext)
                db_paths = set(self.database.get_all_paths() if self.database else [])
                
                
                for dupe_name in dupes:
                    dupe_paths = [p for p in paths_split_ext if p[0] == dupe_name]
                    # add the ones in the db first, then the ones not in db (db imgs takes priority)
                    dupe_ordered = [p for p in dupe_paths if p in db_paths]
                    dupe_ordered.extend([p for p in dupe_paths if p not in dupe_ordered])
                
                    for i, dp in enumerate(dupe_ordered):
                        if i > 0: # except for the first, rename it 
                            old_path = dp[0]+dp[1]
                            new_path = dp[0] + "_dupe" + str(i) + dp[1]
                            renamed_counter+=1
                            os.rename(old_path, new_path)
                            if old_path in db_paths: # update path in database
                                index = self.database.index_of_image_by_image_path(old_path)
                                self.database.images[index].path = new_path
                if renamed_counter: 
                    if modified_db: # renamed + modified db
                        parameters.log.info(f"Renamed {renamed_counter} images for duplicate names with different extensions (auto renamed in databased)")
                    elif self.database: # renamed, but no matching path in loaded db
                        parameters.log.info(f"Renamed {renamed_counter} images for duplicate names with different extensions (No matching imgs found in database, forgot to add to db?)")
                    else: # renamed and no db was loaded
                        parameters.log.error(f"Renamed {renamed_counter} images for duplicate names with different extensions")
    
    def check_corrupted(self): # convert, print, move bad images
        directory = self.directory if self.directory else self.DirectoryText.text()
        self.bad_imgs = []
        removed_files = []
        if directory:
            if self.checkDupeHash.isChecked() and not(self.database or (self.image_paths or self.duplicate_dir)):
                parameters.log.error("To check for hashes and other bad images, please load the directory")
            else:
                # check bad images
                removed = self.check_bad_images(directory)
                removed_files.extend(removed)
                
                # move files that don't belong here based on extensions
                animated_ext = (".mp4", ".gif", ".MP4", ".GIF")
                animated_files = files.get_all_images_in_folder(directory, animated_ext)
                self.export_bad_imgs(animated_files, "DISCARDED_ANIMATION")
                
                # second check for duplicate md5
                if self.checkDupeHash.isChecked():
                    self.duplicate_paths = [p for p in self.duplicate_paths if p not in removed_files]
                    removed = self.check_dupe_md5(self.duplicate_paths)
                    removed_files.extend(removed)
                    self.duplicate_paths = []
                else:
                    parameters.log.info("Skipping Hash dupe check")
                
                # check for duplicate names with different extensions, and rename them
                self.check_dupe_base_filename(directory)
            
                # lowercase all extensions
                self.lowercase_all_extensions(directory)
                parameters.log.info("Done checking/moving/renaming for bad images")
                if self.database:
                    self.database.reapply_md5()
                    self.database.save_database()
        else:
            parameters.log.error("Enter a directory")