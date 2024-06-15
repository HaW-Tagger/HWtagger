# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'imageViewBase.ui'
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
    QComboBox, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QListView, QPushButton, QSizePolicy,
    QSlider, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(497, 844)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.comboBox_group_name = QComboBox(Form)
        self.comboBox_group_name.setObjectName(u"comboBox_group_name")
        self.comboBox_group_name.setEditable(False)
        self.comboBox_group_name.setMinimumContentsLength(1)
        self.comboBox_group_name.setFrame(True)
        self.comboBox_group_name.setModelColumn(0)

        self.horizontalLayout.addWidget(self.comboBox_group_name)

        self.pushButton_add_group = QPushButton(Form)
        self.pushButton_add_group.setObjectName(u"pushButton_add_group")
        icon = QIcon(QIcon.fromTheme(u"list-add"))
        self.pushButton_add_group.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButton_add_group)

        self.comboBox_sort_type = QComboBox(Form)
        self.comboBox_sort_type.setObjectName(u"comboBox_sort_type")

        self.horizontalLayout.addWidget(self.comboBox_sort_type)

        self.checkBox_reverse = QCheckBox(Form)
        self.checkBox_reverse.setObjectName(u"checkBox_reverse")

        self.horizontalLayout.addWidget(self.checkBox_reverse)

        self.lineEdit_tag_search = QLineEdit(Form)
        self.lineEdit_tag_search.setObjectName(u"lineEdit_tag_search")

        self.horizontalLayout.addWidget(self.lineEdit_tag_search)

        self.pushButton_clear_search = QPushButton(Form)
        self.pushButton_clear_search.setObjectName(u"pushButton_clear_search")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_clear_search.sizePolicy().hasHeightForWidth())
        self.pushButton_clear_search.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.pushButton_clear_search)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.listView_groups = QListView(Form)
        self.listView_groups.setObjectName(u"listView_groups")
        self.listView_groups.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.listView_groups.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout.addWidget(self.listView_groups)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton_add_selection_to_group = QPushButton(Form)
        self.pushButton_add_selection_to_group.setObjectName(u"pushButton_add_selection_to_group")

        self.horizontalLayout_2.addWidget(self.pushButton_add_selection_to_group)

        self.pushButton_remove_selection_from_group = QPushButton(Form)
        self.pushButton_remove_selection_from_group.setObjectName(u"pushButton_remove_selection_from_group")

        self.horizontalLayout_2.addWidget(self.pushButton_remove_selection_from_group)

        self.pushButton_deleted_group = QPushButton(Form)
        self.pushButton_deleted_group.setObjectName(u"pushButton_deleted_group")

        self.horizontalLayout_2.addWidget(self.pushButton_deleted_group)

        self.checkBox_toggle_ungrouped_images = QCheckBox(Form)
        self.checkBox_toggle_ungrouped_images.setObjectName(u"checkBox_toggle_ungrouped_images")
        self.checkBox_toggle_ungrouped_images.setTristate(False)

        self.horizontalLayout_2.addWidget(self.checkBox_toggle_ungrouped_images)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.listView_other = QListView(Form)
        self.listView_other.setObjectName(u"listView_other")
        self.listView_other.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.listView_other.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout.addWidget(self.listView_other)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSlider_thumbnail_size = QSlider(Form)
        self.horizontalSlider_thumbnail_size.setObjectName(u"horizontalSlider_thumbnail_size")
        self.horizontalSlider_thumbnail_size.setOrientation(Qt.Horizontal)

        self.horizontalLayout_3.addWidget(self.horizontalSlider_thumbnail_size)

        self.label_image_view_count = QLabel(Form)
        self.label_image_view_count.setObjectName(u"label_image_view_count")

        self.horizontalLayout_3.addWidget(self.label_image_view_count)

        self.checkBox_single_selection_mode = QCheckBox(Form)
        self.checkBox_single_selection_mode.setObjectName(u"checkBox_single_selection_mode")

        self.horizontalLayout_3.addWidget(self.checkBox_single_selection_mode)

        self.checkBox_zoom_on_click = QCheckBox(Form)
        self.checkBox_zoom_on_click.setObjectName(u"checkBox_zoom_on_click")

        self.horizontalLayout_3.addWidget(self.checkBox_zoom_on_click)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.pushButton_add_group.setToolTip(QCoreApplication.translate("Form", u"create a new group", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_add_group.setText(QCoreApplication.translate("Form", u"Add Group", None))
#if QT_CONFIG(tooltip)
        self.comboBox_sort_type.setToolTip(QCoreApplication.translate("Form", u"sorting images view, some sorting requires calculations", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.checkBox_reverse.setToolTip(QCoreApplication.translate("Form", u"reverse the sort", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_reverse.setText(QCoreApplication.translate("Form", u"Reverse Search", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_tag_search.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Use tags to search:</p><p>- use * to imply any number of characters in between, before or after</p><p>- use &quot;&quot; to imply exact keyword search</p><p>- use - to imply that you don't want to see the tag</p><p>Separate searches using &quot;,&quot;</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_tag_search.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Tag(s) to Search", None))
#if QT_CONFIG(tooltip)
        self.pushButton_clear_search.setToolTip(QCoreApplication.translate("Form", u"clear the search", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_clear_search.setText(QCoreApplication.translate("Form", u"Clear", None))
#if QT_CONFIG(tooltip)
        self.pushButton_add_selection_to_group.setToolTip(QCoreApplication.translate("Form", u"add all images selected at the bottom to the group", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_add_selection_to_group.setText(QCoreApplication.translate("Form", u"Add selection to group", None))
#if QT_CONFIG(tooltip)
        self.pushButton_remove_selection_from_group.setToolTip(QCoreApplication.translate("Form", u"remove all selected images in the top view from the group", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_remove_selection_from_group.setText(QCoreApplication.translate("Form", u"Remove selection from group", None))
#if QT_CONFIG(tooltip)
        self.pushButton_deleted_group.setToolTip(QCoreApplication.translate("Form", u"delete the group (doesn't delete the images)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_deleted_group.setText(QCoreApplication.translate("Form", u"Delete group", None))
#if QT_CONFIG(tooltip)
        self.checkBox_toggle_ungrouped_images.setToolTip(QCoreApplication.translate("Form", u"show all images in the bottom group except if they belong to the top group", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_toggle_ungrouped_images.setText(QCoreApplication.translate("Form", u"ungrouped", None))
#if QT_CONFIG(tooltip)
        self.horizontalSlider_thumbnail_size.setToolTip(QCoreApplication.translate("Form", u"change the viewed image size", None))
#endif // QT_CONFIG(tooltip)
        self.label_image_view_count.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.checkBox_single_selection_mode.setToolTip(QCoreApplication.translate("Form", u"toggle multi-selection", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_single_selection_mode.setText(QCoreApplication.translate("Form", u"single", None))
#if QT_CONFIG(tooltip)
        self.checkBox_zoom_on_click.setToolTip(QCoreApplication.translate("Form", u"If checked, when selecting one image it will be shown large, wih buttons enabling you to slide right or left of the view", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_zoom_on_click.setText(QCoreApplication.translate("Form", u"zoom", None))
    # retranslateUi

