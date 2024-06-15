# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tagsViewBase.ui'
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
    QLabel, QLineEdit, QListView, QPlainTextEdit,
    QSizePolicy, QVBoxLayout, QWidget)

from imported_widgets import ConflictsTreeView

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(554, 847)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_image_path = QLabel(Form)
        self.label_image_path.setObjectName(u"label_image_path")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_image_path.sizePolicy().hasHeightForWidth())
        self.label_image_path.setSizePolicy(sizePolicy)
        self.label_image_path.setScaledContents(False)
        self.label_image_path.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_image_path)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_tags_len = QLabel(Form)
        self.label_tags_len.setObjectName(u"label_tags_len")

        self.horizontalLayout_2.addWidget(self.label_tags_len)

        self.label_token_len = QLabel(Form)
        self.label_token_len.setObjectName(u"label_token_len")

        self.horizontalLayout_2.addWidget(self.label_token_len)

        self.label_image_ext = QLabel(Form)
        self.label_image_ext.setObjectName(u"label_image_ext")

        self.horizontalLayout_2.addWidget(self.label_image_ext)

        self.label_image_size = QLabel(Form)
        self.label_image_size.setObjectName(u"label_image_size")

        self.horizontalLayout_2.addWidget(self.label_image_size)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.comboBox_score_tags = QComboBox(Form)
        self.comboBox_score_tags.setObjectName(u"comboBox_score_tags")

        self.horizontalLayout_3.addWidget(self.comboBox_score_tags)

        self.checkBox_reviewed = QCheckBox(Form)
        self.checkBox_reviewed.setObjectName(u"checkBox_reviewed")

        self.horizontalLayout_3.addWidget(self.checkBox_reviewed)

        self.checkBox_hide_sentence = QCheckBox(Form)
        self.checkBox_hide_sentence.setObjectName(u"checkBox_hide_sentence")
        self.checkBox_hide_sentence.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox_hide_sentence)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.listView_rejected = QListView(Form)
        self.listView_rejected.setObjectName(u"listView_rejected")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.listView_rejected.sizePolicy().hasHeightForWidth())
        self.listView_rejected.setSizePolicy(sizePolicy1)
        self.listView_rejected.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listView_rejected.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.listView_rejected.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_rejected.setProperty("showDropIndicator", False)
        self.listView_rejected.setMovement(QListView.Static)
        self.listView_rejected.setFlow(QListView.LeftToRight)
        self.listView_rejected.setProperty("isWrapping", True)
        self.listView_rejected.setResizeMode(QListView.Adjust)
        self.listView_rejected.setWordWrap(False)

        self.verticalLayout.addWidget(self.listView_rejected)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.plainTextEdit_sentence = QPlainTextEdit(Form)
        self.plainTextEdit_sentence.setObjectName(u"plainTextEdit_sentence")
        sizePolicy1.setHeightForWidth(self.plainTextEdit_sentence.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_sentence.setSizePolicy(sizePolicy1)
        self.plainTextEdit_sentence.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plainTextEdit_sentence.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.horizontalLayout.addWidget(self.plainTextEdit_sentence)

        self.label_sentence_len = QLabel(Form)
        self.label_sentence_len.setObjectName(u"label_sentence_len")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_sentence_len.sizePolicy().hasHeightForWidth())
        self.label_sentence_len.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.label_sentence_len)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.listView_tags = QListView(Form)
        self.listView_tags.setObjectName(u"listView_tags")
        self.listView_tags.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listView_tags.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_tags.setProperty("showDropIndicator", False)
        self.listView_tags.setMovement(QListView.Static)
        self.listView_tags.setFlow(QListView.LeftToRight)
        self.listView_tags.setProperty("isWrapping", True)
        self.listView_tags.setResizeMode(QListView.Adjust)
        self.listView_tags.setWordWrap(False)

        self.horizontalLayout_4.addWidget(self.listView_tags)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.treeView_conflicts = ConflictsTreeView(Form)
        self.treeView_conflicts.setObjectName(u"treeView_conflicts")
        self.treeView_conflicts.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView_conflicts.setProperty("showDropIndicator", False)
        self.treeView_conflicts.setSelectionBehavior(QAbstractItemView.SelectItems)

        self.verticalLayout_2.addWidget(self.treeView_conflicts)

        self.listView_recommendations = QListView(Form)
        self.listView_recommendations.setObjectName(u"listView_recommendations")
        self.listView_recommendations.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listView_recommendations.setDefaultDropAction(Qt.IgnoreAction)

        self.verticalLayout_2.addWidget(self.listView_recommendations)


        self.horizontalLayout_4.addLayout(self.verticalLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.lineEdit_add_tags = QLineEdit(Form)
        self.lineEdit_add_tags.setObjectName(u"lineEdit_add_tags")

        self.horizontalLayout_5.addWidget(self.lineEdit_add_tags)

        self.checkBox_clear_on_add = QCheckBox(Form)
        self.checkBox_clear_on_add.setObjectName(u"checkBox_clear_on_add")
        self.checkBox_clear_on_add.setChecked(True)

        self.horizontalLayout_5.addWidget(self.checkBox_clear_on_add)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.label_image_path.setToolTip(QCoreApplication.translate("Form", u"path of the image", None))
#endif // QT_CONFIG(tooltip)
        self.label_image_path.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_tags_len.setToolTip(QCoreApplication.translate("Form", u"count of tags in the image", None))
#endif // QT_CONFIG(tooltip)
        self.label_tags_len.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_token_len.setToolTip(QCoreApplication.translate("Form", u"count of tokens in the image", None))
#endif // QT_CONFIG(tooltip)
        self.label_token_len.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_image_ext.setToolTip(QCoreApplication.translate("Form", u"extension of the image", None))
#endif // QT_CONFIG(tooltip)
        self.label_image_ext.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.label_image_size.setToolTip(QCoreApplication.translate("Form", u"size of the image on disk", None))
#endif // QT_CONFIG(tooltip)
        self.label_image_size.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.comboBox_score_tags.setToolTip(QCoreApplication.translate("Form", u"Score of the image, can be changed, removed if necessary, the blue highlight is the curernt score", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.checkBox_reviewed.setToolTip(QCoreApplication.translate("Form", u"if an image is manually reviewed or not", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_reviewed.setText(QCoreApplication.translate("Form", u"Reviewed", None))
#if QT_CONFIG(tooltip)
        self.checkBox_hide_sentence.setToolTip(QCoreApplication.translate("Form", u"hide the sentence panel", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_hide_sentence.setText(QCoreApplication.translate("Form", u"Hide Sentence", None))
#if QT_CONFIG(tooltip)
        self.listView_rejected.setToolTip(QCoreApplication.translate("Form", u"all tags that are rejected (bold tags are manually rejected tags)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.plainTextEdit_sentence.setToolTip(QCoreApplication.translate("Form", u"the sentence is the caption that is not organized in the form of tags", None))
#endif // QT_CONFIG(tooltip)
        self.plainTextEdit_sentence.setPlaceholderText(QCoreApplication.translate("Form", u"This section stores any captions (sentences), If you're reading this message, there's no caption saved.", None))
#if QT_CONFIG(tooltip)
        self.label_sentence_len.setToolTip(QCoreApplication.translate("Form", u"the token len of the sentence", None))
#endif // QT_CONFIG(tooltip)
        self.label_sentence_len.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.listView_tags.setToolTip(QCoreApplication.translate("Form", u"the tags that will be outputed by the tagger, bold tags are manually added tags, click on tag to add it to the rejected, hold and click enter to go the tag danbooru wiki", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.treeView_conflicts.setToolTip(QCoreApplication.translate("Form", u"Tags that are recognized as conflicts, click on the category if you want to hide it for this image, consider it solve", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.listView_recommendations.setToolTip(QCoreApplication.translate("Form", u"tag recommendations based on what is present in the output", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.lineEdit_add_tags.setToolTip(QCoreApplication.translate("Form", u"add tags to this image, tags are separated by commas, press enter to validate the addition", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_add_tags.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Tags to Add (Press Enter to add tag)", None))
#if QT_CONFIG(tooltip)
        self.checkBox_clear_on_add.setToolTip(QCoreApplication.translate("Form", u"if checked, will clear the tags to add when entered", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_clear_on_add.setText(QCoreApplication.translate("Form", u"Clear on add", None))
    # retranslateUi

