# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'image_tools.ui'
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
    QLabel, QLineEdit, QListView, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(734, 763)
        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setAutoFillBackground(False)
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.DirectoryText = QLineEdit(self.widget)
        self.DirectoryText.setObjectName(u"DirectoryText")

        self.gridLayout_5.addWidget(self.DirectoryText, 0, 0, 1, 1)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setBold(True)
        self.label_2.setFont(font)

        self.gridLayout_6.addWidget(self.label_2, 0, 1, 1, 1)

        self.ImageList = QListView(self.widget)
        self.ImageList.setObjectName(u"ImageList")

        self.gridLayout_6.addWidget(self.ImageList, 2, 1, 1, 1)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.checkBox = QCheckBox(self.widget)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setEnabled(False)

        self.gridLayout_3.addWidget(self.checkBox, 11, 0, 1, 2)

        self.checkImgSize = QPushButton(self.widget)
        self.checkImgSize.setObjectName(u"checkImgSize")

        self.gridLayout_3.addWidget(self.checkImgSize, 1, 0, 1, 2)

        self.SaveImages = QPushButton(self.widget)
        self.SaveImages.setObjectName(u"SaveImages")

        self.gridLayout_3.addWidget(self.SaveImages, 25, 0, 1, 1)

        self.pushButton_process_all = QPushButton(self.widget)
        self.pushButton_process_all.setObjectName(u"pushButton_process_all")

        self.gridLayout_3.addWidget(self.pushButton_process_all, 17, 0, 1, 2)

        self.updateDB = QCheckBox(self.widget)
        self.updateDB.setObjectName(u"updateDB")
        self.updateDB.setChecked(True)

        self.gridLayout_3.addWidget(self.updateDB, 14, 0, 1, 2)

        self.OverrideOriginal = QCheckBox(self.widget)
        self.OverrideOriginal.setObjectName(u"OverrideOriginal")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.OverrideOriginal.sizePolicy().hasHeightForWidth())
        self.OverrideOriginal.setSizePolicy(sizePolicy)
        self.OverrideOriginal.setChecked(True)

        self.gridLayout_3.addWidget(self.OverrideOriginal, 12, 0, 2, 2)

        self.line_3 = QFrame(self.widget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_3, 4, 0, 1, 2)

        self.ConvertTransparent = QCheckBox(self.widget)
        self.ConvertTransparent.setObjectName(u"ConvertTransparent")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ConvertTransparent.sizePolicy().hasHeightForWidth())
        self.ConvertTransparent.setSizePolicy(sizePolicy1)
        self.ConvertTransparent.setMaximumSize(QSize(16777215, 100))
        self.ConvertTransparent.setChecked(True)

        self.gridLayout_3.addWidget(self.ConvertTransparent, 8, 0, 1, 2)

        self.CropEdge = QCheckBox(self.widget)
        self.CropEdge.setObjectName(u"CropEdge")
        self.CropEdge.setChecked(True)

        self.gridLayout_3.addWidget(self.CropEdge, 9, 0, 1, 2)

        self.NextPage = QPushButton(self.widget)
        self.NextPage.setObjectName(u"NextPage")
        self.NextPage.setEnabled(False)

        self.gridLayout_3.addWidget(self.NextPage, 25, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 19, 0, 1, 1)

        self.line_2 = QFrame(self.widget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_2, 20, 0, 1, 2)

        self.CropBorder = QCheckBox(self.widget)
        self.CropBorder.setObjectName(u"CropBorder")
        self.CropBorder.setChecked(True)

        self.gridLayout_3.addWidget(self.CropBorder, 10, 0, 1, 2)

        self.ProcessImages = QPushButton(self.widget)
        self.ProcessImages.setObjectName(u"ProcessImages")

        self.gridLayout_3.addWidget(self.ProcessImages, 16, 0, 1, 2)

        self.checkDupeHash = QCheckBox(self.widget)
        self.checkDupeHash.setObjectName(u"checkDupeHash")
        self.checkDupeHash.setChecked(True)

        self.gridLayout_3.addWidget(self.checkDupeHash, 5, 0, 1, 2)

        self.checkImageType = QPushButton(self.widget)
        self.checkImageType.setObjectName(u"checkImageType")

        self.gridLayout_3.addWidget(self.checkImageType, 6, 0, 1, 2)

        self.line_5 = QFrame(self.widget)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_5, 7, 0, 1, 2)

        self.exportSmall = QPushButton(self.widget)
        self.exportSmall.setObjectName(u"exportSmall")

        self.gridLayout_3.addWidget(self.exportSmall, 2, 0, 1, 2)

        self.line_4 = QFrame(self.widget)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_4, 0, 0, 1, 2)


        self.gridLayout_6.addLayout(self.gridLayout_3, 2, 2, 1, 1)

        self.line = QFrame(self.widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_6.addWidget(self.line, 1, 1, 1, 2)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setMaximumSize(QSize(16777215, 100))
        self.label.setFont(font)

        self.gridLayout_6.addWidget(self.label, 0, 2, 1, 1)


        self.gridLayout_5.addLayout(self.gridLayout_6, 3, 0, 1, 2)

        self.LoadDirectory = QPushButton(self.widget)
        self.LoadDirectory.setObjectName(u"LoadDirectory")

        self.gridLayout_5.addWidget(self.LoadDirectory, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_5, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.DirectoryText.setToolTip(QCoreApplication.translate("Form", u"enter image location, database file is not necessary to process the imgs, RECOMMENDED to process imgs here before procedding with database creation", None))
#endif // QT_CONFIG(tooltip)
        self.DirectoryText.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Image Directory", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Images: (Before & After)", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"Identify Texts (Super Slow rn)", None))
