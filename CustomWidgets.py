import os
from copy import copy
import time
import numpy as np

import PySide6.QtGui as QtGui
from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QCompleter, QTreeWidgetItem, QStyledItemDelegate, \
    QDialog, QDialogButtonBox, QMessageBox, QToolTip, QLabel, QCheckBox, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtGui import QPixmap, QImageReader
import PySide6.QtCore as QtCore
from PySide6.QtCore import Signal, Slot, QStringListModel

from classes.class_database import Database, VirtualDatabase
from classes.class_image import ImageDatabase
from interfaces import popupscaledlabel, global_database_item
from resources import parameters
from resources.tag_categories import CATEGORY_TAG_DICT, COLOR_DICT, COLOR_DICT_ORDER, TAG_DEFINITION, HIGH_TOKEN_COUNT

from tools.files import loose_tags_check

import functools
#from version 2, page 203 - 205 of Fluent Python by Luciano Ramalho

def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        arg_lst = [] #name = func.__name__
        if args:
            arg_lst.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ["%s=%r" % (k,w) for k, w in sorted(kwargs.items())]
            arg_lst.append(", ".join(pairs))
        arg_str = ", ".join(arg_lst)
        parameters.log.info("[%0.8fs] %s(%s) -> %r " % (elapsed, func.__name__, arg_str, result))
        return result
    return clocked

def confirmation_dialog(parent, text="Do you confirm your actions ?"):
    """
    return True when the user select yes, False otherwise
    Args:
        parent: parent widget (send None if you don't have one, only for decoration no real use found yet)

    Returns:

    """
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Warning)
    dialog.setText(text)
    dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    dialog.setDefaultButton(QMessageBox.StandardButton.Yes)
    dialog.setModal(True)
    dialog.exec()
    if dialog.clickedButton().text() == "&Yes":
        return True
    else:
        return False


class InputDialog(QDialog):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

class ScaledLabelPopUp(QWidget, popupscaledlabel.Ui_Form):
    def __init__(self, image_path):
        super().__init__()
        self.setupUi(self)
        self.show_image(image_path)

    def show_image(self, image_path):
        self.label.setPixmap(QPixmap(image_path))

class GlobalDatabaseItem(QWidget, global_database_item.Ui_Form):
    def __init__(self, database: Database):
        super().__init__()
        self.setupUi(self)

        self.label_database_path.setText(database.folder)
        self.label_number_of_images.setText(f"{len(database.images)} images")
        self.checkBox_select_database.stateChanged.connect(self.update_check_values)

        self.group_storage: list[QCheckBox] = []
        if database.groups:
            self.add_group("ungrouped",database.get_ungrouped_images())
            for group_name, values in database.groups.items():
                self.add_group(group_name, values["images"])


    def add_group(self, group_name: str, group_data: list):
        if len(group_data) == 0:
            return
        h_layout = QHBoxLayout()
        group_name_checkbox = QCheckBox(group_name)
        group_name_checkbox.setChecked(True)
        self.group_storage.append(group_name_checkbox)
        group_images_len = QLabel(f"{len(group_data)} images")
        h_layout.addWidget(group_name_checkbox)
        h_layout.addWidget(group_images_len)
        self.verticalLayout_2.addLayout(h_layout)


    @Slot()
    def update_check_values(self):
        if self.checkBox_select_database.isChecked():
            for widget in self.group_storage:
                widget.setCheckable(True)
                widget.setChecked(True)
        else:
            for widget in self.group_storage:
                widget.setCheckable(False)
                widget.setChecked(False)

    def checked_database(self) -> bool:
        return self.checkBox_select_database.isChecked()

    def checked_group_names(self) -> list[str]:
        if not self.group_storage:
            return []
        return [x.text() for x in self.group_storage if x.isChecked()]
