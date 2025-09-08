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
        Form.resize(596, 844)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.stackedWidget = QStackedWidget(Form)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        font = QFont()
        font.setPointSize(7)
        self.page.setFont(font)
        self.verticalLayout_2 = QVBoxLayout(self.page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.pushButton_deleted_group = QPushButton(self.page)
        self.pushButton_deleted_group.setObjectName(u"pushButton_deleted_group")
        self.pushButton_deleted_group.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout.addWidget(self.pushButton_deleted_group)

        self.pushButton_add_group = QPushButton(self.page)
        self.pushButton_add_group.setObjectName(u"pushButton_add_group")
        self.pushButton_add_group.setMaximumSize(QSize(16777215, 30))
        icon = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.pushButton_add_group.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButton_add_group)

        self.comboBox_group_name = QComboBox(self.page)
        self.comboBox_group_name.setObjectName(u"comboBox_group_name")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_group_name.sizePolicy().hasHeightForWidth())
        self.comboBox_group_name.setSizePolicy(sizePolicy)
        self.comboBox_group_name.setMaximumSize(QSize(16777215, 30))
        self.comboBox_group_name.setEditable(False)
        self.comboBox_group_name.setMinimumContentsLength(1)
        self.comboBox_group_name.setFrame(True)
        self.comboBox_group_name.setModelColumn(0)

        self.horizontalLayout.addWidget(self.comboBox_group_name)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 2)
        self.comboBox_sort_type = QComboBox(self.page)
        self.comboBox_sort_type.setObjectName(u"comboBox_sort_type")
        self.comboBox_sort_type.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_5.addWidget(self.comboBox_sort_type)

        self.checkBox_reverse = QCheckBox(self.page)
        self.checkBox_reverse.setObjectName(u"checkBox_reverse")
        self.checkBox_reverse.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_5.addWidget(self.checkBox_reverse)

        self.checkBox_include_sentence = QCheckBox(self.page)
        self.checkBox_include_sentence.setObjectName(u"checkBox_include_sentence")
        self.checkBox_include_sentence.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_5.addWidget(self.checkBox_include_sentence)

        self.checkBox_remove_manual = QCheckBox(self.page)
        self.checkBox_remove_manual.setObjectName(u"checkBox_remove_manual")

        self.horizontalLayout_5.addWidget(self.checkBox_remove_manual)

        self.lineEdit_tag_search = QLineEdit(self.page)
        self.lineEdit_tag_search.setObjectName(u"lineEdit_tag_search")
        self.lineEdit_tag_search.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_5.addWidget(self.lineEdit_tag_search)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.listView_groups = QListView(self.page)
        self.listView_groups.setObjectName(u"listView_groups")
        self.listView_groups.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.listView_groups.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout_2.addWidget(self.listView_groups)

        self.view_page_interfaces = QWidget(self.page)
        self.view_page_interfaces.setObjectName(u"view_page_interfaces")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.view_page_interfaces.sizePolicy().hasHeightForWidth())
        self.view_page_interfaces.setSizePolicy(sizePolicy1)
        self.view_page_interfaces.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_6 = QHBoxLayout(self.view_page_interfaces)
        self.horizontalLayout_6.setSpacing(2)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_page_num = QLabel(self.view_page_interfaces)
        self.label_page_num.setObjectName(u"label_page_num")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_page_num.sizePolicy().hasHeightForWidth())
        self.label_page_num.setSizePolicy(sizePolicy2)
        self.label_page_num.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_6.addWidget(self.label_page_num)

        self.pushButton_prev_button = QPushButton(self.view_page_interfaces)
        self.pushButton_prev_button.setObjectName(u"pushButton_prev_button")
        sizePolicy2.setHeightForWidth(self.pushButton_prev_button.sizePolicy().hasHeightForWidth())
        self.pushButton_prev_button.setSizePolicy(sizePolicy2)
        self.pushButton_prev_button.setMaximumSize(QSize(150, 30))

        self.horizontalLayout_6.addWidget(self.pushButton_prev_button)

        self.pushButton_2_next_button = QPushButton(self.view_page_interfaces)
        self.pushButton_2_next_button.setObjectName(u"pushButton_2_next_button")
        self.pushButton_2_next_button.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pushButton_2_next_button.sizePolicy().hasHeightForWidth())
        self.pushButton_2_next_button.setSizePolicy(sizePolicy2)
        self.pushButton_2_next_button.setMaximumSize(QSize(150, 30))
        self.pushButton_2_next_button.setIconSize(QSize(12, 12))

        self.horizontalLayout_6.addWidget(self.pushButton_2_next_button)

        self.lineEdit_Entered_pageNum = QLineEdit(self.view_page_interfaces)
        self.lineEdit_Entered_pageNum.setObjectName(u"lineEdit_Entered_pageNum")
        sizePolicy2.setHeightForWidth(self.lineEdit_Entered_pageNum.sizePolicy().hasHeightForWidth())
        self.lineEdit_Entered_pageNum.setSizePolicy(sizePolicy2)
        self.lineEdit_Entered_pageNum.setMinimumSize(QSize(10, 0))
        self.lineEdit_Entered_pageNum.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_6.addWidget(self.lineEdit_Entered_pageNum)

        self.pushButton_3_jump_page_button = QPushButton(self.view_page_interfaces)
        self.pushButton_3_jump_page_button.setObjectName(u"pushButton_3_jump_page_button")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pushButton_3_jump_page_button.sizePolicy().hasHeightForWidth())
        self.pushButton_3_jump_page_button.setSizePolicy(sizePolicy3)
        self.pushButton_3_jump_page_button.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_6.addWidget(self.pushButton_3_jump_page_button)


        self.verticalLayout_2.addWidget(self.view_page_interfaces)

        self.listView_other = QListView(self.page)
        self.listView_other.setObjectName(u"listView_other")
        self.listView_other.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.listView_other.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout_2.addWidget(self.listView_other)

        self.other_view_page_interfaces = QWidget(self.page)
        self.other_view_page_interfaces.setObjectName(u"other_view_page_interfaces")
        self.other_view_page_interfaces.setEnabled(True)
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.other_view_page_interfaces.sizePolicy().hasHeightForWidth())
        self.other_view_page_interfaces.setSizePolicy(sizePolicy4)
        self.other_view_page_interfaces.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_8 = QHBoxLayout(self.other_view_page_interfaces)
        self.horizontalLayout_8.setSpacing(2)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_page_num_other = QLabel(self.other_view_page_interfaces)
        self.label_page_num_other.setObjectName(u"label_page_num_other")
        sizePolicy2.setHeightForWidth(self.label_page_num_other.sizePolicy().hasHeightForWidth())
        self.label_page_num_other.setSizePolicy(sizePolicy2)
        self.label_page_num_other.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.label_page_num_other)

        self.pushButton_prev_button_other = QPushButton(self.other_view_page_interfaces)
        self.pushButton_prev_button_other.setObjectName(u"pushButton_prev_button_other")
        sizePolicy2.setHeightForWidth(self.pushButton_prev_button_other.sizePolicy().hasHeightForWidth())
        self.pushButton_prev_button_other.setSizePolicy(sizePolicy2)
        self.pushButton_prev_button_other.setMaximumSize(QSize(150, 30))

        self.horizontalLayout_8.addWidget(self.pushButton_prev_button_other)

        self.pushButton_2_next_button_other = QPushButton(self.other_view_page_interfaces)
        self.pushButton_2_next_button_other.setObjectName(u"pushButton_2_next_button_other")
        self.pushButton_2_next_button_other.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.pushButton_2_next_button_other.sizePolicy().hasHeightForWidth())
        self.pushButton_2_next_button_other.setSizePolicy(sizePolicy2)
        self.pushButton_2_next_button_other.setMaximumSize(QSize(150, 30))
        self.pushButton_2_next_button_other.setIconSize(QSize(12, 12))

        self.horizontalLayout_8.addWidget(self.pushButton_2_next_button_other)

        self.lineEdit_Entered_pageNum_other = QLineEdit(self.other_view_page_interfaces)
        self.lineEdit_Entered_pageNum_other.setObjectName(u"lineEdit_Entered_pageNum_other")
        sizePolicy2.setHeightForWidth(self.lineEdit_Entered_pageNum_other.sizePolicy().hasHeightForWidth())
        self.lineEdit_Entered_pageNum_other.setSizePolicy(sizePolicy2)
        self.lineEdit_Entered_pageNum_other.setMinimumSize(QSize(10, 0))
        self.lineEdit_Entered_pageNum_other.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_8.addWidget(self.lineEdit_Entered_pageNum_other)

        self.pushButton_3_jump_page_button_other = QPushButton(self.other_view_page_interfaces)
        self.pushButton_3_jump_page_button_other.setObjectName(u"pushButton_3_jump_page_button_other")
        sizePolicy3.setHeightForWidth(self.pushButton_3_jump_page_button_other.sizePolicy().hasHeightForWidth())
        self.pushButton_3_jump_page_button_other.setSizePolicy(sizePolicy3)
        self.pushButton_3_jump_page_button_other.setMaximumSize(QSize(100, 30))

        self.horizontalLayout_8.addWidget(self.pushButton_3_jump_page_button_other)


        self.verticalLayout_2.addWidget(self.other_view_page_interfaces)

        self.widget = QWidget(self.page)
        self.widget.setObjectName(u"widget")
        sizePolicy4.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy4)
        self.widget.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.pushButton_add_selection_to_group = QPushButton(self.widget)
        self.pushButton_add_selection_to_group.setObjectName(u"pushButton_add_selection_to_group")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.pushButton_add_selection_to_group.sizePolicy().hasHeightForWidth())
        self.pushButton_add_selection_to_group.setSizePolicy(sizePolicy5)
        self.pushButton_add_selection_to_group.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_add_selection_to_group)

        self.pushButton_remove_selection_from_group = QPushButton(self.widget)
        self.pushButton_remove_selection_from_group.setObjectName(u"pushButton_remove_selection_from_group")
        sizePolicy5.setHeightForWidth(self.pushButton_remove_selection_from_group.sizePolicy().hasHeightForWidth())
        self.pushButton_remove_selection_from_group.setSizePolicy(sizePolicy5)
        self.pushButton_remove_selection_from_group.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.pushButton_remove_selection_from_group)

        self.checkBox_toggle_ungrouped_images = QCheckBox(self.widget)
        self.checkBox_toggle_ungrouped_images.setObjectName(u"checkBox_toggle_ungrouped_images")
        sizePolicy3.setHeightForWidth(self.checkBox_toggle_ungrouped_images.sizePolicy().hasHeightForWidth())
        self.checkBox_toggle_ungrouped_images.setSizePolicy(sizePolicy3)
        self.checkBox_toggle_ungrouped_images.setTristate(False)

        self.horizontalLayout_2.addWidget(self.checkBox_toggle_ungrouped_images)


        self.verticalLayout_2.addWidget(self.widget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSlider_thumbnail_size = QSlider(self.page)
        self.horizontalSlider_thumbnail_size.setObjectName(u"horizontalSlider_thumbnail_size")
        self.horizontalSlider_thumbnail_size.setMaximumSize(QSize(16777215, 30))
        self.horizontalSlider_thumbnail_size.setOrientation(Qt.Horizontal)

        self.horizontalLayout_3.addWidget(self.horizontalSlider_thumbnail_size)

        self.label_image_view_count = QLabel(self.page)
        self.label_image_view_count.setObjectName(u"label_image_view_count")
        self.label_image_view_count.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.label_image_view_count)

        self.checkBox_single_selection_mode = QCheckBox(self.page)
        self.checkBox_single_selection_mode.setObjectName(u"checkBox_single_selection_mode")
        self.checkBox_single_selection_mode.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_3.addWidget(self.checkBox_single_selection_mode)

        self.checkBox_zoom_on_click = QCheckBox(self.page)
        self.checkBox_zoom_on_click.setObjectName(u"checkBox_zoom_on_click")
        self.checkBox_zoom_on_click.setMaximumSize(QSize(16777215, 30))

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
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.single_image.sizePolicy().hasHeightForWidth())
        self.single_image.setSizePolicy(sizePolicy6)

        self.gridLayout.addWidget(self.single_image, 2, 0, 1, 3)

        self.pushButton_prev_image = QPushButton(self.page_2)
        self.pushButton_prev_image.setObjectName(u"pushButton_prev_image")
        sizePolicy.setHeightForWidth(self.pushButton_prev_image.sizePolicy().hasHeightForWidth())
        self.pushButton_prev_image.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton_prev_image, 3, 0, 1, 1)

        self.single_info_label = QLabel(self.page_2)
        self.single_info_label.setObjectName(u"single_info_label")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.single_info_label.sizePolicy().hasHeightForWidth())
        self.single_info_label.setSizePolicy(sizePolicy7)
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
        sizePolicy7.setHeightForWidth(self.label_image_md5.sizePolicy().hasHeightForWidth())
        self.label_image_md5.setSizePolicy(sizePolicy7)
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
        self.checkBox_remove_manual.setText(QCoreApplication.translate("Form", u"remove manual", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_tag_search.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Enter text to search for tags:</p><p>By default, it search for any partial matches</p><p>- use the star, &quot;*&quot;, as a wildcard for any number of characters in that position. can be placed in between, before, or after other characters</p><p>- place quotation marks, &quot; &quot;, around the text for exact keyword search</p><p>- use the minus sign, &quot;-&quot;, in front of the text to remove images with that keyword</p><p>- search source_&lt;source name&gt; to filter where the tags came from. Ex: source_Swin, source_Caformer, source_danbooru, source_manual ...</p><p>- search group_&lt;group name&gt; to filter where images are grouped. Ex: group_from_behind, group_from above, ...</p><p>- special seach keywords (we only have 1 tag rn): &quot;2persons&quot; --&gt; search for images with tag combinations that implies 2 people in the image, ex: &quot;1boy&quot; + &quot;1girl&quot;, &quot;2girls&quot;, &quot;2boys&quot;, etc</p><p>Separate multiple tag searches using &quot;,&quot;</p></b"
                        "ody></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_tag_search.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Tag(s) to Search", None))
