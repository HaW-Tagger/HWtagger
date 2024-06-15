# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'global_database_view.ui'
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
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1175, 705)
        self.gridLayout_5 = QGridLayout(Form)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea_databases = QScrollArea(Form)
        self.scrollArea_databases.setObjectName(u"scrollArea_databases")
        self.scrollArea_databases.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea_databases.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_databases.setWidgetResizable(True)
        self.scrollArea_databases.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 563, 606))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollArea_databases.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea_databases, 2, 0, 1, 3)

        self.checkBox_import_best_great = QCheckBox(Form)
        self.checkBox_import_best_great.setObjectName(u"checkBox_import_best_great")

        self.gridLayout.addWidget(self.checkBox_import_best_great, 3, 0, 1, 3)

        self.pushButton_search = QPushButton(Form)
        self.pushButton_search.setObjectName(u"pushButton_search")

        self.gridLayout.addWidget(self.pushButton_search, 1, 2, 1, 1)

        self.lineEdit_global_folder_path = QLineEdit(Form)
        self.lineEdit_global_folder_path.setObjectName(u"lineEdit_global_folder_path")

        self.gridLayout.addWidget(self.lineEdit_global_folder_path, 0, 0, 1, 3)

        self.checkBox_presearch_existence_of_images = QCheckBox(Form)
        self.checkBox_presearch_existence_of_images.setObjectName(u"checkBox_presearch_existence_of_images")

        self.gridLayout.addWidget(self.checkBox_presearch_existence_of_images, 1, 0, 1, 2)

        self.pushButton_validate_choice = QPushButton(Form)
        self.pushButton_validate_choice.setObjectName(u"pushButton_validate_choice")

        self.gridLayout.addWidget(self.pushButton_validate_choice, 4, 0, 1, 3)


        self.gridLayout_5.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pushButton_images_existence = QPushButton(Form)
        self.pushButton_images_existence.setObjectName(u"pushButton_images_existence")

        self.verticalLayout.addWidget(self.pushButton_images_existence)

        self.checkBox_save_databases_as_groups = QCheckBox(Form)
        self.checkBox_save_databases_as_groups.setObjectName(u"checkBox_save_databases_as_groups")

        self.verticalLayout.addWidget(self.checkBox_save_databases_as_groups)

        self.checkBox_reorganize_folder = QCheckBox(Form)
        self.checkBox_reorganize_folder.setObjectName(u"checkBox_reorganize_folder")

        self.verticalLayout.addWidget(self.checkBox_reorganize_folder)

        self.pushButton_merge_datasets = QPushButton(Form)
        self.pushButton_merge_datasets.setObjectName(u"pushButton_merge_datasets")

        self.verticalLayout.addWidget(self.pushButton_merge_datasets)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.pushButton_generate_quality_graph = QPushButton(Form)
        self.pushButton_generate_quality_graph.setObjectName(u"pushButton_generate_quality_graph")

        self.verticalLayout.addWidget(self.pushButton_generate_quality_graph)

        self.pushButton_create_metacap = QPushButton(Form)
        self.pushButton_create_metacap.setObjectName(u"pushButton_create_metacap")

        self.verticalLayout.addWidget(self.pushButton_create_metacap)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout_5.addLayout(self.verticalLayout, 0, 1, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.checkBox_import_best_great.setToolTip(QCoreApplication.translate("Form", u"import only images that contains the 3 top quality tags, choose before validating choice", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_import_best_great.setText(QCoreApplication.translate("Form", u"Import only masterpiece, best, great", None))
#if QT_CONFIG(tooltip)
        self.pushButton_search.setToolTip(QCoreApplication.translate("Form", u"search and load the databases in the selected folder", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_search.setText(QCoreApplication.translate("Form", u"Search", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_global_folder_path.setToolTip(QCoreApplication.translate("Form", u"path to the global database folder thet should contains databases", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_global_folder_path.setInputMask("")
        self.lineEdit_global_folder_path.setPlaceholderText(QCoreApplication.translate("Form", u"Global Folder Path", None))
#if QT_CONFIG(tooltip)
        self.checkBox_presearch_existence_of_images.setToolTip(QCoreApplication.translate("Form", u"when loading check if the images in the databases exists, more powerful than the button on the right panel", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_presearch_existence_of_images.setText(QCoreApplication.translate("Form", u"Check existence of Images for all databases", None))
#if QT_CONFIG(tooltip)
        self.pushButton_validate_choice.setToolTip(QCoreApplication.translate("Form", u"selecte the images from the databases and store the choice", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_validate_choice.setText(QCoreApplication.translate("Form", u"Validate Choice", None))
#if QT_CONFIG(tooltip)
        self.pushButton_images_existence.setToolTip(QCoreApplication.translate("Form", u"check if the validated images exists, simple check", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_images_existence.setText(QCoreApplication.translate("Form", u"Check validated images existence", None))
#if QT_CONFIG(tooltip)
        self.checkBox_save_databases_as_groups.setToolTip(QCoreApplication.translate("Form", u"if not selected the images won't belong to any group", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_save_databases_as_groups.setText(QCoreApplication.translate("Form", u"Save databases origins as groups", None))
#if QT_CONFIG(tooltip)
        self.checkBox_reorganize_folder.setToolTip(QCoreApplication.translate("Form", u"destructive, move a lot of files, could fail if images don't exist or for other reasons, ", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_reorganize_folder.setText(QCoreApplication.translate("Form", u"Reorganize the folders, (move to a backup folder) (reorganize by their groups) (rename to md5)", None))
#if QT_CONFIG(tooltip)
        self.pushButton_merge_datasets.setToolTip(QCoreApplication.translate("Form", u"Create the database.json and saves it", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_merge_datasets.setText(QCoreApplication.translate("Form", u"Merge all datasets", None))
#if QT_CONFIG(tooltip)
        self.pushButton_generate_quality_graph.setToolTip(QCoreApplication.translate("Form", u"not implemented", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_generate_quality_graph.setText(QCoreApplication.translate("Form", u"Generate quality distribution graph", None))
#if QT_CONFIG(tooltip)
        self.pushButton_create_metacap.setToolTip(QCoreApplication.translate("Form", u"not implemented", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_create_metacap.setText(QCoreApplication.translate("Form", u"Create meta_cap.json for all images in the datasets", None))
    # retranslateUi

