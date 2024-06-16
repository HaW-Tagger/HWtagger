# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'databaseCreationTab.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1170, 640)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit_path = QLineEdit(Form)
        self.lineEdit_path.setObjectName(u"lineEdit_path")

        self.gridLayout.addWidget(self.lineEdit_path, 0, 0, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_4 = QGroupBox(self.groupBox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_3 = QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.checkBox_gelbooru = QCheckBox(self.groupBox_4)
        self.checkBox_gelbooru.setObjectName(u"checkBox_gelbooru")

        self.gridLayout_3.addWidget(self.checkBox_gelbooru, 1, 0, 1, 1)

        self.checkBox_rule34 = QCheckBox(self.groupBox_4)
        self.checkBox_rule34.setObjectName(u"checkBox_rule34")

        self.gridLayout_3.addWidget(self.checkBox_rule34, 3, 0, 1, 1)

        self.checkBox_unsafe_gelbooru = QCheckBox(self.groupBox_4)
        self.checkBox_unsafe_gelbooru.setObjectName(u"checkBox_unsafe_gelbooru")

        self.gridLayout_3.addWidget(self.checkBox_unsafe_gelbooru, 1, 1, 1, 1)

        self.checkBox_danbooru = QCheckBox(self.groupBox_4)
        self.checkBox_danbooru.setObjectName(u"checkBox_danbooru")

        self.gridLayout_3.addWidget(self.checkBox_danbooru, 0, 0, 1, 2)

        self.checkBox_unsafe_rule34 = QCheckBox(self.groupBox_4)
        self.checkBox_unsafe_rule34.setObjectName(u"checkBox_unsafe_rule34")

        self.gridLayout_3.addWidget(self.checkBox_unsafe_rule34, 3, 1, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_4)

        self.groupBox_5 = QGroupBox(self.groupBox)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy1)
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.checkBox_offline_tags = QCheckBox(self.groupBox_5)
        self.checkBox_offline_tags.setObjectName(u"checkBox_offline_tags")

        self.verticalLayout_6.addWidget(self.checkBox_offline_tags)

        self.checkBox_both_names_tags = QCheckBox(self.groupBox_5)
        self.checkBox_both_names_tags.setObjectName(u"checkBox_both_names_tags")

        self.verticalLayout_6.addWidget(self.checkBox_both_names_tags)

        self.lineEdit_offline_extension_tags = QLineEdit(self.groupBox_5)
        self.lineEdit_offline_extension_tags.setObjectName(u"lineEdit_offline_extension_tags")

        self.verticalLayout_6.addWidget(self.lineEdit_offline_extension_tags)

        self.lineEdit_offline_name_tags = QLineEdit(self.groupBox_5)
        self.lineEdit_offline_name_tags.setObjectName(u"lineEdit_offline_name_tags")

        self.verticalLayout_6.addWidget(self.lineEdit_offline_name_tags)


        self.verticalLayout_3.addWidget(self.groupBox_5)

        self.groupBox_6 = QGroupBox(self.groupBox)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.verticalLayout_8 = QVBoxLayout(self.groupBox_6)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.checkBox_offline_captions = QCheckBox(self.groupBox_6)
        self.checkBox_offline_captions.setObjectName(u"checkBox_offline_captions")

        self.verticalLayout_8.addWidget(self.checkBox_offline_captions)

        self.checkBox_both_names_captions = QCheckBox(self.groupBox_6)
        self.checkBox_both_names_captions.setObjectName(u"checkBox_both_names_captions")

        self.verticalLayout_8.addWidget(self.checkBox_both_names_captions)

        self.lineEdit_offline_extension_caption = QLineEdit(self.groupBox_6)
        self.lineEdit_offline_extension_caption.setObjectName(u"lineEdit_offline_extension_caption")

        self.verticalLayout_8.addWidget(self.lineEdit_offline_extension_caption)


        self.verticalLayout_3.addWidget(self.groupBox_6)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_3 = QGroupBox(Form)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy2)
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.checkBox_use_taggers = QCheckBox(self.groupBox_3)
        self.checkBox_use_taggers.setObjectName(u"checkBox_use_taggers")

        self.verticalLayout_4.addWidget(self.checkBox_use_taggers)

        self.checkBox_use_aesthetic_scorer = QCheckBox(self.groupBox_3)
        self.checkBox_use_aesthetic_scorer.setObjectName(u"checkBox_use_aesthetic_scorer")

        self.verticalLayout_4.addWidget(self.checkBox_use_aesthetic_scorer)

        self.checkBox_use_classifier = QCheckBox(self.groupBox_3)
        self.checkBox_use_classifier.setObjectName(u"checkBox_use_classifier")

        self.verticalLayout_4.addWidget(self.checkBox_use_classifier)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy2.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy2)
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.checkBox_groups_from_folders = QCheckBox(self.groupBox_2)
        self.checkBox_groups_from_folders.setObjectName(u"checkBox_groups_from_folders")

        self.gridLayout_2.addWidget(self.checkBox_groups_from_folders, 3, 0, 1, 2)

        self.checkBox_rename_to_md5 = QCheckBox(self.groupBox_2)
        self.checkBox_rename_to_md5.setObjectName(u"checkBox_rename_to_md5")

        self.gridLayout_2.addWidget(self.checkBox_rename_to_md5, 0, 0, 1, 2)

        self.checkBox_move_duplicates_out_of_folder = QCheckBox(self.groupBox_2)
        self.checkBox_move_duplicates_out_of_folder.setObjectName(u"checkBox_move_duplicates_out_of_folder")

        self.gridLayout_2.addWidget(self.checkBox_move_duplicates_out_of_folder, 2, 0, 1, 2)

        self.checkBox_rename_to_png = QCheckBox(self.groupBox_2)
        self.checkBox_rename_to_png.setObjectName(u"checkBox_rename_to_png")

        self.gridLayout_2.addWidget(self.checkBox_rename_to_png, 1, 0, 1, 2)

        self.checkBox_filter_all_images = QCheckBox(self.groupBox_2)
        self.checkBox_filter_all_images.setObjectName(u"checkBox_filter_all_images")

        self.gridLayout_2.addWidget(self.checkBox_filter_all_images, 4, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.pushButton_reapply_to_database = QPushButton(Form)
        self.pushButton_reapply_to_database.setObjectName(u"pushButton_reapply_to_database")

        self.gridLayout_4.addWidget(self.pushButton_reapply_to_database, 1, 0, 1, 2)

        self.pushButton_add_new_images = QPushButton(Form)
        self.pushButton_add_new_images.setObjectName(u"pushButton_add_new_images")

        self.gridLayout_4.addWidget(self.pushButton_add_new_images, 0, 1, 1, 1)

        self.pushButton_create_database = QPushButton(Form)
        self.pushButton_create_database.setObjectName(u"pushButton_create_database")

        self.gridLayout_4.addWidget(self.pushButton_create_database, 3, 0, 1, 2)

        self.pushButton_load_database = QPushButton(Form)
        self.pushButton_load_database.setObjectName(u"pushButton_load_database")

        self.gridLayout_4.addWidget(self.pushButton_load_database, 0, 0, 1, 1)

        self.pushButton_save_database = QPushButton(Form)
        self.pushButton_save_database.setObjectName(u"pushButton_save_database")

        self.gridLayout_4.addWidget(self.pushButton_save_database, 5, 0, 1, 2)

        self.line_4 = QFrame(Form)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.gridLayout_4.addWidget(self.line_4, 2, 0, 1, 2)

        self.line_5 = QFrame(Form)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.gridLayout_4.addWidget(self.line_5, 4, 0, 1, 2)


        self.gridLayout.addLayout(self.gridLayout_4, 1, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_path.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>The first step in making a database, enter a directory that contains images or contains subdirectories with images. Then select the method of tagging you want to enable (loading tags from an external file, via API, or autotagging), then create the database.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_path.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Database Path", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"External Tag Sources", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Form", u"Retrieve Tags Via API (No guarantee finding tags for all images)", None))