#if QT_CONFIG(tooltip)
        self.listView_groups.setToolTip(QCoreApplication.translate("Form", u"This is a placeholder listview, will be rebuilt in app", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.listView_groups.setStatusTip(QCoreApplication.translate("Form", u"This is a placeholder listview, will be rebuilt in app", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.listView_groups.setWhatsThis(QCoreApplication.translate("Form", u"This is a placeholder listview, will be rebuilt in app", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(accessibility)
        self.listView_groups.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.label_page_num.setText(QCoreApplication.translate("Form", u"Page: 0/0, Img 0/0", None))
        self.pushButton_prev_button.setText(QCoreApplication.translate("Form", u"Previous", None))
        self.pushButton_2_next_button.setText(QCoreApplication.translate("Form", u"Next", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_Entered_pageNum.setToolTip(QCoreApplication.translate("Form", u"Jump to page number", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_Entered_pageNum.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Page Number", None))
        self.pushButton_3_jump_page_button.setText(QCoreApplication.translate("Form", u"Go To Page", None))
#if QT_CONFIG(tooltip)
        self.listView_other.setToolTip(QCoreApplication.translate("Form", u"This is a placeholder listview, will be rebuilt in app", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.listView_other.setStatusTip(QCoreApplication.translate("Form", u"This is a placeholder listview, will be rebuilt in app", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.listView_other.setWhatsThis(QCoreApplication.translate("Form", u"This is a placeholder listview, will be rebuilt in app", None))
#endif // QT_CONFIG(whatsthis)
        self.label_page_num_other.setText(QCoreApplication.translate("Form", u"Page: 0/0, Img 0/0", None))
        self.pushButton_prev_button_other.setText(QCoreApplication.translate("Form", u"Previous", None))
        self.pushButton_2_next_button_other.setText(QCoreApplication.translate("Form", u"Next", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_Entered_pageNum_other.setToolTip(QCoreApplication.translate("Form", u"Jump to page number", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_Entered_pageNum_other.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Page Number", None))
        self.pushButton_3_jump_page_button_other.setText(QCoreApplication.translate("Form", u"Go To Page", None))
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

