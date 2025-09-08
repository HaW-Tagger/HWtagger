# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'outputBase.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QComboBox,
    QGridLayout, QLineEdit, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(453, 795)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.checkBox_use_separator = QCheckBox(Form)
        self.checkBox_use_separator.setObjectName(u"checkBox_use_separator")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_use_separator.sizePolicy().hasHeightForWidth())
        self.checkBox_use_separator.setSizePolicy(sizePolicy)
        self.checkBox_use_separator.setMinimumSize(QSize(50, 0))
        self.checkBox_use_separator.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_use_separator, 0, 1, 1, 1)

        self.checkBox_trigger_tags = QCheckBox(Form)
        self.checkBox_trigger_tags.setObjectName(u"checkBox_trigger_tags")
        sizePolicy.setHeightForWidth(self.checkBox_trigger_tags.sizePolicy().hasHeightForWidth())
        self.checkBox_trigger_tags.setSizePolicy(sizePolicy)
        self.checkBox_trigger_tags.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_trigger_tags, 0, 0, 1, 1)

        self.checkBox_sentence_separator = QCheckBox(Form)
        self.checkBox_sentence_separator.setObjectName(u"checkBox_sentence_separator")
        sizePolicy.setHeightForWidth(self.checkBox_sentence_separator.sizePolicy().hasHeightForWidth())
        self.checkBox_sentence_separator.setSizePolicy(sizePolicy)
        self.checkBox_sentence_separator.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_sentence_separator, 1, 1, 1, 1)

        self.checkBox_aesthetic_score_in_token_separator = QCheckBox(Form)
        self.checkBox_aesthetic_score_in_token_separator.setObjectName(u"checkBox_aesthetic_score_in_token_separator")
        sizePolicy.setHeightForWidth(self.checkBox_aesthetic_score_in_token_separator.sizePolicy().hasHeightForWidth())
        self.checkBox_aesthetic_score_in_token_separator.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.checkBox_aesthetic_score_in_token_separator, 3, 1, 1, 1)

        self.checkBox_use_sentence = QCheckBox(Form)
        self.checkBox_use_sentence.setObjectName(u"checkBox_use_sentence")
        sizePolicy.setHeightForWidth(self.checkBox_use_sentence.sizePolicy().hasHeightForWidth())
        self.checkBox_use_sentence.setSizePolicy(sizePolicy)
        self.checkBox_use_sentence.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_use_sentence, 1, 0, 1, 1)

        self.checkBox_remove_tags_in_sentence = QCheckBox(Form)
        self.checkBox_remove_tags_in_sentence.setObjectName(u"checkBox_remove_tags_in_sentence")
        self.checkBox_remove_tags_in_sentence.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_remove_tags_in_sentence, 2, 0, 1, 2)

        self.checkBox_export_aesthetic_score = QCheckBox(Form)
        self.checkBox_export_aesthetic_score.setObjectName(u"checkBox_export_aesthetic_score")
        sizePolicy.setHeightForWidth(self.checkBox_export_aesthetic_score.sizePolicy().hasHeightForWidth())
        self.checkBox_export_aesthetic_score.setSizePolicy(sizePolicy)
        self.checkBox_export_aesthetic_score.setChecked(False)

        self.gridLayout.addWidget(self.checkBox_export_aesthetic_score, 3, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.lineEdit_main_trigger_tag = QLineEdit(Form)
        self.lineEdit_main_trigger_tag.setObjectName(u"lineEdit_main_trigger_tag")
        self.lineEdit_main_trigger_tag.setMinimumSize(QSize(50, 0))
        self.lineEdit_main_trigger_tag.setAcceptDrops(True)

        self.verticalLayout.addWidget(self.lineEdit_main_trigger_tag)

        self.plainTextEdit_secondary_trigger_tags = QPlainTextEdit(Form)
        self.plainTextEdit_secondary_trigger_tags.setObjectName(u"plainTextEdit_secondary_trigger_tags")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.plainTextEdit_secondary_trigger_tags.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_secondary_trigger_tags.setSizePolicy(sizePolicy1)
        self.plainTextEdit_secondary_trigger_tags.setMinimumSize(QSize(50, 50))
        self.plainTextEdit_secondary_trigger_tags.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.plainTextEdit_secondary_trigger_tags.setBackgroundVisible(False)

        self.verticalLayout.addWidget(self.plainTextEdit_secondary_trigger_tags)

        self.checkBox_current_group = QCheckBox(Form)
        self.checkBox_current_group.setObjectName(u"checkBox_current_group")

        self.verticalLayout.addWidget(self.checkBox_current_group)

        self.pushButton_txt_file = QPushButton(Form)
        self.pushButton_txt_file.setObjectName(u"pushButton_txt_file")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_txt_file.sizePolicy().hasHeightForWidth())
        self.pushButton_txt_file.setSizePolicy(sizePolicy2)
        self.pushButton_txt_file.setMinimumSize(QSize(50, 0))

        self.verticalLayout.addWidget(self.pushButton_txt_file)

        self.pushButton_json_tags_file = QPushButton(Form)
        self.pushButton_json_tags_file.setObjectName(u"pushButton_json_tags_file")

        self.verticalLayout.addWidget(self.pushButton_json_tags_file)

        self.pushButton_create_jsonl = QPushButton(Form)
        self.pushButton_create_jsonl.setObjectName(u"pushButton_create_jsonl")

        self.verticalLayout.addWidget(self.pushButton_create_jsonl)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, -1, -1, 0)
        self.pushButton_make_sample_toml = QPushButton(Form)
        self.pushButton_make_sample_toml.setObjectName(u"pushButton_make_sample_toml")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pushButton_make_sample_toml.sizePolicy().hasHeightForWidth())
        self.pushButton_make_sample_toml.setSizePolicy(sizePolicy3)

        self.gridLayout_6.addWidget(self.pushButton_make_sample_toml, 0, 0, 1, 1)

        self.comboBox_toml_resolution = QComboBox(Form)
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.setObjectName(u"comboBox_toml_resolution")
        sizePolicy2.setHeightForWidth(self.comboBox_toml_resolution.sizePolicy().hasHeightForWidth())
        self.comboBox_toml_resolution.setSizePolicy(sizePolicy2)

        self.gridLayout_6.addWidget(self.comboBox_toml_resolution, 0, 1, 1, 1)

        self.checkBox_restrictive_candidates = QCheckBox(Form)
        self.checkBox_restrictive_candidates.setObjectName(u"checkBox_restrictive_candidates")
        self.checkBox_restrictive_candidates.setChecked(True)

        self.gridLayout_6.addWidget(self.checkBox_restrictive_candidates, 1, 0, 1, 2)


        self.verticalLayout.addLayout(self.gridLayout_6)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_separator.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Use the token separator set in the setting. <br/><br/>Useful for separating the trigger words (Kohya based trainers have a &quot;use token separator&quot; option). This allows you to have a variable length trigger word.<br/><br/>if this is enabled, tags in the main and secondary are placed in front of the tags and the token separator is placed to separate it from the rest of the tag.<br/></p><p>The tag order in main trigger tag(s) are unshuffled<br/>The tag order in secondary trigger tag(s) is shuffled<br/>The other tags are shuffled.<br/><br/>Here's an example with &quot;|||&quot; as token separator, 1 main trigger word, and 3 secondary trigger word:  main_trigger tag, secondary_tag_3, secondary_tag_1, secondary_tag_2, |||, rest of the tags, ...</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_separator.setText(QCoreApplication.translate("Form", u"Token Separator", None))
