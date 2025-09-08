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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListView, QPlainTextEdit, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QTreeView, QVBoxLayout, QWidget)

from CustomWidgets import OutputWidget

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(380, 686)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_save_database = QPushButton(Form)
        self.pushButton_save_database.setObjectName(u"pushButton_save_database")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_save_database.sizePolicy().hasHeightForWidth())
        self.pushButton_save_database.setSizePolicy(sizePolicy1)
        self.pushButton_save_database.setMinimumSize(QSize(50, 0))

        self.gridLayout.addWidget(self.pushButton_save_database, 8, 0, 1, 1)

        self.pushButton_popup_image = QPushButton(Form)
        self.pushButton_popup_image.setObjectName(u"pushButton_popup_image")
        sizePolicy1.setHeightForWidth(self.pushButton_popup_image.sizePolicy().hasHeightForWidth())
        self.pushButton_popup_image.setSizePolicy(sizePolicy1)
        self.pushButton_popup_image.setMinimumSize(QSize(50, 0))

        self.gridLayout.addWidget(self.pushButton_popup_image, 7, 0, 1, 1)

        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setTabPosition(QTabWidget.East)
        self.tabWidgetPage1 = QWidget()
        self.tabWidgetPage1.setObjectName(u"tabWidgetPage1")
        self.gridLayout_2 = QGridLayout(self.tabWidgetPage1)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_auto_classify = QPushButton(self.tabWidgetPage1)
        self.pushButton_auto_classify.setObjectName(u"pushButton_auto_classify")

        self.gridLayout_2.addWidget(self.pushButton_auto_classify, 10, 0, 1, 2)

        self.pushButton_cleanup_rejected_manual_tags = QPushButton(self.tabWidgetPage1)
        self.pushButton_cleanup_rejected_manual_tags.setObjectName(u"pushButton_cleanup_rejected_manual_tags")

        self.gridLayout_2.addWidget(self.pushButton_cleanup_rejected_manual_tags, 11, 0, 1, 2)

        self.pushButton_discard_image = QPushButton(self.tabWidgetPage1)
        self.pushButton_discard_image.setObjectName(u"pushButton_discard_image")

        self.gridLayout_2.addWidget(self.pushButton_discard_image, 23, 0, 1, 2)

        self.pushButton_auto_tag = QPushButton(self.tabWidgetPage1)
        self.pushButton_auto_tag.setObjectName(u"pushButton_auto_tag")
        sizePolicy1.setHeightForWidth(self.pushButton_auto_tag.sizePolicy().hasHeightForWidth())
        self.pushButton_auto_tag.setSizePolicy(sizePolicy1)
        self.pushButton_auto_tag.setMinimumSize(QSize(50, 0))

        self.gridLayout_2.addWidget(self.pushButton_auto_tag, 7, 0, 1, 2)

        self.pushButton_open_in_default_program = QPushButton(self.tabWidgetPage1)
        self.pushButton_open_in_default_program.setObjectName(u"pushButton_open_in_default_program")

        self.gridLayout_2.addWidget(self.pushButton_open_in_default_program, 24, 0, 1, 2)

        self.pushButton_reset_manual_score = QPushButton(self.tabWidgetPage1)
        self.pushButton_reset_manual_score.setObjectName(u"pushButton_reset_manual_score")

        self.gridLayout_2.addWidget(self.pushButton_reset_manual_score, 17, 0, 1, 2)

        self.pushButton_auto_score = QPushButton(self.tabWidgetPage1)
        self.pushButton_auto_score.setObjectName(u"pushButton_auto_score")

        self.gridLayout_2.addWidget(self.pushButton_auto_score, 9, 0, 1, 2)

        self.pushButton_apply_filtering = QPushButton(self.tabWidgetPage1)
        self.pushButton_apply_filtering.setObjectName(u"pushButton_apply_filtering")
        sizePolicy1.setHeightForWidth(self.pushButton_apply_filtering.sizePolicy().hasHeightForWidth())
        self.pushButton_apply_filtering.setSizePolicy(sizePolicy1)
        self.pushButton_apply_filtering.setMinimumSize(QSize(50, 0))

        self.gridLayout_2.addWidget(self.pushButton_apply_filtering, 5, 0, 1, 2)

        self.scrollArea = QScrollArea(self.tabWidgetPage1)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 333, 225))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.scrollArea, 1, 0, 1, 2)

        self.pushButton_export_images = QPushButton(self.tabWidgetPage1)
        self.pushButton_export_images.setObjectName(u"pushButton_export_images")

        self.gridLayout_2.addWidget(self.pushButton_export_images, 22, 0, 1, 2)

        self.line = QFrame(self.tabWidgetPage1)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 3, 0, 1, 2)

        self.pushButton_flip_horizontally = QPushButton(self.tabWidgetPage1)
        self.pushButton_flip_horizontally.setObjectName(u"pushButton_flip_horizontally")

        self.gridLayout_2.addWidget(self.pushButton_flip_horizontally, 25, 0, 1, 2)

        self.comboBox_selection = QComboBox(self.tabWidgetPage1)
        self.comboBox_selection.setObjectName(u"comboBox_selection")

        self.gridLayout_2.addWidget(self.comboBox_selection, 0, 1, 1, 1)

        self.pushButton_refresh_tags_from_gelbooru_and_rule34 = QPushButton(self.tabWidgetPage1)
        self.pushButton_refresh_tags_from_gelbooru_and_rule34.setObjectName(u"pushButton_refresh_tags_from_gelbooru_and_rule34")

        self.gridLayout_2.addWidget(self.pushButton_refresh_tags_from_gelbooru_and_rule34, 14, 0, 1, 2)

        self.label = QLabel(self.tabWidgetPage1)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.pushButton_replace = QPushButton(self.tabWidgetPage1)
        self.pushButton_replace.setObjectName(u"pushButton_replace")

        self.gridLayout_2.addWidget(self.pushButton_replace, 2, 0, 1, 2)

        self.pushButton_only_tag_characters = QPushButton(self.tabWidgetPage1)
        self.pushButton_only_tag_characters.setObjectName(u"pushButton_only_tag_characters")

        self.gridLayout_2.addWidget(self.pushButton_only_tag_characters, 8, 0, 1, 2)

        self.pushButton_purge_manual = QPushButton(self.tabWidgetPage1)
        self.pushButton_purge_manual.setObjectName(u"pushButton_purge_manual")

        self.gridLayout_2.addWidget(self.pushButton_purge_manual, 19, 0, 1, 2)

        self.pushButton_apply_replacement_to_sentence = QPushButton(self.tabWidgetPage1)
        self.pushButton_apply_replacement_to_sentence.setObjectName(u"pushButton_apply_replacement_to_sentence")

        self.gridLayout_2.addWidget(self.pushButton_apply_replacement_to_sentence, 6, 0, 1, 2)

        self.pushButton_remove_single_source_autotags = QPushButton(self.tabWidgetPage1)
        self.pushButton_remove_single_source_autotags.setObjectName(u"pushButton_remove_single_source_autotags")

        self.gridLayout_2.addWidget(self.pushButton_remove_single_source_autotags, 26, 0, 1, 2)

        self.pushButton_remove_rejected_manual = QPushButton(self.tabWidgetPage1)
        self.pushButton_remove_rejected_manual.setObjectName(u"pushButton_remove_rejected_manual")

        self.gridLayout_2.addWidget(self.pushButton_remove_rejected_manual, 27, 0, 1, 2)

        self.tabWidget.addTab(self.tabWidgetPage1, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.gridLayout_11 = QGridLayout(self.tab_6)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.groupBox_2 = QGroupBox(self.tab_6)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_12 = QGridLayout(self.groupBox_2)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_12.addWidget(self.label_5, 0, 0, 1, 1)

        self.comboBox_selection_2 = QComboBox(self.groupBox_2)
        self.comboBox_selection_2.setObjectName(u"comboBox_selection_2")

        self.gridLayout_12.addWidget(self.comboBox_selection_2, 0, 1, 1, 1)

        self.treeView_category_conflicts = QTreeView(self.groupBox_2)
        self.treeView_category_conflicts.setObjectName(u"treeView_category_conflicts")

        self.gridLayout_12.addWidget(self.treeView_category_conflicts, 1, 0, 1, 2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_12.addItem(self.verticalSpacer_3, 3, 0, 1, 2)

        self.pushButton_discardTagGroup = QPushButton(self.groupBox_2)
        self.pushButton_discardTagGroup.setObjectName(u"pushButton_discardTagGroup")

        self.gridLayout_12.addWidget(self.pushButton_discardTagGroup, 2, 0, 1, 2)


        self.gridLayout_11.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_6, "")
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
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.scrollArea_history.sizePolicy().hasHeightForWidth())
        self.scrollArea_history.setSizePolicy(sizePolicy2)
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
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tab_4.setMinimumSize(QSize(0, 0))
        self.gridLayout_6 = QGridLayout(self.tab_4)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_4 = QLabel(self.tab_4)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_4.addWidget(self.label_4)

        self.line_3 = QFrame(self.tab_4)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line_3)

        self.horizontalGroupBox1 = QGroupBox(self.tab_4)
        self.horizontalGroupBox1.setObjectName(u"horizontalGroupBox1")
        sizePolicy.setHeightForWidth(self.horizontalGroupBox1.sizePolicy().hasHeightForWidth())
        self.horizontalGroupBox1.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.horizontalGroupBox1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(1, 10, 1, 1)
        self.checkBox_highlight1 = QCheckBox(self.horizontalGroupBox1)
        self.checkBox_highlight1.setObjectName(u"checkBox_highlight1")

        self.horizontalLayout.addWidget(self.checkBox_highlight1)

        self.comboBox_sources1 = QComboBox(self.horizontalGroupBox1)
        self.comboBox_sources1.addItem("")
        self.comboBox_sources1.addItem("")
        self.comboBox_sources1.addItem("")
        self.comboBox_sources1.setObjectName(u"comboBox_sources1")
        sizePolicy1.setHeightForWidth(self.comboBox_sources1.sizePolicy().hasHeightForWidth())
        self.comboBox_sources1.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.comboBox_sources1)


        self.verticalLayout_4.addWidget(self.horizontalGroupBox1)

        self.line_2 = QFrame(self.tab_4)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line_2)

        self.horizontalGroupBox2 = QGroupBox(self.tab_4)
        self.horizontalGroupBox2.setObjectName(u"horizontalGroupBox2")
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalGroupBox2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(1, 10, 1, 1)
        self.checkBox_highlight2 = QCheckBox(self.horizontalGroupBox2)
        self.checkBox_highlight2.setObjectName(u"checkBox_highlight2")

        self.horizontalLayout_2.addWidget(self.checkBox_highlight2)

        self.doubleSpinBox_value2 = QDoubleSpinBox(self.horizontalGroupBox2)
        self.doubleSpinBox_value2.setObjectName(u"doubleSpinBox_value2")
        self.doubleSpinBox_value2.setMaximum(1.000000000000000)
        self.doubleSpinBox_value2.setSingleStep(0.010000000000000)
        self.doubleSpinBox_value2.setValue(0.800000000000000)

        self.horizontalLayout_2.addWidget(self.doubleSpinBox_value2)


        self.verticalLayout_4.addWidget(self.horizontalGroupBox2)

        self.horizontalGroupBox3 = QGroupBox(self.tab_4)
        self.horizontalGroupBox3.setObjectName(u"horizontalGroupBox3")
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalGroupBox3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(1, 10, 1, 1)
        self.checkBox_highlight3 = QCheckBox(self.horizontalGroupBox3)
        self.checkBox_highlight3.setObjectName(u"checkBox_highlight3")

        self.horizontalLayout_3.addWidget(self.checkBox_highlight3)

        self.spinBox_tokencount3 = QSpinBox(self.horizontalGroupBox3)
        self.spinBox_tokencount3.setObjectName(u"spinBox_tokencount3")
        self.spinBox_tokencount3.setValue(5)

        self.horizontalLayout_3.addWidget(self.spinBox_tokencount3)


        self.verticalLayout_4.addWidget(self.horizontalGroupBox3)

        self.pushButton_print_manual = QPushButton(self.tab_4)
        self.pushButton_print_manual.setObjectName(u"pushButton_print_manual")

        self.verticalLayout_4.addWidget(self.pushButton_print_manual)

        self.pushButton_print_recommendations = QPushButton(self.tab_4)
        self.pushButton_print_recommendations.setObjectName(u"pushButton_print_recommendations")

        self.verticalLayout_4.addWidget(self.pushButton_print_recommendations)

        self.pushButton_print_curr_img_data = QPushButton(self.tab_4)
        self.pushButton_print_curr_img_data.setObjectName(u"pushButton_print_curr_img_data")

        self.verticalLayout_4.addWidget(self.pushButton_print_curr_img_data)

        self.pushButton_tfidf_comp = QPushButton(self.tab_4)
        self.pushButton_tfidf_comp.setObjectName(u"pushButton_tfidf_comp")

        self.verticalLayout_4.addWidget(self.pushButton_tfidf_comp)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)


        self.gridLayout_6.addLayout(self.verticalLayout_4, 0, 1, 1, 1)

        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.gridLayout_5 = QGridLayout(self.tab_5)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.NoteSection = QGroupBox(self.tab_5)
        self.NoteSection.setObjectName(u"NoteSection")
        font = QFont()
        font.setPointSize(10)
        self.NoteSection.setFont(font)
        self.gridLayout_9 = QGridLayout(self.NoteSection)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.plainTextEdit_notes = QPlainTextEdit(self.NoteSection)
        self.plainTextEdit_notes.setObjectName(u"plainTextEdit_notes")

        self.gridLayout_9.addWidget(self.plainTextEdit_notes, 0, 0, 1, 1)


        self.verticalLayout_5.addWidget(self.NoteSection)

        self.ReportSection = QGroupBox(self.tab_5)
        self.ReportSection.setObjectName(u"ReportSection")
        self.ReportSection.setFont(font)
        self.gridLayout_8 = QGridLayout(self.ReportSection)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.plainTextEdit_reports = QPlainTextEdit(self.ReportSection)
        self.plainTextEdit_reports.setObjectName(u"plainTextEdit_reports")

        self.gridLayout_8.addWidget(self.plainTextEdit_reports, 1, 0, 1, 1)

        self.pushButton_generate_report = QPushButton(self.ReportSection)
        self.pushButton_generate_report.setObjectName(u"pushButton_generate_report")

        self.gridLayout_8.addWidget(self.pushButton_generate_report, 0, 0, 1, 1)


        self.verticalLayout_5.addWidget(self.ReportSection)


        self.gridLayout_5.addLayout(self.verticalLayout_5, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_5, "")
        self.NoteToSelf = QWidget()
        self.NoteToSelf.setObjectName(u"NoteToSelf")
        self.verticalLayout_7 = QVBoxLayout(self.NoteToSelf)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.plainTextEdit_noteToSelf = QPlainTextEdit(self.NoteToSelf)
        self.plainTextEdit_noteToSelf.setObjectName(u"plainTextEdit_noteToSelf")

        self.verticalLayout_6.addWidget(self.plainTextEdit_noteToSelf)


        self.verticalLayout_7.addLayout(self.verticalLayout_6)

        self.tabWidget.addTab(self.NoteToSelf, "")

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
        self.pushButton_auto_classify.setToolTip(QCoreApplication.translate("Form", u"Use the classifer model and some images will have additional tags for sources if the confidence is high", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_classify.setText(QCoreApplication.translate("Form", u"Auto-classifier", None))
#if QT_CONFIG(tooltip)
        self.pushButton_cleanup_rejected_manual_tags.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Can always be used without causing issues, should be used when you want to remove rejected manual tags that are useless.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_cleanup_rejected_manual_tags.setText(QCoreApplication.translate("Form", u"Cleanup Rejected manual tags", None))
#if QT_CONFIG(tooltip)
        self.pushButton_discard_image.setToolTip(QCoreApplication.translate("Form", u"discard the selected images by moving it to the discarded folder", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_discard_image.setText(QCoreApplication.translate("Form", u"Discard Images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_tag.setToolTip(QCoreApplication.translate("Form", u"use an auto tagger for tagging the image using your preferred tagging method", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_tag.setText(QCoreApplication.translate("Form", u"Auto-tagger", None))
#if QT_CONFIG(tooltip)
        self.pushButton_open_in_default_program.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>open the images in the default program or the specified program in the settings</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_open_in_default_program.setText(QCoreApplication.translate("Form", u"Open in default program", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reset_manual_score.setToolTip(QCoreApplication.translate("Form", u"reset all scores that were changed, and if the threshold are changed, will change the scores, without needing to restart the scorer", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reset_manual_score.setText(QCoreApplication.translate("Form", u"Reset manual score", None))
#if QT_CONFIG(tooltip)
        self.pushButton_auto_score.setToolTip(QCoreApplication.translate("Form", u"use an auto scorer for scoring the image using your preferred scoring method", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_auto_score.setText(QCoreApplication.translate("Form", u"Auto-aesthetic scorer", None))
#if QT_CONFIG(tooltip)
        self.pushButton_apply_filtering.setToolTip(QCoreApplication.translate("Form", u"filter the selction", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_apply_filtering.setText(QCoreApplication.translate("Form", u"Apply Filtering", None))
#if QT_CONFIG(tooltip)
        self.scrollArea.setToolTip(QCoreApplication.translate("Form", u"Add a new line to set up a tag replacement rule (not saved by the database)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_export_images.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>This will export the selection (check the apply to section above) to a new directory.<br/><br/>A pop up will show up and ask for a directory and a group name</p><p><br/></p><p>If a database doesn't exist in the output location, then a new database is created with the same tags.</p><p><br/></p><p>If a database exists, then the images are exported, and the tags are automatically added to the previously exisiting database under the entered group name.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_export_images.setText(QCoreApplication.translate("Form", u"Export Images", None))
        self.pushButton_flip_horizontally.setText(QCoreApplication.translate("Form", u"Flip Horizontally", None))
#if QT_CONFIG(tooltip)
        self.comboBox_selection.setToolTip(QCoreApplication.translate("Form", u"Apply to most of the buttons below", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_refresh_tags_from_gelbooru_and_rule34.setText(QCoreApplication.translate("Form", u"Refresh Tags from rule34 and gelbooru", None))
        self.label.setText(QCoreApplication.translate("Form", u"Apply to:", None))
#if QT_CONFIG(tooltip)
        self.pushButton_replace.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Using the selection combo box at the top, each lines are an independent replacement:</p><p>- only right tags: add tags to the selection</p><p>- only left tags: remove tags from the selection</p><p>- both tags: in images with all tags on the left, remove them and add the right tags</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_replace.setText(QCoreApplication.translate("Form", u"Replace", None))
#if QT_CONFIG(tooltip)
        self.pushButton_only_tag_characters.setToolTip(QCoreApplication.translate("Form", u"Use the Swinv2-3 tagger and only extract identified characters", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_only_tag_characters.setText(QCoreApplication.translate("Form", u"Only auto-tag characters", None))
#if QT_CONFIG(tooltip)
        self.pushButton_purge_manual.setToolTip(QCoreApplication.translate("Form", u"remove all manually edited tags and reviewed conflicts", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_purge_manual.setText(QCoreApplication.translate("Form", u"Purge Manual", None))
#if QT_CONFIG(tooltip)
        self.pushButton_apply_replacement_to_sentence.setToolTip(QCoreApplication.translate("Form", u"Currently doesn't do anything, will be implemented later", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_apply_replacement_to_sentence.setText(QCoreApplication.translate("Form", u"Apply Replacement to Sentence", None))
#if QT_CONFIG(tooltip)
        self.pushButton_remove_single_source_autotags.setToolTip(QCoreApplication.translate("Form", u"This will remove autotags that are only from one source. This only works if there's multiple sources of autotags. Basically keep common tags while pruning non-overlapping tags", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_remove_single_source_autotags.setText(QCoreApplication.translate("Form", u"Remove Single Source Autotags", None))
        self.pushButton_remove_rejected_manual.setText(QCoreApplication.translate("Form", u" Remove Rejected Manual", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWidgetPage1), QCoreApplication.translate("Form", u"Batch Operations", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"Batch Category", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"Apply to:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_selection_2.setToolTip(QCoreApplication.translate("Form", u"Apply to most of the buttons below", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.treeView_category_conflicts.setWhatsThis(QCoreApplication.translate("Form", u"select which category to discard, ex leotard vs swimsuit (looks very similar)", None))
#endif // QT_CONFIG(whatsthis)
        self.pushButton_discardTagGroup.setText(QCoreApplication.translate("Form", u"Discard Groupings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QCoreApplication.translate("Form", u"Category Filter", None))
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
        self.pushButton_remove_tags_from_frequency_batch.setText(QCoreApplication.translate("Form", u"Reject ALL or Selected tags from View", None))
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
        self.label_4.setText(QCoreApplication.translate("Form", u"Optional Settings", None))
        self.horizontalGroupBox1.setTitle(QCoreApplication.translate("Form", u"Highlight Single Source Tags", None))
        self.checkBox_highlight1.setText(QCoreApplication.translate("Form", u"Highlight", None))
        self.comboBox_sources1.setItemText(0, QCoreApplication.translate("Form", u"Swinv2v3", None))
        self.comboBox_sources1.setItemText(1, QCoreApplication.translate("Form", u"Eva02_largev3", None))
        self.comboBox_sources1.setItemText(2, QCoreApplication.translate("Form", u"Caformer", None))

        self.horizontalGroupBox2.setTitle(QCoreApplication.translate("Form", u"Higlight Tags Under Threshold", None))
        self.checkBox_highlight2.setText(QCoreApplication.translate("Form", u"Highlight", None))
        self.horizontalGroupBox3.setTitle(QCoreApplication.translate("Form", u"Highlight Tags with Tokens above", None))
        self.checkBox_highlight3.setText(QCoreApplication.translate("Form", u"Highlight", None))
        self.pushButton_print_manual.setText(QCoreApplication.translate("Form", u"print manual changes", None))
        self.pushButton_print_recommendations.setText(QCoreApplication.translate("Form", u"print Unknown Recommendations", None))
        self.pushButton_print_curr_img_data.setText(QCoreApplication.translate("Form", u"Print curr img data", None))
        self.pushButton_tfidf_comp.setText(QCoreApplication.translate("Form", u"Print tf-idf comparison", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Form", u"Page", None))
        self.NoteSection.setTitle(QCoreApplication.translate("Form", u"Notes", None))
        self.plainTextEdit_notes.setPlaceholderText(QCoreApplication.translate("Form", u"Enter any notes regarding database here", None))
        self.ReportSection.setTitle(QCoreApplication.translate("Form", u"Reports", None))
        self.plainTextEdit_reports.setPlaceholderText(QCoreApplication.translate("Form", u"AutoGenerate report and or edit info outside of Notes", None))
        self.pushButton_generate_report.setText(QCoreApplication.translate("Form", u"AutoGenerate Report", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("Form", u"Notes", None))
#if QT_CONFIG(accessibility)
        self.NoteToSelf.setAccessibleName(QCoreApplication.translate("Form", u"Note to self", None))
#endif // QT_CONFIG(accessibility)
        self.plainTextEdit_noteToSelf.setPlainText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.NoteToSelf), QCoreApplication.translate("Form", u"Note to Self", None))
    # retranslateUi

