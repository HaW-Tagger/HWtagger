# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rectangleTagsBase.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QListView, QPlainTextEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1069, 299)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.listView_full_tags = QListView(Form)
        self.listView_full_tags.setObjectName(u"listView_full_tags")
        self.listView_full_tags.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_full_tags.setFlow(QListView.LeftToRight)
        self.listView_full_tags.setProperty("isWrapping", True)
        self.listView_full_tags.setResizeMode(QListView.Adjust)

        self.verticalLayout_4.addWidget(self.listView_full_tags)

        self.lineEdit_full_tags = QLineEdit(Form)
        self.lineEdit_full_tags.setObjectName(u"lineEdit_full_tags")

        self.verticalLayout_4.addWidget(self.lineEdit_full_tags)

        self.plainTextEdit_sentence = QPlainTextEdit(Form)
        self.plainTextEdit_sentence.setObjectName(u"plainTextEdit_sentence")

        self.verticalLayout_4.addWidget(self.plainTextEdit_sentence)


        self.horizontalLayout.addLayout(self.verticalLayout_4)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout.addWidget(self.line)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_name = QLabel(Form)
        self.label_name.setObjectName(u"label_name")

        self.verticalLayout_3.addWidget(self.label_name)

        self.pushButton_pick_color = QPushButton(Form)
        self.pushButton_pick_color.setObjectName(u"pushButton_pick_color")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_pick_color.sizePolicy().hasHeightForWidth())
        self.pushButton_pick_color.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.pushButton_pick_color)

        self.pushButton_edit_rect = QPushButton(Form)
        self.pushButton_edit_rect.setObjectName(u"pushButton_edit_rect")
        sizePolicy.setHeightForWidth(self.pushButton_edit_rect.sizePolicy().hasHeightForWidth())
        self.pushButton_edit_rect.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.pushButton_edit_rect)

        self.pushButton_delete = QPushButton(Form)
        self.pushButton_delete.setObjectName(u"pushButton_delete")
        sizePolicy.setHeightForWidth(self.pushButton_delete.sizePolicy().hasHeightForWidth())
        self.pushButton_delete.setSizePolicy(sizePolicy)

        self.verticalLayout_3.addWidget(self.pushButton_delete)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_name.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.pushButton_pick_color.setText(QCoreApplication.translate("Form", u"Color", None))
        self.pushButton_edit_rect.setText(QCoreApplication.translate("Form", u"Edit Rect", None))
        self.pushButton_delete.setText(QCoreApplication.translate("Form", u"Delete", None))
    # retranslateUi