#if QT_CONFIG(tooltip)
        self.checkBox_trigger_tags.setToolTip(QCoreApplication.translate("Form", u"put trigger tags at the front", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_trigger_tags.setText(QCoreApplication.translate("Form", u"Trigger Tags", None))
#if QT_CONFIG(tooltip)
        self.checkBox_sentence_separator.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Place sentence (caption) infront of the token separator.</p><p>Useful if you want natural language in the front of the tags</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_sentence_separator.setText(QCoreApplication.translate("Form", u"Sentence in Token Separator", None))
#if QT_CONFIG(tooltip)
        self.checkBox_aesthetic_score_in_token_separator.setToolTip(QCoreApplication.translate("Form", u"Include the quality tags from the aesthetic scores and place them into the main trigger tag section.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_aesthetic_score_in_token_separator.setText(QCoreApplication.translate("Form", u"Aesthetic scores in token separator", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_sentence.setToolTip(QCoreApplication.translate("Form", u"include any sentences/caption in the export.  If no captions were set, they're not added to the exported file(s)", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_sentence.setText(QCoreApplication.translate("Form", u"Sentence", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_tags_in_sentence.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Enable this to remove tags that are included in the sentence. This is to reduce potential duplicates in both the caption and tags.<br/>Example: <br/>caption: &quot;1girl sitting on a chair thinking and contemplating life&quot;<br/>tag: &quot;1girl, solo, chair, sitting, red hair, green eyes, blue shirt&quot;<br/>--&gt; </p><p>caption and a shorter tag list is exported: caption + &quot;solo, red hair, green eyes, blue shirt&quot;</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_tags_in_sentence.setText(QCoreApplication.translate("Form", u"Remove tag if included in sentence", None))
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
        self.checkBox_current_group.setText(QCoreApplication.translate("Form", u"For Currently Selected Group", None))
#if QT_CONFIG(tooltip)
        self.pushButton_txt_file.setToolTip(QCoreApplication.translate("Form", u"create a txt file containing the full tags, same as the first tab", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_txt_file.setText(QCoreApplication.translate("Form", u"Create TXT files", None))
#if QT_CONFIG(tooltip)
        self.pushButton_json_tags_file.setToolTip(QCoreApplication.translate("Form", u"useful for checkpoints, makes a .json with the captions and tags. Exports like the meta_cap.json in Kohya.  You can run the meta_lat creator from Kohya directly on this exported json", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_json_tags_file.setText(QCoreApplication.translate("Form", u"Create .json tag file", None))
        self.pushButton_create_jsonl.setText(QCoreApplication.translate("Form", u"Create .jsonl file (for HF dataset library)", None))
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
        self.checkBox_restrictive_candidates.setText(QCoreApplication.translate("Form", u"Use more restrictive conditions", None))
    # retranslateUi

