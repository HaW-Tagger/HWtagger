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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QComboBox,
    QFrame, QGridLayout, QGroupBox, QHeaderView,
    QLabel, QLineEdit, QListView, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QTabWidget,
    QTreeView, QVBoxLayout, QWidget)

from CustomWidgets import OutputWidget

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(453, 825)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_save_database = QPushButton(Form)
        self.pushButton_save_database.setObjectName(u"pushButton_save_database")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_save_database.sizePolicy().hasHeightForWidth())
        self.pushButton_save_database.setSizePolicy(sizePolicy)
        self.pushButton_save_database.setMinimumSize(QSize(50, 0))

        self.gridLayout.addWidget(self.pushButton_save_database, 8, 0, 1, 1)

        self.pushButton_popup_image = QPushButton(Form)
        self.pushButton_popup_image.setObjectName(u"pushButton_popup_image")
        sizePolicy.setHeightForWidth(self.pushButton_popup_image.sizePolicy().hasHeightForWidth())
        self.pushButton_popup_image.setSizePolicy(sizePolicy)
        self.pushButton_popup_image.setMinimumSize(QSize(50, 0))

        self.gridLayout.addWidget(self.pushButton_popup_image, 7, 0, 1, 1)

        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.East)
        self.tabWidgetPage1 = QWidget()
        self.tabWidgetPage1.setObjectName(u"tabWidgetPage1")
        self.gridLayout_2 = QGridLayout(self.tabWidgetPage1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_cleanup_rejected_manual_tags = QPushButton(self.tabWidgetPage1)
        self.pushButton_cleanup_rejected_manual_tags.setObjectName(u"pushButton_cleanup_rejected_manual_tags")

        self.gridLayout_2.addWidget(self.pushButton_cleanup_rejected_manual_tags, 9, 0, 1, 2)

        self.pushButton_discard_image = QPushButton(self.tabWidgetPage1)
        self.pushButton_discard_image.setObjectName(u"pushButton_discard_image")

        self.gridLayout_2.addWidget(self.pushButton_discard_image, 21, 0, 1, 2)

        self.pushButton_auto_classify = QPushButton(self.tabWidgetPage1)
        self.pushButton_auto_classify.setObjectName(u"pushButton_auto_classify")

        self.gridLayout_2.addWidget(self.pushButton_auto_classify, 8, 0, 1, 2)

        self.pushButton_flip_horizontally = QPushButton(self.tabWidgetPage1)
        self.pushButton_flip_horizontally.setObjectName(u"pushButton_flip_horizontally")

        self.gridLayout_2.addWidget(self.pushButton_flip_horizontally, 23, 0, 1, 2)

        self.label = QLabel(self.tabWidgetPage1)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.pushButton_open_in_default_program = QPushButton(self.tabWidgetPage1)
        self.pushButton_open_in_default_program.setObjectName(u"pushButton_open_in_default_program")

        self.gridLayout_2.addWidget(self.pushButton_open_in_default_program, 22, 0, 1, 2)

        self.pushButton_refresh_tags_from_gelbooru_and_rule34 = QPushButton(self.tabWidgetPage1)
        self.pushButton_refresh_tags_from_gelbooru_and_rule34.setObjectName(u"pushButton_refresh_tags_from_gelbooru_and_rule34")

        self.gridLayout_2.addWidget(self.pushButton_refresh_tags_from_gelbooru_and_rule34, 12, 0, 1, 2)

        self.pushButton_export_images = QPushButton(self.tabWidgetPage1)
        self.pushButton_export_images.setObjectName(u"pushButton_export_images")

        self.gridLayout_2.addWidget(self.pushButton_export_images, 20, 0, 1, 2)

        self.pushButton_only_tag_characters = QPushButton(self.tabWidgetPage1)
        self.pushButton_only_tag_characters.setObjectName(u"pushButton_only_tag_characters")

        self.gridLayout_2.addWidget(self.pushButton_only_tag_characters, 6, 0, 1, 2)

        self.pushButton_purge_manual = QPushButton(self.tabWidgetPage1)
        self.pushButton_purge_manual.setObjectName(u"pushButton_purge_manual")

        self.gridLayout_2.addWidget(self.pushButton_purge_manual, 17, 0, 1, 2)

        self.pushButton_reset_manual_score = QPushButton(self.tabWidgetPage1)
        self.pushButton_reset_manual_score.setObjectName(u"pushButton_reset_manual_score")

        self.gridLayout_2.addWidget(self.pushButton_reset_manual_score, 15, 0, 1, 2)

        self.pushButton_apply_replacement_to_sentence = QPushButton(self.tabWidgetPage1)
        self.pushButton_apply_replacement_to_sentence.setObjectName(u"pushButton_apply_replacement_to_sentence")

        self.gridLayout_2.addWidget(self.pushButton_apply_replacement_to_sentence, 4, 0, 1, 2)

        self.pushButton_auto_tag = QPushButton(self.tabWidgetPage1)
        self.pushButton_auto_tag.setObjectName(u"pushButton_auto_tag")
        sizePolicy.setHeightForWidth(self.pushButton_auto_tag.sizePolicy().hasHeightForWidth())
        self.pushButton_auto_tag.setSizePolicy(sizePolicy)
        self.pushButton_auto_tag.setMinimumSize(QSize(50, 0))

        self.gridLayout_2.addWidget(self.pushButton_auto_tag, 5, 0, 1, 2)

        self.pushButton_auto_score = QPushButton(self.tabWidgetPage1)
        self.pushButton_auto_score.setObjectName(u"pushButton_auto_score")

        self.gridLayout_2.addWidget(self.pushButton_auto_score, 7, 0, 1, 2)

        self.comboBox_selection = QComboBox(self.tabWidgetPage1)
        self.comboBox_selection.setObjectName(u"comboBox_selection")

        self.gridLayout_2.addWidget(self.comboBox_selection, 0, 1, 1, 1)

        self.pushButton_apply_filtering = QPushButton(self.tabWidgetPage1)
        self.pushButton_apply_filtering.setObjectName(u"pushButton_apply_filtering")
        sizePolicy.setHeightForWidth(self.pushButton_apply_filtering.sizePolicy().hasHeightForWidth())
        self.pushButton_apply_filtering.setSizePolicy(sizePolicy)
        self.pushButton_apply_filtering.setMinimumSize(QSize(50, 0))

        self.gridLayout_2.addWidget(self.pushButton_apply_filtering, 3, 0, 1, 2)

        self.line = QFrame(self.tabWidgetPage1)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 1, 0, 1, 2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_3, 24, 0, 1, 2)

        self.tabWidget.addTab(self.tabWidgetPage1, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_4 = QVBoxLayout(self.tab_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.scrollArea = QScrollArea(self.tab_4)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 388, 721))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_4.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.tab_4, "")
        self.tabWidgetPage2 = QWidget()
        self.tabWidgetPage2.setObjectName(u"tabWidgetPage2")
        self.verticalLayout = QVBoxLayout(self.tabWidgetPage2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget_to_output = OutputWidget(self.tabWidgetPage2)
        self.widget_to_output.setObjectName(u"widget_to_output")

        self.verticalLayout.addWidget(self.widget_to_output)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tabWidgetPage2, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_3 = QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.treeView_favourites = QTreeView(self.tab_2)
        self.treeView_favourites.setObjectName(u"treeView_favourites")
        self.treeView_favourites.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView_favourites.setProperty("showDropIndicator", False)
        self.treeView_favourites.setAnimated(True)
        self.treeView_favourites.header().setVisible(False)

        self.gridLayout_3.addWidget(self.treeView_favourites, 0, 0, 1, 1)

        self.lineEdit_edit_favourites = QLineEdit(self.tab_2)
        self.lineEdit_edit_favourites.setObjectName(u"lineEdit_edit_favourites")

        self.gridLayout_3.addWidget(self.lineEdit_edit_favourites, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_3 = QVBoxLayout(self.tab_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.comboBox_frequency_sort = QComboBox(self.tab_3)
        self.comboBox_frequency_sort.setObjectName(u"comboBox_frequency_sort")
        self.comboBox_frequency_sort.setFrame(True)

        self.verticalLayout_3.addWidget(self.comboBox_frequency_sort)

        self.groupBox = QGroupBox(self.tab_3)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout_7 = QGridLayout(self.groupBox)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_7.addWidget(self.label_2, 0, 0, 1, 1)

        self.comboBox_batch_selection_frequency = QComboBox(self.groupBox)
        self.comboBox_batch_selection_frequency.setObjectName(u"comboBox_batch_selection_frequency")

        self.gridLayout_7.addWidget(self.comboBox_batch_selection_frequency, 0, 1, 1, 1)

        self.pushButton_remove_tags_from_frequency_batch = QPushButton(self.groupBox)
        self.pushButton_remove_tags_from_frequency_batch.setObjectName(u"pushButton_remove_tags_from_frequency_batch")

        self.gridLayout_7.addWidget(self.pushButton_remove_tags_from_frequency_batch, 2, 0, 1, 2)

        self.lineEdit_tag_frequency_search = QLineEdit(self.groupBox)
        self.lineEdit_tag_frequency_search.setObjectName(u"lineEdit_tag_frequency_search")

        self.gridLayout_7.addWidget(self.lineEdit_tag_frequency_search, 1, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_7.addWidget(self.label_3, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.listView_tags_frequency = QListView(self.tab_3)
        self.listView_tags_frequency.setObjectName(u"listView_tags_frequency")

        self.verticalLayout_3.addWidget(self.listView_tags_frequency)

        self.pushButton_refresh_tags_frequency = QPushButton(self.tab_3)
        self.pushButton_refresh_tags_frequency.setObjectName(u"pushButton_refresh_tags_frequency")

        self.verticalLayout_3.addWidget(self.pushButton_refresh_tags_frequency)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_4 = QGridLayout(self.tab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.scrollArea_history = QScrollArea(self.tab)
        self.scrollArea_history.setObjectName(u"scrollArea_history")
        self.scrollArea_history.setWidgetResizable(True)
        self.scrollAreaWidgetContents_history = QWidget()
        self.scrollAreaWidgetContents_history.setObjectName(u"scrollAreaWidgetContents_history")
        self.scrollAreaWidgetContents_history.setGeometry(QRect(0, 0, 98, 28))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents_history)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea_history.setWidget(self.scrollAreaWidgetContents_history)

        self.gridLayout_4.addWidget(self.scrollArea_history, 0, 0, 1, 1)

        self.pushButton_clean_history = QPushButton(self.tab)
        self.pushButton_clean_history.setObjectName(u"pushButton_clean_history")

        self.gridLayout_4.addWidget(self.pushButton_clean_history, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tab, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)


        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.pushButton_save_database.setToolTip(QCoreApplication.translate("Form", u"save the database, this is the only button on this page that saves the database", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_save_database.setText(QCoreApplication.translate("Form", u"Save Database", None))
#if QT_CONFIG(tooltip)
        self.pushButton_popup_image.setToolTip(QCoreApplication.translate("Form", u"Display the selected image in a separate window", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_popup_image.setText(QCoreApplication.translate("Form", u"Pop-up image", None))
#if QT_CONFIG(tooltip)
        self.pushButton_cleanup_rejected_manual_tags.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Can always be used without causing issues, should be used when you want to remove rejected manual tags that are useless.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_cleanup_rejected_manual_tags.setText(QCoreApplication.translate("Form", u"Cleanup Rejected manual tags", None))
#if QT_CONFIG(tooltip)
        self.pushButton_discard_image.setToolTip(QCoreApplication.translate("Form", u"discard the selected images by moving it to the discarded folder", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_discard_image.setText(QCoreApplication.translate("Form", u"Discard Images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_classify.setToolTip(QCoreApplication.translate("Form", u"Use the classifer model and some images will have additional tags for sources if the confidence is high", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_classify.setText(QCoreApplication.translate("Form", u"Auto-classifier", None))
        self.pushButton_flip_horizontally.setText(QCoreApplication.translate("Form", u"Flip Horizontally", None))
        self.label.setText(QCoreApplication.translate("Form", u"Apply to:", None))
#if QT_CONFIG(tooltip)
        self.pushButton_open_in_default_program.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>open the images in the default program or the specified program in the settings</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_open_in_default_program.setText(QCoreApplication.translate("Form", u"Open in default program", None))
        self.pushButton_refresh_tags_from_gelbooru_and_rule34.setText(QCoreApplication.translate("Form", u"Refresh Tags from rule34 and gelbooru", None))
#if QT_CONFIG(tooltip)
        self.pushButton_export_images.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>This will export the selection (check the apply to section above) to a new directory.<br/><br/>A pop up will show up and ask for a directory and a group name</p><p><br/></p><p>If a database doesn't exist in the output location, then a new database is created with the same tags.</p><p><br/></p><p>If a database exists, then the images are exported, and the tags are automatically added to the previously exisiting database under the entered group name.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_export_images.setText(QCoreApplication.translate("Form", u"Export Images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_only_tag_characters.setToolTip(QCoreApplication.translate("Form", u"Use the Swinv2-3 tagger and only extract identified characters", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_only_tag_characters.setText(QCoreApplication.translate("Form", u"Only auto-tag characters", None))
#if QT_CONFIG(tooltip)
        self.pushButton_purge_manual.setToolTip(QCoreApplication.translate("Form", u"remove all manually edited tags and reviewed conflicts", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_purge_manual.setText(QCoreApplication.translate("Form", u"Purge Manual", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reset_manual_score.setToolTip(QCoreApplication.translate("Form", u"reset all scores that were changed, and if the threshold are changed, will change the scores, without needing to restart the scorer", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reset_manual_score.setText(QCoreApplication.translate("Form", u"Reset manual score", None))
#if QT_CONFIG(tooltip)
        self.pushButton_apply_replacement_to_sentence.setToolTip(QCoreApplication.translate("Form", u"Currently doesn't do anything, will be implemented later", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_apply_replacement_to_sentence.setText(QCoreApplication.translate("Form", u"Apply Replacement to Sentence", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_tag.setToolTip(QCoreApplication.translate("Form", u"use an auto tagger for tagging the image using your preferred tagging method", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_tag.setText(QCoreApplication.translate("Form", u"Auto-tagger", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_score.setToolTip(QCoreApplication.translate("Form", u"use an auto scorer for scoring the image using your preferred scoring method", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_score.setText(QCoreApplication.translate("Form", u"Auto-aesthetic scorer", None))
#if QT_CONFIG(tooltip)
        self.comboBox_selection.setToolTip(QCoreApplication.translate("Form", u"Apply to most of the buttons below", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_apply_filtering.setToolTip(QCoreApplication.translate("Form", u"filter the selction", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_apply_filtering.setText(QCoreApplication.translate("Form", u"Apply Filtering", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage1), QCoreApplication.translate("Form", u"Batch Operations", None))
#if QT_CONFIG(tooltip)
        self.scrollArea.setToolTip(QCoreApplication.translate("Form", u"Add a new line to set up a tag replacement rule (not saved by the database)", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Form", u"Database Settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage2), QCoreApplication.translate("Form", u"Output", None))
#if QT_CONFIG(tooltip)
        self.treeView_favourites.setToolTip(QCoreApplication.translate("Form", u"tags that are parts of the favourites, currently it's impossible to add tags to it in the UI", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.lineEdit_edit_favourites.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Type tags separated by commas to the favourites:</p><p>- if the tag is present in the favourites it will remove the tag from the favourites</p><p>- if the tag is not in the favourites it will be added</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_edit_favourites.setPlaceholderText(QCoreApplication.translate("Form", u"add and remove favourite tags (separated by ,)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Form", u"Favourites", None))
        self.groupBox.setTitle("")
        self.label_2.setText(QCoreApplication.translate("Form", u"Apply to:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_batch_selection_frequency.setToolTip(QCoreApplication.translate("Form", u"Apply to most of the buttons below", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_remove_tags_from_frequency_batch.setText(QCoreApplication.translate("Form", u"Remove all tags from frequency", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_tag_frequency_search.setToolTip(QCoreApplication.translate("Form", u"Enter text to filter down your results, does fuzzy search on each tags listed below", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_tag_frequency_search.setPlaceholderText(QCoreApplication.translate("Form", u"Enter text to search", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Search:", None))
#if QT_CONFIG(tooltip)
        self.listView_tags_frequency.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Show the tags common in the images, sorted by frequency, double clicking on a tag select all the images with this tags that are currently visible in the view (takes into account groups, search, ...)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_refresh_tags_frequency.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>The tag frequency is only updated when pressing this button, BUT It will still select the images that currently have the selected tag and not the images at the time you refreshed the page</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_refresh_tags_frequency.setText(QCoreApplication.translate("Form", u"Refresh Tags Frequency", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Form", u"Tags Frequency", None))
        self.pushButton_clean_history.setText(QCoreApplication.translate("Form", u"Clean History", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"History", None))
    # retranslateUi

