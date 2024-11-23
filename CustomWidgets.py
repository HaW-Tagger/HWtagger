import functools
import time

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCompleter, QDialog, QMessageBox, QLabel, QCheckBox, QHBoxLayout, \
    QLineEdit, QPushButton, QGridLayout, QFileDialog, QStyle

from classes.class_database import Database
from interfaces import global_database_item, outputBase
from resources import parameters
from tools import files


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

def path_input_dialog(parent):
    if parameters.PARAMETERS["default_path"]:
        file_dialog = QFileDialog(parent, directory=parameters.PARAMETERS["default_path"])
    else:
        file_dialog = QFileDialog(parent)
    file_dialog.setFileMode(QFileDialog.FileMode.Directory)
    folder = file_dialog.getExistingDirectory()
    return folder

def file_input_dialog(parent, accepted_extensions=None) -> str:
    if parameters.PARAMETERS["default_path"]:
        file_dialog = QFileDialog(parent, directory=parameters.PARAMETERS["default_path"])
    else:
        file_dialog = QFileDialog(parent)
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    if accepted_extensions:
        file_dialog.setNameFilters(accepted_extensions)
    if file_dialog.exec():
        filename = file_dialog.selectedFiles()[0]
        return filename
    else:
        return ""
class OutputWidget(QWidget, outputBase.Ui_Form):
    createTxtFiles = Signal()
    createJsonTagFile = Signal()
    createSampleToml = Signal()
    createJsonLFile = Signal()

    editedMainTriggerTag = Signal(str)
    editedSecondaryTriggerTag = Signal(str)

    def __init__(self, parent=None, *, primary_tags: str="", secondary_tags: str=""):
        super().__init__()
        self.setupUi(self)

        # Setup text
        self.lineEdit_main_trigger_tag.setText(primary_tags)
        self.plainTextEdit_secondary_trigger_tags.setPlainText(secondary_tags)

        # Create TXT file
        self.pushButton_txt_file.clicked.connect(lambda: self.createTxtFiles.emit())

        # Creates Json Tag File (meta_cap.json)
        self.pushButton_json_tags_file.clicked.connect(lambda: self.createJsonTagFile.emit())

        # Create Sample Toml
        self.pushButton_make_sample_toml.clicked.connect(lambda: self.createSampleToml.emit())
        
        # Create JsonL file
        self.pushButton_create_jsonl.clicked.connect(lambda: self.createJsonLFile.emit())

        # Edited Trigger tags
        self.lineEdit_main_trigger_tag.editingFinished.connect(lambda: self.editedMainTriggerTag.emit(self.lineEdit_main_trigger_tag.text()))
        self.plainTextEdit_secondary_trigger_tags.textChanged.connect(lambda: self.editedSecondaryTriggerTag.emit(self.plainTextEdit_secondary_trigger_tags.toPlainText()))

    def shuffle_tags(self):
        return self.checkBox_shuffle_tags.isChecked()

    def use_trigger_tags(self):
        return self.checkBox_trigger_tags.isChecked()

    def use_token_separator(self):
        return self.checkBox_use_separator.isChecked()

    def use_sentence(self):
        return self.checkBox_use_sentence.isChecked()

    def use_sentence_in_token_separator(self):
        return self.checkBox_sentence_separator.isChecked()

    def remove_tag_in_sentence(self):
        return self.checkBox_remove_tags_in_sentence.isChecked()

    def use_aesthetic_score(self):
        return self.checkBox_export_aesthetic_score.isChecked()

    def use_aesthetic_score_in_token_separator(self):
        return self.checkBox_aesthetic_score_in_token_separator.isChecked()

    def toml_resolution(self):
        return self.comboBox_toml_resolution.currentText()

    def toml_use_restrictive_candidates(self):
        return self.checkBox_restrictive_candidates.currentText()

    def set_trigger_tags(self, primary_tags, secondary_tags):
        self.lineEdit_main_trigger_tag.setText(primary_tags)
        self.plainTextEdit_secondary_trigger_tags.setPlainText(secondary_tags)

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

