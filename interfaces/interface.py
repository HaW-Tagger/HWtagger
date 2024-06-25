# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPlainTextEdit,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1052, 858)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QTabWidget.Rounded)
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setAutoFillBackground(True)
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setLayoutDirection(Qt.LeftToRight)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tabWidget.setElideMode(Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.widget = QWidget()
        self.widget.setObjectName(u"widget")
        self.gridLayout_10 = QGridLayout(self.widget)
        self.gridLayout_10.setSpacing(0)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.tabWidget_2 = QTabWidget(self.widget)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lineEdit_database_folder = QLineEdit(self.tab)
        self.lineEdit_database_folder.setObjectName(u"lineEdit_database_folder")
        self.lineEdit_database_folder.setClearButtonEnabled(False)

        self.verticalLayout_2.addWidget(self.lineEdit_database_folder)

        self.pushButton_load_database = QPushButton(self.tab)
        self.pushButton_load_database.setObjectName(u"pushButton_load_database")

        self.verticalLayout_2.addWidget(self.pushButton_load_database)

        self.pushButton_save_database = QPushButton(self.tab)
        self.pushButton_save_database.setObjectName(u"pushButton_save_database")

        self.verticalLayout_2.addWidget(self.pushButton_save_database)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox_6 = QGroupBox(self.tab)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_11 = QGridLayout(self.groupBox_6)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.gridLayout_11.setContentsMargins(-1, 12, -1, -1)
        self.pushButton_convert_images_to_png = QPushButton(self.groupBox_6)
        self.pushButton_convert_images_to_png.setObjectName(u"pushButton_convert_images_to_png")

        self.gridLayout_11.addWidget(self.pushButton_convert_images_to_png, 0, 0, 1, 1)

        self.pushButton_rename_images_md5 = QPushButton(self.groupBox_6)
        self.pushButton_rename_images_md5.setObjectName(u"pushButton_rename_images_md5")

        self.gridLayout_11.addWidget(self.pushButton_rename_images_md5, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_6)

        self.groupBox_3 = QGroupBox(self.tab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.gridLayout_6 = QGridLayout(self.groupBox_3)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(-1, 12, -1, -1)
        self.pushButton_rescores = QPushButton(self.groupBox_3)
        self.pushButton_rescores.setObjectName(u"pushButton_rescores")

        self.gridLayout_6.addWidget(self.pushButton_rescores, 2, 0, 1, 1)

        self.pushButton_reautotags = QPushButton(self.groupBox_3)
        self.pushButton_reautotags.setObjectName(u"pushButton_reautotags")

        self.gridLayout_6.addWidget(self.pushButton_reautotags, 1, 0, 1, 1)

        self.pushButton_reclassify = QPushButton(self.groupBox_3)
        self.pushButton_reclassify.setObjectName(u"pushButton_reclassify")

        self.gridLayout_6.addWidget(self.pushButton_reclassify, 3, 0, 1, 1)

        self.pushButton_filter_images = QPushButton(self.groupBox_3)
        self.pushButton_filter_images.setObjectName(u"pushButton_filter_images")

        self.gridLayout_6.addWidget(self.pushButton_filter_images, 1, 1, 1, 1)

        self.pushButton_images_existence = QPushButton(self.groupBox_3)
        self.pushButton_images_existence.setObjectName(u"pushButton_images_existence")

        self.gridLayout_6.addWidget(self.pushButton_images_existence, 2, 1, 1, 1)

        self.pushButton_rehash = QPushButton(self.groupBox_3)
        self.pushButton_rehash.setObjectName(u"pushButton_rehash")

        self.gridLayout_6.addWidget(self.pushButton_rehash, 3, 1, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_3)

        self.groupBox_5 = QGroupBox(self.tab)
        self.groupBox_5.setObjectName(u"groupBox_5")
        sizePolicy.setHeightForWidth(self.groupBox_5.sizePolicy().hasHeightForWidth())
        self.groupBox_5.setSizePolicy(sizePolicy)
        self.gridLayout_8 = QGridLayout(self.groupBox_5)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(-1, 12, -1, -1)
        self.pushButton_move_files_groupings = QPushButton(self.groupBox_5)
        self.pushButton_move_files_groupings.setObjectName(u"pushButton_move_files_groupings")

        self.gridLayout_8.addWidget(self.pushButton_move_files_groupings, 0, 0, 1, 1)

        self.pushButton_rebuild_groups = QPushButton(self.groupBox_5)
        self.pushButton_rebuild_groups.setObjectName(u"pushButton_rebuild_groups")

        self.gridLayout_8.addWidget(self.pushButton_rebuild_groups, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_5)

        self.groupBox_10 = QGroupBox(self.tab)
        self.groupBox_10.setObjectName(u"groupBox_10")
        sizePolicy.setHeightForWidth(self.groupBox_10.sizePolicy().hasHeightForWidth())
        self.groupBox_10.setSizePolicy(sizePolicy)
        self.gridLayout_13 = QGridLayout(self.groupBox_10)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.gridLayout_13.setContentsMargins(-1, 12, -1, -1)
        self.lineEdit_secondary_db_folder = QLineEdit(self.groupBox_10)
        self.lineEdit_secondary_db_folder.setObjectName(u"lineEdit_secondary_db_folder")

        self.gridLayout_13.addWidget(self.lineEdit_secondary_db_folder, 0, 0, 1, 1)

        self.pushButton_load_and_merge_secondary = QPushButton(self.groupBox_10)
        self.pushButton_load_and_merge_secondary.setObjectName(u"pushButton_load_and_merge_secondary")

        self.gridLayout_13.addWidget(self.pushButton_load_and_merge_secondary, 1, 0, 1, 1)


        self.verticalLayout_3.addWidget(self.groupBox_10)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)


        self.horizontalLayout_19.addLayout(self.verticalLayout_3)

        self.line = QFrame(self.tab)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_19.addWidget(self.line)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.gridLayout_5 = QGridLayout(self.groupBox_2)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(-1, 12, -1, -1)
        self.checkBox_remove_tag_in_sentence = QCheckBox(self.groupBox_2)
        self.checkBox_remove_tag_in_sentence.setObjectName(u"checkBox_remove_tag_in_sentence")

        self.gridLayout_5.addWidget(self.checkBox_remove_tag_in_sentence, 4, 1, 1, 1)

        self.checkBox_trigger_tags = QCheckBox(self.groupBox_2)
        self.checkBox_trigger_tags.setObjectName(u"checkBox_trigger_tags")
        self.checkBox_trigger_tags.setChecked(True)

        self.gridLayout_5.addWidget(self.checkBox_trigger_tags, 2, 0, 1, 1)

        self.plainTextEdit_secondary_trigger_tags = QPlainTextEdit(self.groupBox_2)
        self.plainTextEdit_secondary_trigger_tags.setObjectName(u"plainTextEdit_secondary_trigger_tags")

        self.gridLayout_5.addWidget(self.plainTextEdit_secondary_trigger_tags, 1, 0, 1, 2)

        self.checkBox_aesthetic_score = QCheckBox(self.groupBox_2)
        self.checkBox_aesthetic_score.setObjectName(u"checkBox_aesthetic_score")

        self.gridLayout_5.addWidget(self.checkBox_aesthetic_score, 4, 0, 1, 1)

        self.checkBox_token_separator = QCheckBox(self.groupBox_2)
        self.checkBox_token_separator.setObjectName(u"checkBox_token_separator")

        self.gridLayout_5.addWidget(self.checkBox_token_separator, 3, 0, 1, 1)

        self.checkBox_sentence_in_token_separator = QCheckBox(self.groupBox_2)
        self.checkBox_sentence_in_token_separator.setObjectName(u"checkBox_sentence_in_token_separator")

        self.gridLayout_5.addWidget(self.checkBox_sentence_in_token_separator, 3, 1, 1, 1)

        self.checkBox_sentence = QCheckBox(self.groupBox_2)
        self.checkBox_sentence.setObjectName(u"checkBox_sentence")

        self.gridLayout_5.addWidget(self.checkBox_sentence, 2, 1, 1, 1)

        self.lineEdit_main_trigger_tags = QLineEdit(self.groupBox_2)
        self.lineEdit_main_trigger_tags.setObjectName(u"lineEdit_main_trigger_tags")

        self.gridLayout_5.addWidget(self.lineEdit_main_trigger_tags, 0, 0, 1, 2)

        self.pushButton_create_txt_files = QPushButton(self.groupBox_2)
        self.pushButton_create_txt_files.setObjectName(u"pushButton_create_txt_files")

        self.gridLayout_5.addWidget(self.pushButton_create_txt_files, 5, 0, 1, 2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.pushButton_create_sample_toml = QPushButton(self.groupBox_2)
        self.pushButton_create_sample_toml.setObjectName(u"pushButton_create_sample_toml")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_create_sample_toml.sizePolicy().hasHeightForWidth())
        self.pushButton_create_sample_toml.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.pushButton_create_sample_toml)

        self.comboBox_toml_resolution = QComboBox(self.groupBox_2)
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.addItem("")
        self.comboBox_toml_resolution.setObjectName(u"comboBox_toml_resolution")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBox_toml_resolution.sizePolicy().hasHeightForWidth())
        self.comboBox_toml_resolution.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.comboBox_toml_resolution)


        self.gridLayout_5.addLayout(self.horizontalLayout_2, 6, 0, 1, 2)


        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.pushButton_print_unknown_tags = QPushButton(self.tab)
        self.pushButton_print_unknown_tags.setObjectName(u"pushButton_print_unknown_tags")

        self.verticalLayout_4.addWidget(self.pushButton_print_unknown_tags)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_4)


        self.horizontalLayout_19.addLayout(self.verticalLayout_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_19)

        self.tabWidget_2.addTab(self.tab, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_12 = QGridLayout(self.tab_3)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_12.addItem(self.verticalSpacer_2, 2, 0, 1, 1)

        self.groupBox_4 = QGroupBox(self.tab_3)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_9 = QGridLayout(self.groupBox_4)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(-1, 12, -1, -1)
        self.pushButton_create_meta_cap = QPushButton(self.groupBox_4)
        self.pushButton_create_meta_cap.setObjectName(u"pushButton_create_meta_cap")

        self.gridLayout_9.addWidget(self.pushButton_create_meta_cap, 5, 0, 1, 1)

        self.pushButton_export_npz = QPushButton(self.groupBox_4)
        self.pushButton_export_npz.setObjectName(u"pushButton_export_npz")

        self.gridLayout_9.addWidget(self.pushButton_export_npz, 2, 0, 1, 1)

        self.pushButton_merge_metacap = QPushButton(self.groupBox_4)
        self.pushButton_merge_metacap.setObjectName(u"pushButton_merge_metacap")

        self.gridLayout_9.addWidget(self.pushButton_merge_metacap, 4, 0, 1, 1)

        self.pushButton_rename_all = QPushButton(self.groupBox_4)
        self.pushButton_rename_all.setObjectName(u"pushButton_rename_all")

        self.gridLayout_9.addWidget(self.pushButton_rename_all, 1, 0, 1, 1)


        self.gridLayout_12.addWidget(self.groupBox_4, 1, 0, 1, 1)

        self.lineEdit_dataset_folder = QLineEdit(self.tab_3)
        self.lineEdit_dataset_folder.setObjectName(u"lineEdit_dataset_folder")

        self.gridLayout_12.addWidget(self.lineEdit_dataset_folder, 0, 0, 1, 1)

        self.tabWidget_2.addTab(self.tab_3, "")

        self.gridLayout_10.addWidget(self.tabWidget_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.widget, "")
        self.databasesViewTab = QWidget()
        self.databasesViewTab.setObjectName(u"databasesViewTab")
        self.gridLayout_14 = QGridLayout(self.databasesViewTab)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.gridLayout_14.setContentsMargins(0, 0, 0, 0)
        self.pushButton_view_database = QPushButton(self.databasesViewTab)
        self.pushButton_view_database.setObjectName(u"pushButton_view_database")

        self.gridLayout_14.addWidget(self.pushButton_view_database, 0, 1, 1, 1)

        self.databaseTabWidget = QTabWidget(self.databasesViewTab)
        self.databaseTabWidget.setObjectName(u"databaseTabWidget")
        self.databaseTabWidget.setTabsClosable(True)

        self.gridLayout_14.addWidget(self.databaseTabWidget, 1, 0, 1, 3)

        self.lineEdit_view_database_path = QLineEdit(self.databasesViewTab)
        self.lineEdit_view_database_path.setObjectName(u"lineEdit_view_database_path")

        self.gridLayout_14.addWidget(self.lineEdit_view_database_path, 0, 0, 1, 1)

        self.tabWidget.addTab(self.databasesViewTab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_15 = QGridLayout(self.tab_2)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.scrollArea = QScrollArea(self.tab_2)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1015, 808))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(-1, 12, -1, -1)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.spin_font_size = QSpinBox(self.groupBox)
        self.spin_font_size.setObjectName(u"spin_font_size")
        self.spin_font_size.setMinimum(5)
        self.spin_font_size.setMaximum(30)

        self.horizontalLayout_3.addWidget(self.spin_font_size)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.spin_image_load_size = QSpinBox(self.groupBox)
        self.spin_image_load_size.setObjectName(u"spin_image_load_size")
        self.spin_image_load_size.setMinimum(128)
        self.spin_image_load_size.setMaximum(1024)
        self.spin_image_load_size.setSingleStep(32)

        self.horizontalLayout_4.addWidget(self.spin_image_load_size)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)

        self.checkBox_enable_image_tooltip = QCheckBox(self.groupBox)
        self.checkBox_enable_image_tooltip.setObjectName(u"checkBox_enable_image_tooltip")

        self.verticalLayout_5.addWidget(self.checkBox_enable_image_tooltip)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.comboBox_click_option = QComboBox(self.groupBox)
        self.comboBox_click_option.addItem("")
        self.comboBox_click_option.addItem("")
        self.comboBox_click_option.setObjectName(u"comboBox_click_option")

        self.horizontalLayout.addWidget(self.comboBox_click_option)

        self.label_14 = QLabel(self.groupBox)
        self.label_14.setObjectName(u"label_14")

        self.horizontalLayout.addWidget(self.label_14)


        self.verticalLayout_5.addLayout(self.horizontalLayout)

        self.checkBox_hide_sentence_in_view = QCheckBox(self.groupBox)
        self.checkBox_hide_sentence_in_view.setObjectName(u"checkBox_hide_sentence_in_view")

        self.verticalLayout_5.addWidget(self.checkBox_hide_sentence_in_view)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_8 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_8)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(-1, 12, -1, -1)
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.spin_max_batch_size = QSpinBox(self.groupBox_8)
        self.spin_max_batch_size.setObjectName(u"spin_max_batch_size")
        self.spin_max_batch_size.setMinimum(2)
        self.spin_max_batch_size.setMaximum(16)
        self.spin_max_batch_size.setSingleStep(2)

        self.horizontalLayout_11.addWidget(self.spin_max_batch_size)

        self.label_8 = QLabel(self.groupBox_8)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_11.addWidget(self.label_8)


        self.verticalLayout_7.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.lineEdit_keep_token_tag_separator = QLineEdit(self.groupBox_8)
        self.lineEdit_keep_token_tag_separator.setObjectName(u"lineEdit_keep_token_tag_separator")

        self.horizontalLayout_12.addWidget(self.lineEdit_keep_token_tag_separator)

        self.label_9 = QLabel(self.groupBox_8)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.label_9)


        self.verticalLayout_7.addLayout(self.horizontalLayout_12)

        self.check_remove_transparency_from_images = QCheckBox(self.groupBox_8)
        self.check_remove_transparency_from_images.setObjectName(u"check_remove_transparency_from_images")

        self.verticalLayout_7.addWidget(self.check_remove_transparency_from_images)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.spin_max_images_loader_thread = QSpinBox(self.groupBox_8)
        self.spin_max_images_loader_thread.setObjectName(u"spin_max_images_loader_thread")
        self.spin_max_images_loader_thread.setMinimum(2)
        self.spin_max_images_loader_thread.setMaximum(128)
        self.spin_max_images_loader_thread.setSingleStep(2)

        self.horizontalLayout_13.addWidget(self.spin_max_images_loader_thread)

        self.label_10 = QLabel(self.groupBox_8)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_13.addWidget(self.label_10)


        self.verticalLayout_7.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.spin_max_4k_pixels_save_multiplier = QSpinBox(self.groupBox_8)
        self.spin_max_4k_pixels_save_multiplier.setObjectName(u"spin_max_4k_pixels_save_multiplier")
        self.spin_max_4k_pixels_save_multiplier.setMinimum(2)
        self.spin_max_4k_pixels_save_multiplier.setMaximum(100)

        self.horizontalLayout_14.addWidget(self.spin_max_4k_pixels_save_multiplier)

        self.label_11 = QLabel(self.groupBox_8)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_14.addWidget(self.label_11)


        self.verticalLayout_7.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.spin_similarity_thresh = QDoubleSpinBox(self.groupBox_8)
        self.spin_similarity_thresh.setObjectName(u"spin_similarity_thresh")
        self.spin_similarity_thresh.setMaximum(0.990000000000000)
        self.spin_similarity_thresh.setSingleStep(0.050000000000000)

        self.horizontalLayout_16.addWidget(self.spin_similarity_thresh)

        self.label_12 = QLabel(self.groupBox_8)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_16.addWidget(self.label_12)


        self.verticalLayout_7.addLayout(self.horizontalLayout_16)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.lineEdit_external_image_editor_path = QLineEdit(self.groupBox_8)
        self.lineEdit_external_image_editor_path.setObjectName(u"lineEdit_external_image_editor_path")
        sizePolicy1.setHeightForWidth(self.lineEdit_external_image_editor_path.sizePolicy().hasHeightForWidth())
        self.lineEdit_external_image_editor_path.setSizePolicy(sizePolicy1)

        self.horizontalLayout_17.addWidget(self.lineEdit_external_image_editor_path)

        self.label_13 = QLabel(self.groupBox_8)
        self.label_13.setObjectName(u"label_13")
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)

        self.horizontalLayout_17.addWidget(self.label_13)


        self.verticalLayout_7.addLayout(self.horizontalLayout_17)

        self.check_filter_remove_series = QCheckBox(self.groupBox_8)
        self.check_filter_remove_series.setObjectName(u"check_filter_remove_series")

        self.verticalLayout_7.addWidget(self.check_filter_remove_series)

        self.check_filter_remove_metadata = QCheckBox(self.groupBox_8)
        self.check_filter_remove_metadata.setObjectName(u"check_filter_remove_metadata")

        self.verticalLayout_7.addWidget(self.check_filter_remove_metadata)

        self.check_filter_remove_characters = QCheckBox(self.groupBox_8)
        self.check_filter_remove_characters.setObjectName(u"check_filter_remove_characters")

        self.verticalLayout_7.addWidget(self.check_filter_remove_characters)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.spinBox_custom_height = QSpinBox(self.groupBox_8)
        self.spinBox_custom_height.setObjectName(u"spinBox_custom_height")
        self.spinBox_custom_height.setMaximum(4096)
        self.spinBox_custom_height.setValue(1024)

        self.horizontalLayout_18.addWidget(self.spinBox_custom_height)

        self.spinBox_custom_width = QSpinBox(self.groupBox_8)
        self.spinBox_custom_width.setObjectName(u"spinBox_custom_width")
        self.spinBox_custom_width.setMaximum(4096)
        self.spinBox_custom_width.setValue(1024)

        self.horizontalLayout_18.addWidget(self.spinBox_custom_width)

        self.spinBox_custom_bucket_steps = QSpinBox(self.groupBox_8)
        self.spinBox_custom_bucket_steps.setObjectName(u"spinBox_custom_bucket_steps")
        self.spinBox_custom_bucket_steps.setMinimum(1)
        self.spinBox_custom_bucket_steps.setMaximum(128)
        self.spinBox_custom_bucket_steps.setValue(64)

        self.horizontalLayout_18.addWidget(self.spinBox_custom_bucket_steps)


        self.horizontalLayout_5.addLayout(self.horizontalLayout_18)

        self.label_15 = QLabel(self.groupBox_8)
        self.label_15.setObjectName(u"label_15")

        self.horizontalLayout_5.addWidget(self.label_15)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(-1, -1, -1, 10)
        self.spinBox_sample_count = QSpinBox(self.groupBox_8)
        self.spinBox_sample_count.setObjectName(u"spinBox_sample_count")
        self.spinBox_sample_count.setValue(5)

        self.horizontalLayout_20.addWidget(self.spinBox_sample_count)

        self.label_16 = QLabel(self.groupBox_8)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_20.addWidget(self.label_16)


        self.verticalLayout_7.addLayout(self.horizontalLayout_20)


        self.gridLayout.addWidget(self.groupBox_8, 2, 0, 1, 1)

        self.groupBox_7 = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_7)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(-1, 12, -1, -1)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.lineEdit_automatic_tagger = QLineEdit(self.groupBox_7)
        self.lineEdit_automatic_tagger.setObjectName(u"lineEdit_automatic_tagger")

        self.horizontalLayout_6.addWidget(self.lineEdit_automatic_tagger)

        self.label_3 = QLabel(self.groupBox_7)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.label_3)


        self.verticalLayout_6.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.spin_swinv2_thresh = QDoubleSpinBox(self.groupBox_7)
        self.spin_swinv2_thresh.setObjectName(u"spin_swinv2_thresh")
        self.spin_swinv2_thresh.setMaximum(0.990000000000000)
        self.spin_swinv2_thresh.setSingleStep(0.050000000000000)

        self.horizontalLayout_7.addWidget(self.spin_swinv2_thresh)

        self.label_4 = QLabel(self.groupBox_7)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_7.addWidget(self.label_4)


        self.verticalLayout_6.addLayout(self.horizontalLayout_7)

        self.check_swinv2_chara = QCheckBox(self.groupBox_7)
        self.check_swinv2_chara.setObjectName(u"check_swinv2_chara")

        self.verticalLayout_6.addWidget(self.check_swinv2_chara)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.spin_swinv2_chara_thresh = QDoubleSpinBox(self.groupBox_7)
        self.spin_swinv2_chara_thresh.setObjectName(u"spin_swinv2_chara_thresh")
        self.spin_swinv2_chara_thresh.setMaximum(0.990000000000000)
        self.spin_swinv2_chara_thresh.setSingleStep(0.050000000000000)

        self.horizontalLayout_8.addWidget(self.spin_swinv2_chara_thresh)

        self.label_5 = QLabel(self.groupBox_7)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_8.addWidget(self.label_5)


        self.verticalLayout_6.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.spin_swinv2_chara_count = QSpinBox(self.groupBox_7)
        self.spin_swinv2_chara_count.setObjectName(u"spin_swinv2_chara_count")
        self.spin_swinv2_chara_count.setMinimum(100)
        self.spin_swinv2_chara_count.setMaximum(100000)
        self.spin_swinv2_chara_count.setSingleStep(100)

        self.horizontalLayout_9.addWidget(self.spin_swinv2_chara_count)

        self.label_6 = QLabel(self.groupBox_7)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_9.addWidget(self.label_6)


        self.verticalLayout_6.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.spin_caformer_thresh = QDoubleSpinBox(self.groupBox_7)
        self.spin_caformer_thresh.setObjectName(u"spin_caformer_thresh")
        self.spin_caformer_thresh.setMaximum(0.990000000000000)
        self.spin_caformer_thresh.setSingleStep(0.050000000000000)

        self.horizontalLayout_10.addWidget(self.spin_caformer_thresh)

        self.label_7 = QLabel(self.groupBox_7)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_10.addWidget(self.label_7)


        self.verticalLayout_6.addLayout(self.horizontalLayout_10)


        self.gridLayout.addWidget(self.groupBox_7, 1, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_15.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.pushButton_cancel_settings = QPushButton(self.tab_2)
        self.pushButton_cancel_settings.setObjectName(u"pushButton_cancel_settings")

        self.horizontalLayout_15.addWidget(self.pushButton_cancel_settings)

        self.pushButton_reload_default = QPushButton(self.tab_2)
        self.pushButton_reload_default.setObjectName(u"pushButton_reload_default")

        self.horizontalLayout_15.addWidget(self.pushButton_reload_default)

        self.pushButton_save_settings = QPushButton(self.tab_2)
        self.pushButton_save_settings.setObjectName(u"pushButton_save_settings")

        self.horizontalLayout_15.addWidget(self.pushButton_save_settings)


        self.gridLayout_15.addLayout(self.horizontalLayout_15, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.databaseTabWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Hecate Tagger", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_database_folder.setToolTip(QCoreApplication.translate("MainWindow", u"path that will be used by the buttons below", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_database_folder.setText("")
        self.lineEdit_database_folder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Database Folder", None))
#if QT_CONFIG(tooltip)
        self.pushButton_load_database.setToolTip(QCoreApplication.translate("MainWindow", u"load the database in memory", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_load_database.setText(QCoreApplication.translate("MainWindow", u"Load Database", None))
#if QT_CONFIG(tooltip)
        self.pushButton_save_database.setToolTip(QCoreApplication.translate("MainWindow", u"save the database that is in memory", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_save_database.setText(QCoreApplication.translate("MainWindow", u"Save Database", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"Pre-Processing Tools", None))
#if QT_CONFIG(tooltip)
        self.pushButton_convert_images_to_png.setToolTip(QCoreApplication.translate("MainWindow", u"use the path above", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_convert_images_to_png.setText(QCoreApplication.translate("MainWindow", u"Convert images to PNG (destructive)", None))
#if QT_CONFIG(tooltip)
        self.pushButton_rename_images_md5.setToolTip(QCoreApplication.translate("MainWindow", u"use the path above", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_rename_images_md5.setText(QCoreApplication.translate("MainWindow", u"Rename images to MD5 (destructive)", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Database Validation Tools", None))
#if QT_CONFIG(tooltip)
        self.pushButton_rescores.setToolTip(QCoreApplication.translate("MainWindow", u"only change the score tags for existing images in the dataset", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_rescores.setText(QCoreApplication.translate("MainWindow", u"Re-evaluate Aesthetics", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reautotags.setToolTip(QCoreApplication.translate("MainWindow", u"only change the automatic tags for existing images in the dataset (you retain your manually added tags and rejected and conflicts, ...)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reautotags.setText(QCoreApplication.translate("MainWindow", u"Re-AutoTag images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reclassify.setToolTip(QCoreApplication.translate("MainWindow", u"only change the classification for existing images in the dataset", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reclassify.setText(QCoreApplication.translate("MainWindow", u"Re-Classify images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_filter_images.setToolTip(QCoreApplication.translate("MainWindow", u"apply the filter to the database", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_filter_images.setText(QCoreApplication.translate("MainWindow", u"Filter images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_images_existence.setToolTip(QCoreApplication.translate("MainWindow", u"correct the images paths and md5 stored", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_images_existence.setText(QCoreApplication.translate("MainWindow", u"Check existence of images", None))
#if QT_CONFIG(tooltip)
        self.pushButton_rehash.setToolTip(QCoreApplication.translate("MainWindow", u"refind the md5 of the image (could fail be careful, experimental feature)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_rehash.setText(QCoreApplication.translate("MainWindow", u"Rehash images in database", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Group Management Tools", None))
#if QT_CONFIG(tooltip)
        self.pushButton_move_files_groupings.setToolTip(QCoreApplication.translate("MainWindow", u"move images from the database to their corresponding groups (destructive be careful, you could lose information)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_move_files_groupings.setText(QCoreApplication.translate("MainWindow", u"Move files according to groupings (move images)", None))
#if QT_CONFIG(tooltip)
        self.pushButton_rebuild_groups.setToolTip(QCoreApplication.translate("MainWindow", u"delete all groups and add images to groups following the directory structure", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_rebuild_groups.setText(QCoreApplication.translate("MainWindow", u"Rebuild groups (doesn't move images, remove actual groups)", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("MainWindow", u"External Database Tools", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_secondary_db_folder.setToolTip(QCoreApplication.translate("MainWindow", u"Enter the location of the secondary database", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_secondary_db_folder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter secondary database folder", None))
#if QT_CONFIG(tooltip)
        self.pushButton_load_and_merge_secondary.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>There's two database at play.</p><p><br/></p><p>The primary database loaded at the top and the secondary database entered right above this button.<br/><br/>This will search for any duplicate md5 hashes in both databases and pull tags from the secondary database and update the content of the primary database.<br/><br/>This is useful if you're importing tags from a previously cleaned database</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_load_and_merge_secondary.setText(QCoreApplication.translate("MainWindow", u"Load secondary database and merge tags", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Output Captions/Tags", None))
#if QT_CONFIG(tooltip)
        self.checkBox_remove_tag_in_sentence.setToolTip(QCoreApplication.translate("MainWindow", u"remove tags if in sentence, so no repetitive", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_remove_tag_in_sentence.setText(QCoreApplication.translate("MainWindow", u"Remove tag if included in sentence", None))
#if QT_CONFIG(tooltip)
        self.checkBox_trigger_tags.setToolTip(QCoreApplication.translate("MainWindow", u"put trigger tags at the front", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_trigger_tags.setText(QCoreApplication.translate("MainWindow", u"Trigger Tags", None))
#if QT_CONFIG(tooltip)
        self.plainTextEdit_secondary_trigger_tags.setToolTip(QCoreApplication.translate("MainWindow", u"tags separated by commas that will be put at the front, after the main trigger tags and that will have their order randomized", None))
#endif // QT_CONFIG(tooltip)
        self.plainTextEdit_secondary_trigger_tags.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Secondary Trigger Tag(s), Separate with \",\"", None))
#if QT_CONFIG(tooltip)
        self.checkBox_aesthetic_score.setToolTip(QCoreApplication.translate("MainWindow", u"put the aesthetic score in the final output", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_aesthetic_score.setText(QCoreApplication.translate("MainWindow", u"Aesthetic Score", None))
#if QT_CONFIG(tooltip)
        self.checkBox_token_separator.setToolTip(QCoreApplication.translate("MainWindow", u"use the token separator to separate the trigger tags from the rest", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_token_separator.setText(QCoreApplication.translate("MainWindow", u"Token Separator", None))
#if QT_CONFIG(tooltip)
        self.checkBox_sentence_in_token_separator.setToolTip(QCoreApplication.translate("MainWindow", u"put the sentence in the token separator", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_sentence_in_token_separator.setText(QCoreApplication.translate("MainWindow", u"Sentence in token separator", None))
#if QT_CONFIG(tooltip)
        self.checkBox_sentence.setToolTip(QCoreApplication.translate("MainWindow", u"output the sentence in the tags", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_sentence.setText(QCoreApplication.translate("MainWindow", u"Sentence", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_main_trigger_tags.setToolTip(QCoreApplication.translate("MainWindow", u"tags separated by commas that will be put at the front, the list is ordered", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_main_trigger_tags.setInputMask("")
        self.lineEdit_main_trigger_tags.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Main Trigger Tag(s), Separate with \",\"", None))
#if QT_CONFIG(tooltip)
        self.pushButton_create_txt_files.setToolTip(QCoreApplication.translate("MainWindow", u"create txt files with the settings from the left, txt files are named after the image path", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_create_txt_files.setText(QCoreApplication.translate("MainWindow", u"Create .txt Files", None))
#if QT_CONFIG(tooltip)
        self.pushButton_create_sample_toml.setToolTip(QCoreApplication.translate("MainWindow", u"do some filtering and generate example prompts based off the dataset, and makes a toml file (currently using the pony template) in the database location", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_create_sample_toml.setText(QCoreApplication.translate("MainWindow", u"Create sample TOML", None))
        self.comboBox_toml_resolution.setItemText(0, QCoreApplication.translate("MainWindow", u"SDXL", None))
        self.comboBox_toml_resolution.setItemText(1, QCoreApplication.translate("MainWindow", u"SD1.5", None))
        self.comboBox_toml_resolution.setItemText(2, QCoreApplication.translate("MainWindow", u"SD1.0", None))
        self.comboBox_toml_resolution.setItemText(3, QCoreApplication.translate("MainWindow", u"Custom", None))

#if QT_CONFIG(tooltip)
        self.comboBox_toml_resolution.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>this defines the base output resolution in the toml (using buckets)</p><p>SDXL: (1024, 1024)</p><p>SD1.5: (768, 768)</p><p>SD1.0: (512, 512)</p><p>Custom Resolution: (modify in setting)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.pushButton_print_unknown_tags.setToolTip(QCoreApplication.translate("MainWindow", u"useful for making the tag categories csv, prints tags that are known by tagger, that are not listed in the tag category", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_print_unknown_tags.setText(QCoreApplication.translate("MainWindow", u"Print unknown tags", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Database Edit Tools", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Checkpoint Tools", None))
#if QT_CONFIG(tooltip)
        self.pushButton_create_meta_cap.setToolTip(QCoreApplication.translate("MainWindow", u"when making checkpoints, permits the making of npz, currently uses preprocess settings from the basic tools tab", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_create_meta_cap.setText(QCoreApplication.translate("MainWindow", u"Create meta_cap.json", None))
#if QT_CONFIG(tooltip)
        self.pushButton_export_npz.setToolTip(QCoreApplication.translate("MainWindow", u"used for making our Eclipse XL model", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_export_npz.setText(QCoreApplication.translate("MainWindow", u"Move All .npz and update metadata json", None))
#if QT_CONFIG(tooltip)
        self.pushButton_merge_metacap.setToolTip(QCoreApplication.translate("MainWindow", u"used for making our EclipseXL model", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_merge_metacap.setText(QCoreApplication.translate("MainWindow", u"Merge meta_cap.json", None))
#if QT_CONFIG(tooltip)
        self.pushButton_rename_all.setToolTip(QCoreApplication.translate("MainWindow", u"used for our eclipseXL model", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_rename_all.setText(QCoreApplication.translate("MainWindow", u"Rename all img files in db (update lat and cap json), also npz + txt", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_dataset_folder.setToolTip(QCoreApplication.translate("MainWindow", u"folder mainly used by the tools below", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_dataset_folder.setText("")
        self.lineEdit_dataset_folder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Dataset Folder", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Checkpoint Tools", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.widget), QCoreApplication.translate("MainWindow", u"Database Tools", None))
        self.pushButton_view_database.setText(QCoreApplication.translate("MainWindow", u"View Database", None))
        self.lineEdit_view_database_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Database Directory", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.databasesViewTab), QCoreApplication.translate("MainWindow", u"View Databases", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"UI", None))
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("MainWindow", u"font size", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("MainWindow", u"Font Size", None))
#if QT_CONFIG(tooltip)
        self.label_2.setToolTip(QCoreApplication.translate("MainWindow", u"maximum size for the images to be loaded in the view (increasing it can have huge impact on load time and RAM usage)", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Image Load Size", None))
        self.checkBox_enable_image_tooltip.setText(QCoreApplication.translate("MainWindow", u"Enable Image Tooltip in the Database View", None))
        self.comboBox_click_option.setItemText(0, QCoreApplication.translate("MainWindow", u"Single Click", None))
        self.comboBox_click_option.setItemText(1, QCoreApplication.translate("MainWindow", u"Double Click", None))

        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Tag Edit Click Count", None))
        self.checkBox_hide_sentence_in_view.setText(QCoreApplication.translate("MainWindow", u"Hide Sentence in the Database View", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", u"Misc", None))
#if QT_CONFIG(tooltip)
        self.label_8.setToolTip(QCoreApplication.translate("MainWindow", u"used for the taggers, recommended 8 but if the VRAM is lacking we recommend to reduce it", None))
#endif // QT_CONFIG(tooltip)
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Max Batch Size", None))
        self.lineEdit_keep_token_tag_separator.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter special separator used to split trigger tag and general tags (We use \"|||\")", None))
#if QT_CONFIG(tooltip)
        self.label_9.setToolTip(QCoreApplication.translate("MainWindow", u"the string that should be used when using the keep token tag separator", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Keep Token Tags Separator", None))
#if QT_CONFIG(tooltip)
        self.check_remove_transparency_from_images.setToolTip(QCoreApplication.translate("MainWindow", u"when in the image tools, should the tool remove transparency from images (currently changed to a white background)", None))
#endif // QT_CONFIG(tooltip)
        self.check_remove_transparency_from_images.setText(QCoreApplication.translate("MainWindow", u"Remove Transparency for Images", None))
#if QT_CONFIG(tooltip)
        self.label_10.setToolTip(QCoreApplication.translate("MainWindow", u"probably don't change it, used everywhere and could really impact your performance if too high", None))
#endif // QT_CONFIG(tooltip)
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Max Images Loader Thread", None))
        self.spin_max_4k_pixels_save_multiplier.setSuffix("")
#if QT_CONFIG(tooltip)
        self.label_11.setToolTip(QCoreApplication.translate("MainWindow", u"for images tools, the max number of images to be loaded at the same time, in pixel count", None))
#endif // QT_CONFIG(tooltip)
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Max 4k Pixels Save Multiplier", None))
#if QT_CONFIG(tooltip)
        self.label_12.setToolTip(QCoreApplication.translate("MainWindow", u"when calculating similarity, which rate of similarity should be considered", None))
#endif // QT_CONFIG(tooltip)
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Similarity Threshold", None))
        self.lineEdit_external_image_editor_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Image Editing Software .exe Path (Photoshop, Gimp, Krita, etc)", None))
#if QT_CONFIG(tooltip)
        self.label_13.setToolTip(QCoreApplication.translate("MainWindow", u"path to the image editor that should be used to open images, if not specified, the default app will be launched", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"External Image Editor Path", None))
        self.check_filter_remove_series.setText(QCoreApplication.translate("MainWindow", u"Filter remove series", None))
        self.check_filter_remove_metadata.setText(QCoreApplication.translate("MainWindow", u"Filter remove metadata", None))
        self.check_filter_remove_characters.setText(QCoreApplication.translate("MainWindow", u"Filter remove characters", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Custom WxH and bucket steps for sample toml", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Prompt count for sample toml", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"Tagger", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("MainWindow", u"if you don't like one tagger or the other, mainly use both, available currently: SWINV2V3,CAFORMER,SWINV2V2", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Automatic Tagger", None))
#if QT_CONFIG(tooltip)
        self.label_4.setToolTip(QCoreApplication.translate("MainWindow", u"the threshold for wich to add tags from the swinv2 tagger", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Swinv2 Threshold", None))
#if QT_CONFIG(tooltip)
        self.check_swinv2_chara.setToolTip(QCoreApplication.translate("MainWindow", u"whether to tag the characters (characters are tagged only when using swinv2 or both)", None))
#endif // QT_CONFIG(tooltip)
        self.check_swinv2_chara.setText(QCoreApplication.translate("MainWindow", u"Swinv2 Enable Characters", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("MainWindow", u"the threshold for wich to addcharacter tags from the swinv2 tagger", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Swinv2 Character Threshold", None))
        self.spin_swinv2_chara_count.setSuffix("")
#if QT_CONFIG(tooltip)
        self.label_6.setToolTip(QCoreApplication.translate("MainWindow", u"using the danbooru tags, the number of images required to add the character to the tags for the image (used after the threshold)", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Swinv2 Character Count Threshold", None))
#if QT_CONFIG(tooltip)
        self.label_7.setToolTip(QCoreApplication.translate("MainWindow", u"threshold for tags to be added by caformer", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Caformer Threshold", None))
#if QT_CONFIG(tooltip)
        self.pushButton_cancel_settings.setToolTip(QCoreApplication.translate("MainWindow", u"cancel the changes, doesn't restore to defaults, it only restore the previous setting, if yyou want to restore the default, delete the .ini file that acts as the config", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_cancel_settings.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reload_default.setToolTip(QCoreApplication.translate("MainWindow", u"Load the default settings, but doesn't save them", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reload_default.setText(QCoreApplication.translate("MainWindow", u"Load Default Settings", None))
#if QT_CONFIG(tooltip)
        self.pushButton_save_settings.setToolTip(QCoreApplication.translate("MainWindow", u"save the settings for the changes to take effects, either relaunch the app or, in the case of the database view, reopen the database", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_save_settings.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