#if QT_CONFIG(tooltip)
        self.checkBox_gelbooru.setToolTip(QCoreApplication.translate("Form", u"Use API to get the tags of images with matching md5 hashes", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_gelbooru.setText(QCoreApplication.translate("Form", u"Check gelbooru", None))
#if QT_CONFIG(tooltip)
        self.checkBox_rule34.setToolTip(QCoreApplication.translate("Form", u"Use API to get the tags of images with matching md5 hashes", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_rule34.setText(QCoreApplication.translate("Form", u"Check rule34.xxx", None))
#if QT_CONFIG(tooltip)
        self.checkBox_unsafe_gelbooru.setToolTip(QCoreApplication.translate("Form", u"Tries to keep only tags that are known by this tagger (all tags are stored but not shown) (mostly exclude non sensical tags)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_unsafe_gelbooru.setText(QCoreApplication.translate("Form", u"Filter gelbooru tags", None))
#if QT_CONFIG(tooltip)
        self.checkBox_danbooru.setToolTip(QCoreApplication.translate("Form", u"Use API to get the tags of images with matching md5 hashes", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_danbooru.setText(QCoreApplication.translate("Form", u"Check danbooru", None))
#if QT_CONFIG(tooltip)
        self.checkBox_unsafe_rule34.setToolTip(QCoreApplication.translate("Form", u"Tries to keep only tags that are known by this tagger (all tags are stored but not shown) (mostly exclude non sensical tags)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_unsafe_rule34.setText(QCoreApplication.translate("Form", u"Filter rule34.xxx tags", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("Form", u"Tags from files", None))
#if QT_CONFIG(tooltip)
        self.checkBox_offline_tags.setToolTip(QCoreApplication.translate("Form", u"Enable this to load tags from a local file in the same directory, usually a .txt file next to the images with the tags", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_offline_tags.setText(QCoreApplication.translate("Form", u"Enable", None))
#if QT_CONFIG(tooltip)
        self.checkBox_both_names_tags.setToolTip(QCoreApplication.translate("Form", u"As an example, enable this to search both \"image_name.txt\" and \"image_name.png.txt\" for \"image_name.png\"", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_both_names_tags.setText(QCoreApplication.translate("Form", u"Search for files with both the image extension and without (only one will be taken)", None))
        self.lineEdit_offline_extension_tags.setText("")
        self.lineEdit_offline_extension_tags.setPlaceholderText(QCoreApplication.translate("Form", u"extension name, example: .txt", None))
        self.lineEdit_offline_name_tags.setPlaceholderText(QCoreApplication.translate("Form", u"name used to identify the source of the tags, example: gpt4-o", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("Form", u"Captions from files", None))
#if QT_CONFIG(tooltip)
        self.checkBox_offline_captions.setToolTip(QCoreApplication.translate("Form", u"Enable this to load captions from a local file in the same directory, usually a .txt or .caption file next to the images with the captions", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_offline_captions.setText(QCoreApplication.translate("Form", u"Enable", None))
#if QT_CONFIG(tooltip)
        self.checkBox_both_names_captions.setToolTip(QCoreApplication.translate("Form", u"As an example, enable this to search both \"image_name.txt\" and \"image_name.png.txt\" for \"image_name.png\"", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_both_names_captions.setText(QCoreApplication.translate("Form", u"Search for files with both the image extension and without (only one will be taken)", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_offline_extension_caption.setToolTip(QCoreApplication.translate("Form", u"enter the extension for the images with the caption. usually a .txt or .caption file", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_offline_extension_caption.setText("")
        self.lineEdit_offline_extension_caption.setPlaceholderText(QCoreApplication.translate("Form", u"extension name, example: .caption", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"Automatic Tagging Tools", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_taggers.setToolTip(QCoreApplication.translate("Form", u"Use the taggers configured in the setting tab to autotag the images", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_taggers.setText(QCoreApplication.translate("Form", u"Use taggers", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_aesthetic_scorer.setToolTip(QCoreApplication.translate("Form", u"Score the images so they can be compared via an aesthetic score.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_aesthetic_scorer.setText(QCoreApplication.translate("Form", u"Use aesthetic scorer", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_classifier.setToolTip(QCoreApplication.translate("Form", u"Use an additional img source classifier and add medium/source tags to imgs above a threshold, useful for checkpoints", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_classifier.setText(QCoreApplication.translate("Form", u"Use classifier", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"Pre&Post tagging options", None))
#if QT_CONFIG(tooltip)
        self.checkBox_groups_from_folders.setToolTip(QCoreApplication.translate("Form", u"automatically assign images to groups, use the parent folder's name for group name", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_groups_from_folders.setText(QCoreApplication.translate("Form", u"Create groups following folder structure", None))
#if QT_CONFIG(tooltip)
        self.checkBox_rename_to_md5.setToolTip(QCoreApplication.translate("Form", u"Updates the filename to the exact md5 hash (post tagging)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_rename_to_md5.setText(QCoreApplication.translate("Form", u"Rename Images to MD5", None))
#if QT_CONFIG(tooltip)
        self.checkBox_move_duplicates_out_of_folder.setToolTip(QCoreApplication.translate("Form", u"move duplicate (matching md5 hash) files to duplicate folder", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_move_duplicates_out_of_folder.setText(QCoreApplication.translate("Form", u"Move duplicate images out of folder", None))
#if QT_CONFIG(tooltip)
        self.checkBox_rename_to_png.setToolTip(QCoreApplication.translate("Form", u"convert image to png (post tagging)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_rename_to_png.setText(QCoreApplication.translate("Form", u"Convert Images to PNG", None))
        self.checkBox_filter_all_images.setText(QCoreApplication.translate("Form", u"Apply tag filter", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reapply_to_database.setToolTip(QCoreApplication.translate("Form", u"Re-applies the tagging/processes below to images currently in the database.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reapply_to_database.setText(QCoreApplication.translate("Form", u"Re-Apply to Database", None))
#if QT_CONFIG(tooltip)
        self.pushButton_add_new_images.setToolTip(QCoreApplication.translate("Form", u"Use this to add new images to a pre-existing database.  Load a database and select the tagging criterions and click on this.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_add_new_images.setText(QCoreApplication.translate("Form", u"Add New Images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_create_database.setToolTip(QCoreApplication.translate("Form", u"Create a database using the enabled settng below.  If nothing is enabled it'll just make a database with the images with no tag/caption assigned to them.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_create_database.setText(QCoreApplication.translate("Form", u"Create Database", None))
#if QT_CONFIG(tooltip)
        self.pushButton_load_database.setToolTip(QCoreApplication.translate("Form", u"Enter a database directory, and this will load any database in the folder.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_load_database.setText(QCoreApplication.translate("Form", u"Load Database", None))
#if QT_CONFIG(tooltip)
        self.pushButton_save_database.setToolTip(QCoreApplication.translate("Form", u"Saves the created or loaded database.", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_save_database.setText(QCoreApplication.translate("Form", u"Save Database", None))
    # retranslateUi