class ImageWindow(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Image Window")

        # Load the image
        self.image = QPixmap(image_path)

        # Create a label to display the image
        self.label = QLabel()
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(False)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Set the initial size of the window
        self.setGeometry(100, 100, 300, 200)
        self.setMinimumSize(100,100)

    def resizeEvent(self, event):
        # Resize the image to fit the window
        self.label.setPixmap(self.image.scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

    def update_image(self, image_path):
        self.image = QPixmap(image_path)
        self.label.setPixmap(self.image.scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))

class ImageLabel(QLabel):
    rectangleCreated = Signal(tuple)  # top left, bottom right
    leftClickedWithoutRectangle = Signal()

    class SimpleRectangle(QWidget):
        def __init__(self, rect: QtCore.QRect, color: QtGui.QColor, name):
            super().__init__()
            self.rect = rect
            self.color = color
            self.name = name

        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setPen(QtGui.QPen(self.color, 2))
            painter.drawRect(self.rect)
            painter.drawText(self.rect, self.name)

    def __init__(self, image_path=""):
        super().__init__()
        self.rect = QtCore.QRect()
        self.rect_list: list[tuple[tuple[int, int, int, int], QtGui.QColor, str]] = [] # top, left, width, height, color, name

        self.is_drawing = False
        self.activated_drawing = False

        # Load the image
        if image_path != "":
            self.image = QPixmap(image_path)
            self.current_image_rect = QtCore.QRect()
            self.setScaledContents(False)
            self.setMinimumSize(50,50)
        else:
            self.image = QPixmap(QtCore.QSize(50,50))
            self.image.fill(QtCore.Qt.GlobalColor.white)
            self.current_image_rect = QtCore.QRect()
            self.setScaledContents(False)
            self.setMinimumSize(50,50)

    def update_image(self, image_path):
        self.image = QPixmap(image_path)
        self.current_image_rect = QtCore.QRect()
        self.setScaledContents(False)
        self.setMinimumSize(50, 50)

    def mousePressEvent(self, event):
        if self.activated_drawing and event.button() == QtGui.Qt.MouseButton.LeftButton:
            self.is_drawing = True
            self.rect.setTopLeft(self.mapFromGlobal(event.globalPosition()).toPoint())
            self.rect.setBottomRight(self.mapFromGlobal(event.globalPosition()).toPoint())
            self.update()

    def mouseMoveEvent(self, event):
        if self.activated_drawing and self.is_drawing:
            self.rect.setBottomRight(self.mapFromGlobal(event.globalPosition()).toPoint())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.activated_drawing and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.is_drawing = False
            self.rect = self.rect.normalized()
            self.update()
            if self.rect.left() < self.pixmap().rect().right() and self.rect.top() < self.pixmap().rect().bottom():
                self.rectangleCreated.emit(self.get_absolute_image_rect_pos())
            self.rect = QtCore.QRect()
            self.update()

        elif event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.leftClickedWithoutRectangle.emit()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black, 2))
        self.setPixmap(self.image.scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        painter.drawPixmap(QtCore.QPoint(0, 0), self.pixmap())
        if self.current_image_rect != self.pixmap().rect():
            self.current_image_rect = self.pixmap().rect()
            self.add_all_simple_rectangle_widget()
            self.rect = QtCore.QRect()
        painter.drawRect(self.rect)

    def add_all_simple_rectangle_widget(self):
        i = 0
        while i < self.parent().layout().count():
            if isinstance(self.parent().layout().itemAt(i).widget(), self.SimpleRectangle):
                self.parent().layout().itemAt(i).widget().hide()
                self.parent().layout().itemAt(i).widget().destroy()
                self.parent().layout().removeItem(self.parent().layout().itemAt(i))
            else:
                i+=1
        for rectangle in self.rect_list:
            left, top, width, height = self.get_relative_image_rect_pos(rectangle[0])
            self.parent().layout().addWidget(self.SimpleRectangle(QtCore.QRect(left, top, width, height), rectangle[1], rectangle[2]), 0, 0)

    def get_absolute_image_rect_pos(self):
        relative_pos = (self.rect.topLeft().toTuple(), self.rect.bottomRight().toTuple())
        pixmap_width = self.pixmap().width()
        pixmap_height = self.pixmap().height()
        image_width = self.image.width()
        image_height = self.image.height()

        left = max(round(relative_pos[0][0] * (image_width / pixmap_width)), 0) # left
        top = max(round(relative_pos[0][1] * (image_height / pixmap_height)), 0) # top

        width = min(round(relative_pos[1][0] * (image_width / pixmap_width)) - left, image_width - left) # width
        height = min(round(relative_pos[1][1] * (image_height / pixmap_height)) - top, image_height - top) # height

        return left, top, width, height

    def get_relative_image_rect_pos(self, rectangle):
        pixmap_width = self.pixmap().width()
        pixmap_height = self.pixmap().height()
        image_width = self.image.width()
        image_height = self.image.height()

        left = round(rectangle[0] * (pixmap_width / image_width))
        top = round(rectangle[1] * (pixmap_height / image_height))
        width = round(rectangle[2] * (pixmap_width / image_width))
        height = round(rectangle[3] * (pixmap_height / image_height))

        return left, top, width, height

    def add_rectangle(self, rectangle: tuple[int, int, int, int], color: QtGui.QColor, name: str):
        # left, top, width, height
        self.rect_list.append((rectangle, color, name))
        self.add_all_simple_rectangle_widget()

class PaintingImage(QWidget):
    rectangleCreated = Signal(tuple)  # top, left, width, height
    leftClickedWithoutRectangle = Signal()

    def __init__(self, parent=None, path=""):
        super().__init__(parent=parent)
        self.label = ImageLabel(path)
        self.label.rectangleCreated.connect(self.created_rectangle)
        self.label.leftClickedWithoutRectangle.connect(lambda: self.leftClickedWithoutRectangle.emit())

        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.label, 0, 0)
        self.setLayout(layout)
        self.setMinimumSize(50, 50)
        self.activated_drawing = False


    def mousePressEvent(self, event):
        if self.activated_drawing:
            self.label.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.activated_drawing:
            self.label.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.activated_drawing:
            self.label.mouseReleaseEvent(event)
        elif event.button() == QtGui.Qt.MouseButton.LeftButton:
            self.leftClickedWithoutRectangle.emit()

    def update_image(self, image_path):
        self.label.update_image(image_path)
        self.label.rect_list = []

    def created_rectangle(self, rect_pos):
        self.rectangleCreated.emit(rect_pos)
        self.activated_drawing = False

    def add_rectangle(self, rectangle: tuple[int, int, int, int], color: QtGui.QColor|QtCore.Qt.GlobalColor=QtCore.Qt.GlobalColor.blue, name: str=""):
        self.label.add_rectangle(rectangle, color, name)

    def clear_rectangles(self):
        self.label.rect_list = []


    def edit_rectangle(self):
        self.activated_drawing = True
        self.label.activated_drawing = True

