# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'statistics.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QLabel,
    QLineEdit, QListView, QPushButton, QSizePolicy,
    QTabWidget, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(940, 498)
        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        self.widget.setAutoFillBackground(False)
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_load_database = QPushButton(self.widget)
        self.pushButton_load_database.setObjectName(u"pushButton_load_database")

        self.gridLayout.addWidget(self.pushButton_load_database, 0, 1, 1, 2)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QSize(200, 0))

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.tabWidget = QTabWidget(self.widget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setMinimumSize(QSize(400, 0))
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.gridLayout_4 = QGridLayout(self.tab_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_5 = QLabel(self.tab_3)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setMinimumSize(QSize(280, 0))

        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.gridLayout_5 = QGridLayout(self.tab_4)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_token_count = QLabel(self.tab_4)
        self.label_token_count.setObjectName(u"label_token_count")

        self.gridLayout_5.addWidget(self.label_token_count, 1, 0, 1, 1)

        self.listView_tokens = QListView(self.tab_4)
        self.listView_tokens.setObjectName(u"listView_tokens")

        self.gridLayout_5.addWidget(self.listView_tokens, 2, 0, 1, 1)

        self.lineEdit_token_input = QLineEdit(self.tab_4)
        self.lineEdit_token_input.setObjectName(u"lineEdit_token_input")

        self.gridLayout_5.addWidget(self.lineEdit_token_input, 0, 0, 1, 1)

        self.tabWidget.addTab(self.tab_4, "")

        self.gridLayout_3.addWidget(self.tabWidget, 2, 0, 5, 1)

        self.line = QFrame(self.widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line, 1, 0, 1, 10)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.label, 0, 2, 1, 8)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.label_2, 4, 2, 1, 1)

        self.line_3 = QFrame(self.widget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_3, 5, 1, 1, 1)

        self.pushButton_threshold_view = QPushButton(self.widget)
        self.pushButton_threshold_view.setObjectName(u"pushButton_threshold_view")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pushButton_threshold_view.sizePolicy().hasHeightForWidth())
        self.pushButton_threshold_view.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.pushButton_threshold_view, 2, 2, 1, 4)

        self.lineEdit_lower_bound = QLineEdit(self.widget)
        self.lineEdit_lower_bound.setObjectName(u"lineEdit_lower_bound")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.lineEdit_lower_bound.sizePolicy().hasHeightForWidth())
        self.lineEdit_lower_bound.setSizePolicy(sizePolicy4)

        self.gridLayout_3.addWidget(self.lineEdit_lower_bound, 2, 6, 1, 1)

        self.pushButton = QPushButton(self.widget)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy3.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.pushButton, 4, 6, 1, 1)

        self.lineEdit_higher_bound = QLineEdit(self.widget)
        self.lineEdit_higher_bound.setObjectName(u"lineEdit_higher_bound")
        sizePolicy4.setHeightForWidth(self.lineEdit_higher_bound.sizePolicy().hasHeightForWidth())
        self.lineEdit_higher_bound.setSizePolicy(sizePolicy4)

        self.gridLayout_3.addWidget(self.lineEdit_higher_bound, 2, 7, 1, 3)

        self.line_2 = QFrame(self.widget)
        self.line_2.setObjectName(u"line_2")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy5)
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_2, 6, 1, 1, 1)

        self.pushButton_quality = QPushButton(self.widget)
        self.pushButton_quality.setObjectName(u"pushButton_quality")
        sizePolicy3.setHeightForWidth(self.pushButton_quality.sizePolicy().hasHeightForWidth())
        self.pushButton_quality.setSizePolicy(sizePolicy3)

        self.gridLayout_3.addWidget(self.pushButton_quality, 4, 9, 1, 1)

        self.gridLayout_4_graph = QGridLayout()
        self.gridLayout_4_graph.setObjectName(u"gridLayout_4_graph")

        self.gridLayout_3.addLayout(self.gridLayout_4_graph, 6, 2, 1, 8)

        self.line_4 = QFrame(self.widget)
        self.line_4.setObjectName(u"line_4")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.line_4.sizePolicy().hasHeightForWidth())
        self.line_4.setSizePolicy(sizePolicy6)
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_4, 5, 2, 1, 8)

        self.line_5 = QFrame(self.widget)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_5, 3, 2, 1, 8)

        self.line_6 = QFrame(self.widget)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.VLine)
        self.line_6.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_6, 4, 7, 1, 2)

        self.lineEdit = QLineEdit(self.widget)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy4.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy4)

        self.gridLayout_3.addWidget(self.lineEdit, 4, 3, 1, 3)


        self.gridLayout.addLayout(self.gridLayout_3, 1, 0, 1, 3)

        self.lineEdit_folder = QLineEdit(self.widget)
        self.lineEdit_folder.setObjectName(u"lineEdit_folder")

        self.gridLayout.addWidget(self.lineEdit_folder, 0, 0, 1, 1)


        self.gridLayout_2.addWidget(self.widget, 0, 0, 1, 1)


        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(tooltip)
        self.pushButton_load_database.setToolTip(QCoreApplication.translate("Form", u"loads database", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_load_database.setText(QCoreApplication.translate("Form", u"Load Database", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Key Statistics:", None))
#if QT_CONFIG(tooltip)
        self.tabWidget.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.tab_3.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>shows basic tag and conflict distribution statistics when &quot;generate Graph&quot; is pressed.</p><p>&quot;Unique tags post filter&quot; is the number of unique tags in the database after filtering</p><p>&quot;Unique rejected tags&quot; is the number of unique tags in the rejected category</p><p><br/></p><p>&quot;Used Tags&quot; section shows the distribution breakdown of data</p><p><br/></p><p>&quot;Tag Conflict Category&quot; section shows the number of potential conflicts in the database, based on tag_category.csv</p><p><br/></p><p><br/></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Form", u"General Tag Distribution Info", None))
#if QT_CONFIG(tooltip)
        self.tab_4.setToolTip(QCoreApplication.translate("Form", u"Displays token info (openCLIP implimentation)", None))
#endif // QT_CONFIG(tooltip)
        self.label_token_count.setText(QCoreApplication.translate("Form", u"Token Count:", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_token_input.setToolTip(QCoreApplication.translate("Form", u"Enter tag(s) here and return the tokenized results.  Shows the tokenized version of the tag(s) and a list of tags with overlapping tokens will be listed below", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_token_input.setText("")
        self.lineEdit_token_input.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Tags", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Form", u"Tokenizer", None))
        self.label.setText(QCoreApplication.translate("Form", u"Graph and Statistics", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"H/W Entries", None))
#if QT_CONFIG(tooltip)
        self.pushButton_threshold_view.setToolTip(QCoreApplication.translate("Form", u"generate a list of autotags in the database between the threshold in the terminal/console", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_threshold_view.setText(QCoreApplication.translate("Form", u"Threshold View", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_lower_bound.setToolTip(QCoreApplication.translate("Form", u"lower threshold for tag search", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_lower_bound.setText(QCoreApplication.translate("Form", u"0.6", None))
        self.lineEdit_lower_bound.setPlaceholderText(QCoreApplication.translate("Form", u"lower_bound", None))
#if QT_CONFIG(tooltip)
        self.pushButton.setToolTip(QCoreApplication.translate("Form", u"this will generate a frequency heatmap using the tags in the database and displayed below", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton.setText(QCoreApplication.translate("Form", u"Generate Frequency Graph", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_higher_bound.setToolTip(QCoreApplication.translate("Form", u"upper threshold for tag search", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_higher_bound.setText(QCoreApplication.translate("Form", u"0.65", None))
        self.lineEdit_higher_bound.setPlaceholderText(QCoreApplication.translate("Form", u"higher bound", None))
#if QT_CONFIG(tooltip)
        self.pushButton_quality.setToolTip(QCoreApplication.translate("Form", u"this will generate a distribution graph of the aesthetic score, tends to generate a normal distribution (law of large number), but is useful to see skewed results with aesthetic scorer (ex: male focus img tends to be ranked lower than female focus)", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_quality.setText(QCoreApplication.translate("Form", u"Show Quality Distribution", None))
#if QT_CONFIG(tooltip)
        self.lineEdit.setToolTip(QCoreApplication.translate("Form", u"height and width size for generating a frequency heatmap of top tags in the database", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit.setText(QCoreApplication.translate("Form", u"100", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"# of top tags to consider for graphing, -1 for all tags", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_folder.setToolTip(QCoreApplication.translate("Form", u"enter directory with database file", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_folder.setPlaceholderText(QCoreApplication.translate("Form", u"Enter Database Directory", None))
    # retranslateUi

