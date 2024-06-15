# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dataset_cleaning.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QLabel, QLineEdit, QListView,
    QPushButton, QSizePolicy, QSlider, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(783, 780)
        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setAutoFillBackground(False)
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_dataset_cleaning = QLabel(self.widget)
        self.label_dataset_cleaning.setObjectName(u"label_dataset_cleaning")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_dataset_cleaning.sizePolicy().hasHeightForWidth())
        self.label_dataset_cleaning.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.label_dataset_cleaning, 3, 2, 1, 1)

        self.pushButton_filter_with_conditional = QPushButton(self.widget)
        self.pushButton_filter_with_conditional.setObjectName(u"pushButton_filter_with_conditional")
        sizePolicy.setHeightForWidth(self.pushButton_filter_with_conditional.sizePolicy().hasHeightForWidth())
        self.pushButton_filter_with_conditional.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.pushButton_filter_with_conditional, 1, 3, 1, 1)

        self.lineEdit_filter_phrase = QLineEdit(self.widget)
        self.lineEdit_filter_phrase.setObjectName(u"lineEdit_filter_phrase")
        sizePolicy.setHeightForWidth(self.lineEdit_filter_phrase.sizePolicy().hasHeightForWidth())
        self.lineEdit_filter_phrase.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.lineEdit_filter_phrase, 1, 2, 1, 1)

        self.label_2_dataset_cleaning = QLabel(self.widget)
        self.label_2_dataset_cleaning.setObjectName(u"label_2_dataset_cleaning")
        sizePolicy.setHeightForWidth(self.label_2_dataset_cleaning.sizePolicy().hasHeightForWidth())
        self.label_2_dataset_cleaning.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.label_2_dataset_cleaning, 3, 3, 1, 1)

        self.listView_2_dataset_cleaning = QListView(self.widget)
        self.listView_2_dataset_cleaning.setObjectName(u"listView_2_dataset_cleaning")
        palette = QPalette()
        brush = QBrush(QColor(234, 234, 234, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush1 = QBrush(QColor(240, 240, 240, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        self.listView_2_dataset_cleaning.setPalette(palette)

        self.gridLayout_3.addWidget(self.listView_2_dataset_cleaning, 4, 3, 1, 1)

        self.listView_dataset_cleaning = QListView(self.widget)
        self.listView_dataset_cleaning.setObjectName(u"listView_dataset_cleaning")
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.Base, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        self.listView_dataset_cleaning.setPalette(palette1)

        self.gridLayout_3.addWidget(self.listView_dataset_cleaning, 4, 2, 1, 1)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(-1, 0, -1, -1)
        self.slider_activation_thresh = QSlider(self.widget)
        self.slider_activation_thresh.setObjectName(u"slider_activation_thresh")
        self.slider_activation_thresh.setMinimum(50)
        self.slider_activation_thresh.setMaximum(100)
        self.slider_activation_thresh.setSliderPosition(100)
        self.slider_activation_thresh.setOrientation(Qt.Horizontal)
        self.slider_activation_thresh.setTickPosition(QSlider.TicksBelow)
        self.slider_activation_thresh.setTickInterval(5)

        self.gridLayout_7.addWidget(self.slider_activation_thresh, 1, 0, 1, 1)

        self.checkBox_filter_special = QCheckBox(self.widget)
        self.checkBox_filter_special.setObjectName(u"checkBox_filter_special")
        self.checkBox_filter_special.setChecked(True)

        self.gridLayout_7.addWidget(self.checkBox_filter_special, 0, 0, 1, 1)

        self.slider_activation_label = QLabel(self.widget)
        self.slider_activation_label.setObjectName(u"slider_activation_label")

        self.gridLayout_7.addWidget(self.slider_activation_label, 1, 1, 1, 1)

        self.slider_prob_thresh = QSlider(self.widget)
        self.slider_prob_thresh.setObjectName(u"slider_prob_thresh")
        self.slider_prob_thresh.setEnabled(False)
        self.slider_prob_thresh.setMinimum(20)
        self.slider_prob_thresh.setMaximum(100)
        self.slider_prob_thresh.setSingleStep(1)
        self.slider_prob_thresh.setSliderPosition(60)
        self.slider_prob_thresh.setOrientation(Qt.Horizontal)
        self.slider_prob_thresh.setTickPosition(QSlider.TicksBelow)
        self.slider_prob_thresh.setTickInterval(5)

        self.gridLayout_7.addWidget(self.slider_prob_thresh, 2, 0, 1, 1)

        self.slider_prob_label = QLabel(self.widget)
        self.slider_prob_label.setObjectName(u"slider_prob_label")

        self.gridLayout_7.addWidget(self.slider_prob_label, 2, 1, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout_7, 7, 0, 1, 1)

        self.checkBox_solo_check = QCheckBox(self.widget)
        self.checkBox_solo_check.setObjectName(u"checkBox_solo_check")
        self.checkBox_solo_check.setChecked(True)

        self.gridLayout_4.addWidget(self.checkBox_solo_check, 9, 0, 1, 1)

        self.pushButton_cleanup_tags = QPushButton(self.widget)
        self.pushButton_cleanup_tags.setObjectName(u"pushButton_cleanup_tags")

        self.gridLayout_4.addWidget(self.pushButton_cleanup_tags, 12, 0, 1, 1)

        self.line = QFrame(self.widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_4.addWidget(self.line, 15, 0, 1, 1)

        self.listView_searched_tags = QListView(self.widget)
        self.listView_searched_tags.setObjectName(u"listView_searched_tags")
        palette2 = QPalette()
        palette2.setBrush(QPalette.Active, QPalette.Base, brush)
        palette2.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette2.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        self.listView_searched_tags.setPalette(palette2)

        self.gridLayout_4.addWidget(self.listView_searched_tags, 18, 0, 1, 1)

        self.pushButton_apply_change = QPushButton(self.widget)
        self.pushButton_apply_change.setObjectName(u"pushButton_apply_change")

        self.gridLayout_4.addWidget(self.pushButton_apply_change, 13, 0, 1, 1)

        self.label_3_dataset_cleaning = QLabel(self.widget)
        self.label_3_dataset_cleaning.setObjectName(u"label_3_dataset_cleaning")
        font = QFont()
        font.setBold(True)
        self.label_3_dataset_cleaning.setFont(font)

        self.gridLayout_4.addWidget(self.label_3_dataset_cleaning, 2, 0, 1, 1)

        self.checkBox_use_tag_csv = QCheckBox(self.widget)
        self.checkBox_use_tag_csv.setObjectName(u"checkBox_use_tag_csv")
        self.checkBox_use_tag_csv.setChecked(False)

        self.gridLayout_4.addWidget(self.checkBox_use_tag_csv, 4, 0, 1, 1)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font)

        self.gridLayout_4.addWidget(self.label_4, 16, 0, 1, 1)

        self.line_3 = QFrame(self.widget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.gridLayout_4.addWidget(self.line_3, 19, 0, 1, 1)

        self.lineEdit_search_tags = QLineEdit(self.widget)
        self.lineEdit_search_tags.setObjectName(u"lineEdit_search_tags")

        self.gridLayout_4.addWidget(self.lineEdit_search_tags, 17, 0, 1, 1)

        self.checkBox_filter_bow = QCheckBox(self.widget)
        self.checkBox_filter_bow.setObjectName(u"checkBox_filter_bow")
        self.checkBox_filter_bow.setChecked(True)

        self.gridLayout_4.addWidget(self.checkBox_filter_bow, 5, 0, 1, 1)

        self.checkBox_symbolic_tag = QCheckBox(self.widget)
        self.checkBox_symbolic_tag.setObjectName(u"checkBox_symbolic_tag")
        self.checkBox_symbolic_tag.setChecked(True)

        self.gridLayout_4.addWidget(self.checkBox_symbolic_tag, 6, 0, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_4, 0, 5, 5, 1)

        self.comboBox_filter_method = QComboBox(self.widget)
        self.comboBox_filter_method.addItem("")
        self.comboBox_filter_method.addItem("")
        self.comboBox_filter_method.addItem("")
        self.comboBox_filter_method.addItem("")
        self.comboBox_filter_method.addItem("")
        self.comboBox_filter_method.addItem("")
        self.comboBox_filter_method.setObjectName(u"comboBox_filter_method")
        sizePolicy.setHeightForWidth(self.comboBox_filter_method.sizePolicy().hasHeightForWidth())
        self.comboBox_filter_method.setSizePolicy(sizePolicy)
        self.comboBox_filter_method.setEditable(False)
        self.comboBox_filter_method.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)

        self.gridLayout_3.addWidget(self.comboBox_filter_method, 0, 2, 1, 1)

        self.comboBox_filterGroups = QComboBox(self.widget)
        self.comboBox_filterGroups.addItem("")
        self.comboBox_filterGroups.setObjectName(u"comboBox_filterGroups")
        sizePolicy.setHeightForWidth(self.comboBox_filterGroups.sizePolicy().hasHeightForWidth())
        self.comboBox_filterGroups.setSizePolicy(sizePolicy)
        self.comboBox_filterGroups.setAutoFillBackground(False)
        self.comboBox_filterGroups.setMaxVisibleItems(20)

        self.gridLayout_3.addWidget(self.comboBox_filterGroups, 0, 3, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_3, 1, 0, 1, 5)

        self.lineEdit_dataset_dir = QLineEdit(self.widget)
        self.lineEdit_dataset_dir.setObjectName(u"lineEdit_dataset_dir")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEdit_dataset_dir.sizePolicy().hasHeightForWidth())
        self.lineEdit_dataset_dir.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.lineEdit_dataset_dir, 0, 0, 1, 1)

        self.pushButton_load_dataset = QPushButton(self.widget)
        self.pushButton_load_dataset.setObjectName(u"pushButton_load_dataset")

        self.gridLayout.addWidget(self.pushButton_load_dataset, 0, 1, 1, 1)

        self.pushButton_reload_resources = QPushButton(self.widget)
        self.pushButton_reload_resources.setObjectName(u"pushButton_reload_resources")

        self.gridLayout.addWidget(self.pushButton_reload_resources, 0, 3, 1, 1)


        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)


        self.retranslateUi(Form)

        self.comboBox_filter_method.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_dataset_cleaning.setText(QCoreApplication.translate("Form", u"Before:", None))
#if QT_CONFIG(tooltip)
        self.pushButton_filter_with_conditional.setToolTip(QCoreApplication.translate("Form", u"This runs the cleanup if the second tag column is also shown, so speed depends on the dataset size", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.pushButton_filter_with_conditional.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.pushButton_filter_with_conditional.setText(QCoreApplication.translate("Form", u"Filter using Conditional", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_filter_phrase.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>separate multiple tags with commas</p><p>This will filter and narow your view of the database using the conditional.</p><p>Click filter to reprocess the Before and After list</p><p>This will filter the view to imgs with matching conditional</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.lineEdit_filter_phrase.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.lineEdit_filter_phrase.setPlaceholderText(QCoreApplication.translate("Form", u"Conditional phrase/tags (exact match)", None))
        self.label_2_dataset_cleaning.setText(QCoreApplication.translate("Form", u"After:", None))
#if QT_CONFIG(tooltip)
        self.listView_dataset_cleaning.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.slider_activation_thresh.setToolTip(QCoreApplication.translate("Form", u"Tag count threshold for activating the aggressive filter", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.checkBox_filter_special.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Filter or add some tags based on multi conditional criterions. </p><p>The conditions are somewhat biased for my (wasabi's) use case. </p><p>Some example of things that are filtered:</p><p>- cleaning up ganguro tags and common mistagged tags</p><p>- merging clothing tags when tag count is above threshold (ex: black bra+black panties -&gt; black underwear)</p><p>- Series specific outfits and objects, ex: (arknights), (idol master), ...</p><p>- Cosplat tags: (cosplay)</p><p>- adding &quot;3d&quot; to images tagged with &quot;realistic&quot;</p><p><br/></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_filter_special.setText(QCoreApplication.translate("Form", u"Filter Specific Criterions:", None))
#if QT_CONFIG(tooltip)
        self.slider_activation_label.setToolTip(QCoreApplication.translate("Form", u"count threshold for tags to filter", None))
#endif // QT_CONFIG(tooltip)
        self.slider_activation_label.setText(QCoreApplication.translate("Form", u"100", None))
#if QT_CONFIG(tooltip)
        self.slider_prob_thresh.setToolTip(QCoreApplication.translate("Form", u"Remove tags under this threshold in the aggresive filter,currently disabled and only uses the count threshold", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.slider_prob_label.setToolTip(QCoreApplication.translate("Form", u"percent threshold for tag filter to keep for the autotagger", None))
#endif // QT_CONFIG(tooltip)
        self.slider_prob_label.setText(QCoreApplication.translate("Form", u"60%", None))
#if QT_CONFIG(tooltip)
        self.checkBox_solo_check.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Only applies to &quot;solo&quot; subject images without multicolor shenanigans.</p><p>Case 1.) Check the threshold value and remove tags with overlaps</p><p>Case 2.) Similar to Case1, but don't use threshold and prioritize rarer tags</p><p>Example 1: black hair [Thr: 0.9], brown hair [Thr: 0.8] --&gt; black hair<br/>Example 2: green eyes [Thr: 0.8], light green eyes [Thr: 0.7] --&gt; light green eyes</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_solo_check.setText(QCoreApplication.translate("Form", u"Additional tag check for solo imgs", None))
        self.pushButton_cleanup_tags.setText(QCoreApplication.translate("Form", u"Cleanup tags", None))
        self.pushButton_apply_change.setText(QCoreApplication.translate("Form", u"Apply Changes and Save to Database", None))
        self.label_3_dataset_cleaning.setText(QCoreApplication.translate("Form", u"Clean up Tags:", None))
#if QT_CONFIG(tooltip)
        self.checkBox_use_tag_csv.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Planned to be decomissioned, removing once enough tags from tag csv is transfered to main tag csv.<br/><br/>Use default logic to filter different types of bows, ribbons, and ties based on priority</p><p>Recommend disabling when the bow/ribbon is an important tag.</p><p>Priority: hair bow = necktie &gt; bow &gt; ribbon, other logic in place for hat bows and many others</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_use_tag_csv.setText(QCoreApplication.translate("Form", u"Prune tags with child tags (tag.csv)", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Search tags:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_search_tags.setToolTip(QCoreApplication.translate("Form", u"enter text to search in the database, result is sorted by frequency", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_search_tags.setPlaceholderText(QCoreApplication.translate("Form", u"Enter tag or string to search", None))
#if QT_CONFIG(tooltip)
        self.checkBox_filter_bow.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Replace emotions, Ex: ;) -&gt; winking</p><p>Conversion pair in resources\\emotions.csv</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_filter_bow.setText(QCoreApplication.translate("Form", u"Filter Bows/Bowties", None))
        self.checkBox_symbolic_tag.setText(QCoreApplication.translate("Form", u"Replace Symbolic Emotions", None))
        self.comboBox_filter_method.setItemText(0, QCoreApplication.translate("Form", u"Frequency (Desc, High-low)", None))
        self.comboBox_filter_method.setItemText(1, QCoreApplication.translate("Form", u"Frequency (Asc, Low-High)", None))
        self.comboBox_filter_method.setItemText(2, QCoreApplication.translate("Form", u"Alphabetical (Desc, A-Z)", None))
        self.comboBox_filter_method.setItemText(3, QCoreApplication.translate("Form", u"Alphabetical (Asc, Z-A)", None))
        self.comboBox_filter_method.setItemText(4, QCoreApplication.translate("Form", u"Tag Groups (Alphabetical)*", u"*some tags in multiple groups"))
        self.comboBox_filter_method.setItemText(5, QCoreApplication.translate("Form", u"Token Length (Desc, High-Low)", None))

#if QT_CONFIG(tooltip)
        self.comboBox_filter_method.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Order of Tags</p><p>* Tag Grouping - some tags may appear in multiple categories</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.comboBox_filter_method.setCurrentText(QCoreApplication.translate("Form", u"Frequency (Desc, High-low)", None))
        self.comboBox_filterGroups.setItemText(0, QCoreApplication.translate("Form", u"Main View", None))

#if QT_CONFIG(tooltip)
        self.comboBox_filterGroups.setToolTip(QCoreApplication.translate("Form", u"Dropdown options will show up if groups are present in the database, select \"main view\" to view all tags in the database or select any group names in the database to filter the imgs used in the count", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.lineEdit_dataset_dir.setToolTip(QCoreApplication.translate("Form", u"enter directory with the database (.json) file", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_dataset_dir.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Database Directory", None))
#if QT_CONFIG(tooltip)
        self.pushButton_load_dataset.setToolTip(QCoreApplication.translate("Form", u"loads database in the text field", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_load_dataset.setText(QCoreApplication.translate("Form", u"Load Database", None))
#if QT_CONFIG(tooltip)
        self.pushButton_reload_resources.setToolTip(QCoreApplication.translate("Form", u"Reload data store in .csv in the resources folder", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_reload_resources.setText(QCoreApplication.translate("Form", u"Reload Filter Resources", None))
    # retranslateUi