#if QT_CONFIG(tooltip)
        self.checkImgSize.setToolTip(QCoreApplication.translate("Form", u"No need to load directory, only type a valid dir in the top field.  Recursively check the directories and find images not suited for XL training (total img pixels < 640 x 768) ", None))
#endif // QT_CONFIG(tooltip)
        self.checkImgSize.setText(QCoreApplication.translate("Form", u"Find Small Images (for XL)", None))
        self.SaveImages.setText(QCoreApplication.translate("Form", u"Save Images/DB", None))
#if QT_CONFIG(tooltip)
        self.pushButton_process_all.setToolTip(QCoreApplication.translate("Form", u"Process ALL images in the directory using the checked criterions, skips confirmation by user", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_process_all.setText(QCoreApplication.translate("Form", u"Process ALL Images (Skip check)", None))
#if QT_CONFIG(tooltip)
        self.updateDB.setToolTip(QCoreApplication.translate("Form", u"This will update the md5 hashes in the database when the \"Save Images\" is clicked", None))
#endif // QT_CONFIG(tooltip)
        self.updateDB.setText(QCoreApplication.translate("Form", u"Update Database (if it exists)", None))
#if QT_CONFIG(tooltip)
        self.OverrideOriginal.setToolTip(QCoreApplication.translate("Form", u"The new images that are saved when you click \"save Image\" at the bottom of the page will overwrite the original.  If unchecked, it will use the original name + \"post_edit\" as it's new name", None))
#endif // QT_CONFIG(tooltip)
        self.OverrideOriginal.setText(QCoreApplication.translate("Form", u"Override Original Image", None))
#if QT_CONFIG(tooltip)
        self.ConvertTransparent.setToolTip(QCoreApplication.translate("Form", u"This will make a new layer that is white and paste it below the transparent image", None))
#endif // QT_CONFIG(tooltip)
        self.ConvertTransparent.setText(QCoreApplication.translate("Form", u"Convert Trasparent to White", None))
#if QT_CONFIG(tooltip)
        self.CropEdge.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>This will crop empty spaces (monocolor or weak gradient) </p><p>and will leave a ~2% (relative to original dim) pad around the subject</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.CropEdge.setText(QCoreApplication.translate("Form", u"Crop Edges to Subject", None))
#if QT_CONFIG(tooltip)
        self.NextPage.setToolTip(QCoreApplication.translate("Form", u"this button will activate if you're processing images ", None))
#endif // QT_CONFIG(tooltip)
        self.NextPage.setText(QCoreApplication.translate("Form", u"Next Page ->", None))
#if QT_CONFIG(tooltip)
        self.CropBorder.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>This will identify a border by checking sides that goes from monocolor or </p><p>weak gradient to a sudden change in color. Then crop without a padding.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.CropBorder.setText(QCoreApplication.translate("Form", u"Crop Borders", None))
#if QT_CONFIG(tooltip)
        self.ProcessImages.setToolTip(QCoreApplication.translate("Form", u"Process images (up to max 4k pixels multiplier in settings tab) using the checked criterions, this will cache the results and ask the user for confirmation in the side window", None))
#endif // QT_CONFIG(tooltip)
        self.ProcessImages.setText(QCoreApplication.translate("Form", u"Process Images", None))
#if QT_CONFIG(tooltip)
        self.checkDupeHash.setToolTip(QCoreApplication.translate("Form", u"Check for duplicate hashes and moves them out (Directory needs to be loaded for this)", None))
#endif // QT_CONFIG(tooltip)
        self.checkDupeHash.setText(QCoreApplication.translate("Form", u"Check Dupe Hashes", None))
#if QT_CONFIG(tooltip)
        self.checkImageType.setToolTip(QCoreApplication.translate("Form", u"This will convert non jpeg/jpg/png images to png and print out truncated files that are not used for training.", None))
#endif // QT_CONFIG(tooltip)
        self.checkImageType.setText(QCoreApplication.translate("Form", u"Convert/Print/Move Bad Images", None))
#if QT_CONFIG(tooltip)
        self.exportSmall.setToolTip(QCoreApplication.translate("Form", u"Run after button above, this will make a new folder in the directory and move all small images while keeping the folder structure", None))
#endif // QT_CONFIG(tooltip)
        self.exportSmall.setText(QCoreApplication.translate("Form", u"Export Small Images (for XL)", None))
        self.label.setText(QCoreApplication.translate("Form", u"Settings:", None))
#if QT_CONFIG(tooltip)
        self.LoadDirectory.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.LoadDirectory.setText(QCoreApplication.translate("Form", u"Load Directory", None))
    # retranslateUi