class CustomQCompleter(QCompleter):
    def splitPath(self, path):
        # Split the input text by comma
        parts = path.split(",")
        # Return the last part as the prefix for the completer
        if len(parts[-1].strip()) > 2:
            return [parts[-1].strip()]
        else:
            return ["AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"]

    def pathFromIndex(self, index):
        # Get the selected completion text
        completion_text = self.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        # Get the current text in the line edit
        current_text = self.widget().text()
        # Split the current text by comma
        parts = current_text.split(",")
        # Replace the last part with the selected completion text
        parts[-1] = completion_text.strip()
        # Join the parts back together with commas
        return ", ".join(parts)


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
            for group_name, group_data in database.groups.items():
                self.add_group(group_name, group_data.md5s)


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

class DatabaseTagsLogicWidget(QWidget):
    changedState = Signal(tuple) #index, TagLogic save dict
    deleted = Signal(int) #index
    def __init__(self, conditions, added, index: int, keep_conditions=False, completer: QCompleter=None):
        super().__init__()
        self.index = index # an integer index for creating and storing where the TagsLogic is from
        h_layout = QHBoxLayout()

        self.first_line_edit = QLineEdit()
        h_layout.addWidget(self.first_line_edit)
        self.keep_conditions_check = QCheckBox()
        self.keep_conditions_check.setToolTip("Checked: Keep the conditions \nUnchecked: Remove the conditions")
        h_layout.addWidget(self.keep_conditions_check)

        h_layout.addWidget(QLabel("->"))

        self.second_line_edit = QLineEdit()
        h_layout.addWidget(self.second_line_edit)

        self.delete_button = QPushButton(
            QtGui.QIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)), "")
        h_layout.addWidget(self.delete_button)

        self.setLayout(h_layout)

        if completer:
            self.first_line_edit.setCompleter(completer)
            self.second_line_edit.setCompleter(completer)

        self.keep_conditions_check.setChecked(keep_conditions)
        self.second_line_edit.setText(", ".join(added))
        if conditions:
            first_line_text = []
            for condition in conditions:
                current_condition = []
                for tag_tuple in condition:
                    tag=""
                    if not tag_tuple[1]:
                        tag+="-"
                    if tag_tuple[2]:
                        tag+='"'
                    if len(tag_tuple[0])>1:
                        tag += "*".join(tag_tuple[0])
                    else:
                        tag += tag_tuple[0][0]
                    if tag_tuple[2]:
                        tag+='"'
                    current_condition.append(tag)
                first_line_text.append(", ".join(current_condition))
            self.first_line_edit.setText(parameters.PARAMETERS["separator_for_tags_logics_conditions"].join(first_line_text))

        self.first_line_edit.editingFinished.connect(self._state_changed)
        self.second_line_edit.editingFinished.connect(self._state_changed)
        self.keep_conditions_check.stateChanged.connect(self._state_changed)
        self.delete_button.clicked.connect(self._delete_clicked)

    def _get_conditions(self):
        return [files.loose_tags_search_settings_from_tags_list([tag for tag in tags.split(",")]) for tags in self.first_line_edit.text().split(parameters.PARAMETERS["separator_for_tags_logics_conditions"])]

    def _get_keep_conditions(self):
        return self.keep_conditions_check.isChecked()

    def _get_added(self):
        return [tag.strip() for tag in self.second_line_edit.text().split(',')]

    def _get_tags_logic(self):
        return {"conditions":self._get_conditions(), "added":self._get_added(), "keep_conditions":self._get_keep_conditions()}

    def change_index(self, index):
        self.index = index

    @Slot()
    def _state_changed(self):
        self.changedState.emit((self.index, self._get_tags_logic()))

    @Slot()
    def _delete_clicked(self):
        self.deleted.emit(self.index)

