# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'databaseToolsBase.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QComboBox, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QScrollArea, QSizePolicy, QToolBox, QTreeView,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(309, 528)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.comboBox_selection = QComboBox(Form)
        self.comboBox_selection.setObjectName(u"comboBox_selection")

        self.gridLayout.addWidget(self.comboBox_selection, 0, 1, 1, 2)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 295, 116))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 3)

        self.pushButton_replace = QPushButton(Form)
        self.pushButton_replace.setObjectName(u"pushButton_replace")

        self.gridLayout.addWidget(self.pushButton_replace, 2, 0, 1, 3)

        self.toolBox = QToolBox(Form)
        self.toolBox.setObjectName(u"toolBox")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.page.setGeometry(QRect(0, 0, 284, 260))
        self.gridLayout_2 = QGridLayout(self.page)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_txt_file = QPushButton(self.page)
        self.pushButton_txt_file.setObjectName(u"pushButton_txt_file")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_txt_file.sizePolicy().hasHeightForWidth())
        self.pushButton_txt_file.setSizePolicy(sizePolicy)
        self.pushButton_txt_file.setMinimumSize(QSize(50, 0))

        self.gridLayout_2.addWidget(self.pushButton_txt_file, 8, 0, 1, 1)

        self.checkBox_remove_tags_in_sentence = QCheckBox(self.page)
        self.checkBox_remove_tags_in_sentence.setObjectName(u"checkBox_remove_tags_in_sentence")
        self.checkBox_remove_tags_in_sentence.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_remove_tags_in_sentence, 1, 0, 1, 1)

        self.checkBox_use_separator = QCheckBox(self.page)
        self.checkBox_use_separator.setObjectName(u"checkBox_use_separator")
        self.checkBox_use_separator.setMinimumSize(QSize(50, 0))
        self.checkBox_use_separator.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_use_separator, 3, 0, 1, 1)

        self.pushButton_json_tags_file = QPushButton(self.page)
        self.pushButton_json_tags_file.setObjectName(u"pushButton_json_tags_file")

        self.gridLayout_2.addWidget(self.pushButton_json_tags_file, 9, 0, 1, 1)

        self.checkBox_use_sentence = QCheckBox(self.page)
        self.checkBox_use_sentence.setObjectName(u"checkBox_use_sentence")
        self.checkBox_use_sentence.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_use_sentence, 2, 0, 1, 1)

        self.checkBox_sentence_separator = QCheckBox(self.page)
        self.checkBox_sentence_separator.setObjectName(u"checkBox_sentence_separator")
        self.checkBox_sentence_separator.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_sentence_separator, 0, 0, 1, 1)

        self.checkBox_export_aesthetic_score = QCheckBox(self.page)
        self.checkBox_export_aesthetic_score.setObjectName(u"checkBox_export_aesthetic_score")
        self.checkBox_export_aesthetic_score.setChecked(False)

        self.gridLayout_2.addWidget(self.checkBox_export_aesthetic_score, 4, 0, 1, 1)

        self.lineEdit_main_trigger_tag = QLineEdit(self.page)
        self.lineEdit_main_trigger_tag.setObjectName(u"lineEdit_main_trigger_tag")
        self.lineEdit_main_trigger_tag.setMinimumSize(QSize(50, 0))
        self.lineEdit_main_trigger_tag.setAcceptDrops(True)

        self.gridLayout_2.addWidget(self.lineEdit_main_trigger_tag, 6, 0, 1, 1)

        self.plainTextEdit_secondary_trigger_tags = QPlainTextEdit(self.page)
        self.plainTextEdit_secondary_trigger_tags.setObjectName(u"plainTextEdit_secondary_trigger_tags")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.plainTextEdit_secondary_trigger_tags.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_secondary_trigger_tags.setSizePolicy(sizePolicy1)
        self.plainTextEdit_secondary_trigger_tags.setMinimumSize(QSize(50, 50))
        self.plainTextEdit_secondary_trigger_tags.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.plainTextEdit_secondary_trigger_tags.setBackgroundVisible(False)

        self.gridLayout_2.addWidget(self.plainTextEdit_secondary_trigger_tags, 7, 0, 1, 1)

        self.checkBox_aesthetic_score_in_token_separator = QCheckBox(self.page)
        self.checkBox_aesthetic_score_in_token_separator.setObjectName(u"checkBox_aesthetic_score_in_token_separator")

        self.gridLayout_2.addWidget(self.checkBox_aesthetic_score_in_token_separator, 5, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.pushButton_make_sample_toml = QPushButton(self.page)
        self.pushButton_make_sample_toml.setObjectName(u"pushButton_make_sample_toml")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_make_sample_toml.sizePolicy().hasHeightForWidth())
        self.pushButton_make_sample_toml.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.pushButton_make_sample_toml)

        self.comboBox_toml_resolution = QComboBox(self.page)
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.setObjectName(u"comboBox_toml_resolution")
        sizePolicy.setHeightForWidth(self.comboBox_toml_resolution.sizePolicy().hasHeightForWidth())
        self.comboBox_toml_resolution.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.comboBox_toml_resolution)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 10, 0, 1, 1)

        self.toolBox.addItem(self.page, u"Output Captions/Tags:")
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2.setGeometry(QRect(0, 0, 284, 262))
        self.gridLayout_3 = QGridLayout(self.page_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.pushButton_refresh_tags_from_gelbooru_and_rule34 = QPushButton(self.page_2)
        self.pushButton_refresh_tags_from_gelbooru_and_rule34.setObjectName(u"pushButton_refresh_tags_from_gelbooru_and_rule34")

        self.gridLayout_3.addWidget(self.pushButton_refresh_tags_from_gelbooru_and_rule34, 10, 0, 1, 1)

        self.pushButton_apply_replacement_to_sentence = QPushButton(self.page_2)
        self.pushButton_apply_replacement_to_sentence.setObjectName(u"pushButton_apply_replacement_to_sentence")

        self.gridLayout_3.addWidget(self.pushButton_apply_replacement_to_sentence, 1, 0, 1, 1)

        self.pushButton_export_images = QPushButton(self.page_2)
        self.pushButton_export_images.setObjectName(u"pushButton_export_images")

        self.gridLayout_3.addWidget(self.pushButton_export_images, 12, 0, 1, 1)

        self.pushButton_reset_manual_score = QPushButton(self.page_2)
        self.pushButton_reset_manual_score.setObjectName(u"pushButton_reset_manual_score")

        self.gridLayout_3.addWidget(self.pushButton_reset_manual_score, 8, 0, 1, 1)

        self.pushButton_purge_manual = QPushButton(self.page_2)
        self.pushButton_purge_manual.setObjectName(u"pushButton_purge_manual")

        self.gridLayout_3.addWidget(self.pushButton_purge_manual, 11, 0, 1, 1)

        self.pushButton_auto_classify = QPushButton(self.page_2)
        self.pushButton_auto_classify.setObjectName(u"pushButton_auto_classify")

        self.gridLayout_3.addWidget(self.pushButton_auto_classify, 4, 0, 1, 1)

        self.pushButton_only_tag_characters = QPushButton(self.page_2)
        self.pushButton_only_tag_characters.setObjectName(u"pushButton_only_tag_characters")

        self.gridLayout_3.addWidget(self.pushButton_only_tag_characters, 3, 0, 1, 1)

        self.pushButton_apply_filtering = QPushButton(self.page_2)
        self.pushButton_apply_filtering.setObjectName(u"pushButton_apply_filtering")
        sizePolicy.setHeightForWidth(self.pushButton_apply_filtering.sizePolicy().hasHeightForWidth())
        self.pushButton_apply_filtering.setSizePolicy(sizePolicy)
        self.pushButton_apply_filtering.setMinimumSize(QSize(50, 0))

        self.gridLayout_3.addWidget(self.pushButton_apply_filtering, 0, 0, 1, 1)

        self.pushButton_auto_score = QPushButton(self.page_2)
        self.pushButton_auto_score.setObjectName(u"pushButton_auto_score")

        self.gridLayout_3.addWidget(self.pushButton_auto_score, 5, 0, 1, 1)

        self.pushButton_auto_tag = QPushButton(self.page_2)
        self.pushButton_auto_tag.setObjectName(u"pushButton_auto_tag")
        sizePolicy.setHeightForWidth(self.pushButton_auto_tag.sizePolicy().hasHeightForWidth())
        self.pushButton_auto_tag.setSizePolicy(sizePolicy)
        self.pushButton_auto_tag.setMinimumSize(QSize(50, 0))

        self.gridLayout_3.addWidget(self.pushButton_auto_tag, 2, 0, 1, 1)

        self.pushButton_discard_image = QPushButton(self.page_2)
        self.pushButton_discard_image.setObjectName(u"pushButton_discard_image")

        self.gridLayout_3.addWidget(self.pushButton_discard_image, 13, 0, 1, 1)

        self.lineEdit_tag_highlight = QLineEdit(self.page_2)
        self.lineEdit_tag_highlight.setObjectName(u"lineEdit_tag_highlight")

        self.gridLayout_3.addWidget(self.lineEdit_tag_highlight, 14, 0, 1, 1)

        self.toolBox.addItem(self.page_2, u"Batch Operations:")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setGeometry(QRect(0, 0, 297, 227))
        self.gridLayout_4 = QGridLayout(self.page_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.treeView_favourites = QTreeView(self.page_3)
        self.treeView_favourites.setObjectName(u"treeView_favourites")
        self.treeView_favourites.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView_favourites.setProperty("showDropIndicator", False)
        self.treeView_favourites.setAnimated(True)
        self.treeView_favourites.header().setVisible(False)

        self.gridLayout_4.addWidget(self.treeView_favourites, 0, 0, 1, 1)

        self.lineEdit_edit_favourites = QLineEdit(self.page_3)
        self.lineEdit_edit_favourites.setObjectName(u"lineEdit_edit_favourites")

        self.gridLayout_4.addWidget(self.lineEdit_edit_favourites, 1, 0, 1, 1)

        self.toolBox.addItem(self.page_3, u"Favourite Tags:")

        self.gridLayout.addWidget(self.toolBox, 3, 0, 1, 3)

        self.pushButton_save_database = QPushButton(Form)
        self.pushButton_save_database.setObjectName(u"pushButton_save_database")
        sizePolicy.setHeightForWidth(self.pushButton_save_database.sizePolicy().hasHeightForWidth())
        self.pushButton_save_database.setSizePolicy(sizePolicy)
        self.pushButton_save_database.setMinimumSize(QSize(50, 0))

        self.gridLayout.addWidget(self.pushButton_save_database, 12, 0, 1, 3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_open_in_default_program = QPushButton(Form)
        self.pushButton_open_in_default_program.setObjectName(u"pushButton_open_in_default_program")

        self.horizontalLayout.addWidget(self.pushButton_open_in_default_program)

        self.pushButton_popup_image = QPushButton(Form)
        self.pushButton_popup_image.setObjectName(u"pushButton_popup_image")
        sizePolicy.setHeightForWidth(self.pushButton_popup_image.sizePolicy().hasHeightForWidth())
        self.pushButton_popup_image.setSizePolicy(sizePolicy)
        self.pushButton_popup_image.setMinimumSize(QSize(50, 0))

        self.horizontalLayout.addWidget(self.pushButton_popup_image)


        self.gridLayout.addLayout(self.horizontalLayout, 11, 0, 1, 3)


        self.retranslateUi(Form)

        self.toolBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.comboBox_selection.setToolTip(QCoreApplication.translate("Form", u"Apply to most of the buttons below", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("Form", u"Apply to:", None))
#if QT_CONFIG(tooltip)
        self.scrollArea.setToolTip(QCoreApplication.translate("Form", u"Add a new line to set up a tag replacement rule (not saved by the database)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_replace.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Using the selection combo box at the top, each lines are an independent replacement:</p><p>- only right tags: add tags to the selection</p><p>- only left tags: remove tags from the selection</p><p>- both tags: in images with all tags on the left, remove them and add the right tags</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_replace.setText(QCoreApplication.translate("Form", u"Replace", None))
#if QT_CONFIG(tooltip)
        self.pushButton_txt_file.setToolTip(QCoreApplication.translate("Form", u"create a txt file containing the full tags, same as the first tab", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_txt_file.setText(QCoreApplication.translate("Form", u"Create TXT files", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_tags_in_sentence.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Enable this to remove tags that are included in the sentence. This is to reduce potential duplicates in both the caption and tags.<br/>Example: <br/>caption: &quot;1girl sitting on a chair thinking and contemplating life&quot;<br/>tag: &quot;1girl, solo, chair, sitting, red hair, green eyes, blue shirt&quot;<br/>--&gt; </p><p>caption and a shorter tag list is exported: caption + &quot;solo, red hair, green eyes, blue shirt&quot;</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_tags_in_sentence.setText(QCoreApplication.translate("Form", u"Remove tag if included in sentence", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_separator.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Use the token separator set in the setting. <br/><br/>Useful for separating the trigger words (Kohya based trainers have a &quot;use token separator&quot; option). This allows you to have a variable length trigger word.<br/><br/>if this is enabled, tags in the main and secondary are placed in front of the tags and the token separator is placed to separate it from the rest of the tag.<br/></p><p>The tag order in main trigger tag(s) are unshuffled<br/>The tag order in secondary trigger tag(s) is shuffled<br/>The other tags are shuffled.<br/><br/>Here's an example with &quot;|||&quot; as token separator, 1 main trigger word, and 3 secondary trigger word:  main_trigger tag, secondary_tag_3, secondary_tag_1, secondary_tag_2, |||, rest of the tags, ...</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_separator.setText(QCoreApplication.translate("Form", u"Token Separator", None))
#if QT_CONFIG(tooltip)
        self.pushButton_json_tags_file.setToolTip(QCoreApplication.translate("Form", u"useful for checkpoints, makes a .json with the captions and tags. Exports like the meta_cap.json in Kohya.  You can run the meta_lat creator from Kohya directly on this exported json", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_json_tags_file.setText(QCoreApplication.translate("Form", u"Create .json tag file", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_sentence.setToolTip(QCoreApplication.translate("Form", u"include any sentences/caption in the export.  If no captions were set, they're not added to the exported file(s)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_sentence.setText(QCoreApplication.translate("Form", u"Sentence", None))
#if QT_CONFIG(tooltip)
        self.checkBox_sentence_separator.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Place sentence (caption) infront of the token separator.</p><p>Useful if you want natural language in the front of the tags</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_sentence_separator.setText(QCoreApplication.translate("Form", u"Sentence in Token Separator", None))
#if QT_CONFIG(tooltip)
        self.checkBox_export_aesthetic_score.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Lookup what aesthetic score values map to any quality tags, then export the aesthetic/quality tag with the other tags.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_export_aesthetic_score.setText(QCoreApplication.translate("Form", u"Aesthetic scores", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_main_trigger_tag.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Tags in the main and secondary are placed in front of the other tags. Look at token separator if you want to use token separator with your exporting. You don't need token separator if the count of the trigger tags are constant.</p><p>You can add a * to a tag and it will add all variants to the selection. Example: hole* will add black hole, white hole, sinkhole, whole grain, ...</p><p>The tag order in main trigger tag(s) are unshuffled</p><p>The tag order in secondary trigger tag(s) is shuffled</p><p>The other tags are shuffled.</p><p>Here's an example with no token separator, 1 main trigger word, and 3 secondary trigger word: main_trigger tag, secondary_tag_3, secondary_tag_1, secondary_tag_2, rest of the tags, ...</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_main_trigger_tag.setPlaceholderText(QCoreApplication.translate("Form", u"Main Trigger Tag(s), Separate with \",\"", None))
#if QT_CONFIG(tooltip)
        self.plainTextEdit_secondary_trigger_tags.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Tags in the main and secondary are placed in front of the other tags. Look at token separator if you want to use token separator with your exporting. You don't need token separator if the count of the trigger tags are constant.</p><p><br/></p><p>You can add a * to a tag and it will add all variants to the selection. Example: hole* will add black hole, white hole, sinkhole, whole grain, ...</p><p><br/></p><p>The tag order in main trigger tag(s) are unshuffled</p><p>The tag order in secondary trigger tag(s) is shuffled</p><p>The other tags are shuffled.</p><p><br/></p><p><br/></p><p>Here's an example with no token separator, 1 main trigger word, and 3 secondary trigger word: main_trigger tag, secondary_tag_3, secondary_tag_1, secondary_tag_2, rest of the tags, ...</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.plainTextEdit_secondary_trigger_tags.setPlaceholderText(QCoreApplication.translate("Form", u"Secondary Tag(s), Separated with \",\"", None))
#if QT_CONFIG(tooltip)
        self.checkBox_aesthetic_score_in_token_separator.setToolTip(QCoreApplication.translate("Form", u"Include the quality tags from the aesthetic scores and place them into the main trigger tag section.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_aesthetic_score_in_token_separator.setText(QCoreApplication.translate("Form", u"Aesthetic scores in token separator", None))
#if QT_CONFIG(tooltip)
        self.pushButton_make_sample_toml.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Click on this button to generate a toml that can be used by the trainer to generate the samples. It does some calculations to make a distribution weighted by the &quot;complexity&quot; of the image, and then it samples tags from some images until it fills the sample size (default is 10)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_make_sample_toml.setText(QCoreApplication.translate("Form", u"Generate sample TOML", None))
        self.comboBox_toml_resolution.setItemText(0, QCoreApplication.translate("Form", u"SDXL", None))
        self.comboBox_toml_resolution.setItemText(1, QCoreApplication.translate("Form", u"SD1.5", None))
        self.comboBox_toml_resolution.setItemText(2, QCoreApplication.translate("Form", u"SD1.0", None))
        self.comboBox_toml_resolution.setItemText(3, QCoreApplication.translate("Form", u"Custom", None))

#if QT_CONFIG(tooltip)
        self.comboBox_toml_resolution.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>this defines the base output resolution in the toml (using buckets)</p><p>SDXL: (1024, 1024)</p><p>SD1.5: (768, 768)</p><p>SD1.0: (512, 512)</p><p>Custom Resolution: (modify in setting)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QCoreApplication.translate("Form", u"Output Captions/Tags:", None))
        self.pushButton_refresh_tags_from_gelbooru_and_rule34.setText(QCoreApplication.translate("Form", u"Refresh Tags from rule34 and gelbooru", None))
#if QT_CONFIG(tooltip)
        self.pushButton_apply_replacement_to_sentence.setToolTip(QCoreApplication.translate("Form", u"Currently doesn't do anything, will be implemented later", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_apply_replacement_to_sentence.setText(QCoreApplication.translate("Form", u"Apply Replacement to Sentence", None))
#if QT_CONFIG(tooltip)
        self.pushButton_export_images.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>This will export the selection (check the apply to section above) to a new directory.<br/><br/>A pop up will show up and ask for a directory and a group name</p><p><br/></p><p>If a database doesn't exist in the output location, then a new database is created with the same tags.</p><p><br/></p><p>If a database exists, then the images are exported, and the tags are automatically added to the previously exisiting database under the entered group name.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_export_images.setText(QCoreApplication.translate("Form", u"Export Images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reset_manual_score.setToolTip(QCoreApplication.translate("Form", u"reset all scores that were changed, and if the threshold are changed, will change the scores, without needing to restart the scorer", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reset_manual_score.setText(QCoreApplication.translate("Form", u"Reset manual score", None))
#if QT_CONFIG(tooltip)
        self.pushButton_purge_manual.setToolTip(QCoreApplication.translate("Form", u"remove all manually edited tags and reviewed conflicts", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_purge_manual.setText(QCoreApplication.translate("Form", u"Purge Manual", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_classify.setToolTip(QCoreApplication.translate("Form", u"Use the classifer model and some images will have additional tags for sources if the confidence is high", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_classify.setText(QCoreApplication.translate("Form", u"Auto-classifier", None))
#if QT_CONFIG(tooltip)
        self.pushButton_only_tag_characters.setToolTip(QCoreApplication.translate("Form", u"Use the Swinv2-3 tagger and only extract identified characters", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_only_tag_characters.setText(QCoreApplication.translate("Form", u"Only auto-tag characters", None))
#if QT_CONFIG(tooltip)
        self.pushButton_apply_filtering.setToolTip(QCoreApplication.translate("Form", u"filter the selction", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_apply_filtering.setText(QCoreApplication.translate("Form", u"Apply Filtering", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_score.setToolTip(QCoreApplication.translate("Form", u"use an auto scorer for scoring the image using your preferred scoring method", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_score.setText(QCoreApplication.translate("Form", u"Auto-aesthetic scorer", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_tag.setToolTip(QCoreApplication.translate("Form", u"use an auto tagger for tagging the image using your preferred tagging method", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_tag.setText(QCoreApplication.translate("Form", u"Auto-tagger", None))
#if QT_CONFIG(tooltip)
        self.pushButton_discard_image.setToolTip(QCoreApplication.translate("Form", u"discard the selected images by moving it to the discarded folder", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_discard_image.setText(QCoreApplication.translate("Form", u"Discard Images", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_tag_highlight.setToolTip(QCoreApplication.translate("Form", u"Enter any word and it'll be highlighted in the tag view, separate multiple tags with comma", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_tag_highlight.setPlaceholderText(QCoreApplication.translate("Form", u"Enter text to highlight in tag view", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QCoreApplication.translate("Form", u"Batch Operations:", None))
#if QT_CONFIG(tooltip)
        self.treeView_favourites.setToolTip(QCoreApplication.translate("Form", u"tags that are parts of the favourites, currently it's impossible to add tags to it in the UI", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.lineEdit_edit_favourites.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Type tags separated by commas to the favourites:</p><p>- if the tag is present in the favourites it will remove the tag from the favourites</p><p>- if the tag is not in the favourites it will be added</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_edit_favourites.setPlaceholderText(QCoreApplication.translate("Form", u"add and remove favourite tags (separated by ,)", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), QCoreApplication.translate("Form", u"Favourite Tags:", None))
#if QT_CONFIG(tooltip)
        self.pushButton_save_database.setToolTip(QCoreApplication.translate("Form", u"save the database, this is the only button on this page that saves the database", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_save_database.setText(QCoreApplication.translate("Form", u"Save Database", None))
#if QT_CONFIG(tooltip)
        self.pushButton_open_in_default_program.setToolTip(QCoreApplication.translate("Form", u"open the selected images in the default program or the specified program in the settings", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_open_in_default_program.setText(QCoreApplication.translate("Form", u"Open in default program", None))
#if QT_CONFIG(tooltip)
        self.pushButton_popup_image.setToolTip(QCoreApplication.translate("Form", u"Display the selected image in a separate window", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_popup_image.setText(QCoreApplication.translate("Form", u"Pop-up image", None))
    # retranslateUi

