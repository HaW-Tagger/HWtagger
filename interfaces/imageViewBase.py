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
    QComboBox, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QListView, QPushButton,
    QSizePolicy, QSlider, QStackedWidget, QVBoxLayout,
    QWidget)

from CustomWidgets import PaintingImage

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(508, 844)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.stackedWidget = QStackedWidget(Form)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_2 = QVBoxLayout(self.page)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.pushButton_deleted_group = QPushButton(self.page)
        self.pushButton_deleted_group.setObjectName(u"pushButton_deleted_group")

        self.horizontalLayout.addWidget(self.pushButton_deleted_group)

        self.pushButton_add_group = QPushButton(self.page)
        self.pushButton_add_group.setObjectName(u"pushButton_add_group")
        icon = QIcon(QIcon.fromTheme(u"list-add"))
        self.pushButton_add_group.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButton_add_group)

        self.comboBox_group_name = QComboBox(self.page)
        self.comboBox_group_name.setObjectName(u"comboBox_group_name")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_group_name.sizePolicy().hasHeightForWidth())
        self.comboBox_group_name.setSizePolicy(sizePolicy)
        self.comboBox_group_name.setEditable(False)
        self.comboBox_group_name.setMinimumContentsLength(1)
        self.comboBox_group_name.setFrame(True)
        self.comboBox_group_name.setModelColumn(0)

        self.horizontalLayout.addWidget(self.comboBox_group_name)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.comboBox_sort_type = QComboBox(self.page)
        self.comboBox_sort_type.setObjectName(u"comboBox_sort_type")

        self.horizontalLayout_5.addWidget(self.comboBox_sort_type)

        self.checkBox_reverse = QCheckBox(self.page)
        self.checkBox_reverse.setObjectName(u"checkBox_reverse")

        self.horizontalLayout_5.addWidget(self.checkBox_reverse)

        self.checkBox_include_sentence = QCheckBox(self.page)
        self.checkBox_include_sentence.setObjectName(u"checkBox_include_sentence")

        self.horizontalLayout_5.addWidget(self.checkBox_include_sentence)

        self.lineEdit_tag_search = QLineEdit(self.page)
        self.lineEdit_tag_search.setObjectName(u"lineEdit_tag_search")

        self.horizontalLayout_5.addWidget(self.lineEdit_tag_search)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.listView_groups = QListView(self.page)
        self.listView_groups.setObjectName(u"listView_groups")
        self.listView_groups.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.listView_groups.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout_2.addWidget(self.listView_groups)

        self.listView_other = QListView(self.page)
        self.listView_other.setObjectName(u"listView_other")
        self.listView_other.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.listView_other.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout_2.addWidget(self.listView_other)

        self.widget = QWidget(self.page)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pushButton_add_selection_to_group = QPushButton(self.widget)
        self.pushButton_add_selection_to_group.setObjectName(u"pushButton_add_selection_to_group")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton_add_selection_to_group.sizePolicy().hasHeightForWidth())
        self.pushButton_add_selection_to_group.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.pushButton_add_selection_to_group)

        self.pushButton_remove_selection_from_group = QPushButton(self.widget)
        self.pushButton_remove_selection_from_group.setObjectName(u"pushButton_remove_selection_from_group")
        sizePolicy1.setHeightForWidth(self.pushButton_remove_selection_from_group.sizePolicy().hasHeightForWidth())
        self.pushButton_remove_selection_from_group.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.pushButton_remove_selection_from_group)

        self.checkBox_toggle_ungrouped_images = QCheckBox(self.widget)
        self.checkBox_toggle_ungrouped_images.setObjectName(u"checkBox_toggle_ungrouped_images")
        self.checkBox_toggle_ungrouped_images.setTristate(False)

        self.horizontalLayout_2.addWidget(self.checkBox_toggle_ungrouped_images)


        self.verticalLayout_2.addWidget(self.widget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSlider_thumbnail_size = QSlider(self.page)
        self.horizontalSlider_thumbnail_size.setObjectName(u"horizontalSlider_thumbnail_size")
        self.horizontalSlider_thumbnail_size.setOrientation(Qt.Horizontal)

        self.horizontalLayout_3.addWidget(self.horizontalSlider_thumbnail_size)

        self.label_image_view_count = QLabel(self.page)
        self.label_image_view_count.setObjectName(u"label_image_view_count")

        self.horizontalLayout_3.addWidget(self.label_image_view_count)

        self.checkBox_single_selection_mode = QCheckBox(self.page)
        self.checkBox_single_selection_mode.setObjectName(u"checkBox_single_selection_mode")

        self.horizontalLayout_3.addWidget(self.checkBox_single_selection_mode)

        self.checkBox_zoom_on_click = QCheckBox(self.page)
        self.checkBox_zoom_on_click.setObjectName(u"checkBox_zoom_on_click")

        self.horizontalLayout_3.addWidget(self.checkBox_zoom_on_click)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout = QGridLayout(self.page_2)
        self.gridLayout.setSpacing(3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.single_image = PaintingImage(self.page_2)
        self.single_image.setObjectName(u"single_image")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.single_image.sizePolicy().hasHeightForWidth())
        self.single_image.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.single_image, 2, 0, 1, 3)

        self.pushButton_prev_image = QPushButton(self.page_2)
        self.pushButton_prev_image.setObjectName(u"pushButton_prev_image")
        sizePolicy.setHeightForWidth(self.pushButton_prev_image.sizePolicy().hasHeightForWidth())
        self.pushButton_prev_image.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton_prev_image, 3, 0, 1, 1)

        self.single_info_label = QLabel(self.page_2)
        self.single_info_label.setObjectName(u"single_info_label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.single_info_label.sizePolicy().hasHeightForWidth())
        self.single_info_label.setSizePolicy(sizePolicy3)
        self.single_info_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.single_info_label, 1, 0, 1, 3)

        self.pushButton_next_image = QPushButton(self.page_2)
        self.pushButton_next_image.setObjectName(u"pushButton_next_image")
        sizePolicy.setHeightForWidth(self.pushButton_next_image.sizePolicy().hasHeightForWidth())
        self.pushButton_next_image.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton_next_image, 3, 2, 1, 1)

        self.checkBox_masking = QCheckBox(self.page_2)
        self.checkBox_masking.setObjectName(u"checkBox_masking")
        self.checkBox_masking.setCheckable(True)

        self.gridLayout.addWidget(self.checkBox_masking, 3, 1, 1, 1)

        self.label_image_md5 = QLabel(self.page_2)
        self.label_image_md5.setObjectName(u"label_image_md5")
        sizePolicy3.setHeightForWidth(self.label_image_md5.sizePolicy().hasHeightForWidth())
        self.label_image_md5.setSizePolicy(sizePolicy3)
        self.label_image_md5.setAlignment(Qt.AlignCenter)
        self.label_image_md5.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.gridLayout.addWidget(self.label_image_md5, 0, 0, 1, 3)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout.addWidget(self.stackedWidget)


        self.retranslateUi(Form)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.pushButton_deleted_group.setToolTip(QCoreApplication.translate("Form", u"delete the group (doesn't delete the images)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_deleted_group.setText(QCoreApplication.translate("Form", u"Delete group", None))
#if QT_CONFIG(tooltip)
        self.pushButton_add_group.setToolTip(QCoreApplication.translate("Form", u"create a new group", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_add_group.setText(QCoreApplication.translate("Form", u"Add Group", None))
#if QT_CONFIG(tooltip)
        self.comboBox_group_name.setToolTip(QCoreApplication.translate("Form", u"list of groups", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.comboBox_sort_type.setToolTip(QCoreApplication.translate("Form", u"sorting images view, some sorting requires calculations", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.checkBox_reverse.setToolTip(QCoreApplication.translate("Form", u"reverse the sort", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_reverse.setText(QCoreApplication.translate("Form", u"Reverse", None))
        self.checkBox_include_sentence.setText(QCoreApplication.translate("Form", u"Sentence", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_tag_search.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Enter text to search for tags:</p><p>By default, it search for any partial matches</p><p>- use the star, &quot;*&quot;, as a wildcard for any number of characters in that position. can be placed in between, before, or after other characters</p><p>- place quotation marks, &quot; &quot;, around the text for exact keyword search</p><p>- use the minus sign, &quot;-&quot;, in front of the text to remove images with that keyword</p><p>- search source_&lt;source name&gt; to filter where the tags came from. Ex: source_Swin, source_Caformer, source_danbooru, source_manual ...</p><p>- search group_&lt;group name&gt; to filter where images are grouped. Ex: group_from_behind, group_from above, ...</p><p>- special seach keywords (we only have 1 tag rn): &quot;2persons&quot; --&gt; search for images with tag combinations that implies 2 people in the image, ex: &quot;1boy&quot; + &quot;1girl&quot;, &quot;2girls&quot;, &quot;2boys&quot;, etc</p><p>Separate multiple tag searches using &quot;,&quot;</p></b"
                        "ody></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_tag_search.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Tag(s) to Search", None))
#if QT_CONFIG(tooltip)
        self.pushButton_add_selection_to_group.setToolTip(QCoreApplication.translate("Form", u"add all images selected at the bottom to the group", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_add_selection_to_group.setText(QCoreApplication.translate("Form", u"Add selection to group", None))
#if QT_CONFIG(tooltip)
        self.pushButton_remove_selection_from_group.setToolTip(QCoreApplication.translate("Form", u"remove all selected images in the top view from the group", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_remove_selection_from_group.setText(QCoreApplication.translate("Form", u"Remove selection from group", None))
#if QT_CONFIG(tooltip)
        self.checkBox_toggle_ungrouped_images.setToolTip(QCoreApplication.translate("Form", u"show all images in the bottom group except if they belong to the top group", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_toggle_ungrouped_images.setText(QCoreApplication.translate("Form", u"Show grouped", None))
#if QT_CONFIG(tooltip)
        self.horizontalSlider_thumbnail_size.setToolTip(QCoreApplication.translate("Form", u"change the viewed image size", None))
#endif // QT_CONFIG(tooltip)
        self.label_image_view_count.setText(QCoreApplication.translate("Form", u"TextLabel", None))
#if QT_CONFIG(tooltip)
        self.checkBox_single_selection_mode.setToolTip(QCoreApplication.translate("Form", u"toggle single or multi-selection, tick the checkbox to disable multi-selection. You can only selcted one image at a time.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_single_selection_mode.setText(QCoreApplication.translate("Form", u"Disable multi-selection", None))
#if QT_CONFIG(tooltip)
        self.checkBox_zoom_on_click.setToolTip(QCoreApplication.translate("Form", u"If checked, when selecting one image it will be shown large, wih buttons enabling you to slide right or left of the view", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_zoom_on_click.setText(QCoreApplication.translate("Form", u"Zoom", None))
        self.pushButton_prev_image.setText(QCoreApplication.translate("Form", u"<-", None))
        self.single_info_label.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.pushButton_next_image.setText(QCoreApplication.translate("Form", u"->", None))
        self.checkBox_masking.setText(QCoreApplication.translate("Form", u"Masking", None))
        self.label_image_md5.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

