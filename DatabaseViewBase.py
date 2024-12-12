import copy
import datetime
import enum
import os
import subprocess
import webbrowser

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
from PySide6.QtCore import Slot, QStringListModel, QSize, Signal
from PySide6.QtGui import QPixmap, QStandardItem, QBrush
from PySide6.QtWidgets import QWidget, QCompleter, QSizePolicy, QSplitter, QHBoxLayout, QLabel, QVBoxLayout, QDialog, \
    QPushButton, QLineEdit, QStackedWidget, QButtonGroup, QRadioButton, QScrollArea, \
    QColorDialog, QApplication, QStyle

import CustomWidgets
from CustomWidgets import confirmation_dialog, InputDialog
from classes.class_database import Database
from classes.class_image import *
from interfaces import databaseToolsBase, imageViewBase, tagsViewBase, rectangleTagsBase
from resources import parameters, tag_categories
from tools import files

wordlist = QStringListModel()
tags_wordlist = set([tag for tag, freq in tag_categories.DESCRIPTION_TAGS_FREQUENCY.items() if int(freq) > 50] + list(
    tag_categories.COLOR_DICT.keys()))
wordlist.setStringList(tags_wordlist)
completer = CustomWidgets.CustomQCompleter(wordlist)
completer.setModelSorting(QCompleter.ModelSorting.CaseSensitivelySortedModel)
completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
completer.setMaxVisibleItems(5)


class UniqueTagsView(QtCore.QAbstractListModel):
    def __init__(self, display_tags: TagsList, image: ImageDatabase, uncommon_tags: dict):
        super().__init__()
        self.display_tags = TagsList(tags=display_tags)
        self.display_tags.priority_sort()
        self.image = image # Only used for the tooltips
        self.uncommon_tags = uncommon_tags # Uncommon tags are tags that are present in some of the grouped images but not all of them
        self.uncommon_tags_list = list(uncommon_tags.keys()) # Uncommon tags are tags that are present in some of the grouped images but not all of them
        if self.uncommon_tags_list:
            self.uncommon_tags_list.sort(key=lambda x: uncommon_tags[x], reverse=True)

    def rowCount(self, parent=None):
        return len(self.display_tags)+len(self.uncommon_tags_list)

    def data(self, index, role):
        if index.row() >= len(self.display_tags):
            tag = self.uncommon_tags_list[index.row()-len(self.display_tags)]

            if role == QtGui.Qt.ItemDataRole.DisplayRole:
                return tag.tag

            if role == QtGui.Qt.ItemDataRole.FontRole:
                font = QtGui.QFont()

                font.setItalic(True)
                font.setPointSize(parameters.PARAMETERS["font_size"] - 2)
                return font

            if role == QtGui.Qt.ItemDataRole.ToolTipRole:
                return self.image.uncommon_tags_tooltip(tag)
        else:
            tag = self.display_tags[index.row()]

            if role == QtGui.Qt.ItemDataRole.DisplayRole:
                return tag.tag

            if role == QtGui.Qt.ItemDataRole.FontRole:
                font = QtGui.QFont()
                if tag.manual:
                    font.setBold(True)
                if tag.rejected:
                    font.setStrikeOut(True)
                return font

            if role == QtGui.Qt.ItemDataRole.ForegroundRole:
                red, green, blue, alpha = tag.color
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
                return brush

            if role == QtGui.Qt.ItemDataRole.BackgroundRole and tag.highlight:
                brush = QtGui.QBrush(QtGui.QColor.fromRgb(199,255,255, 80)) # color: Azure (darker shade)
                brush.setStyle(QtCore.Qt.BrushStyle.Dense2Pattern)
                return brush

            if role == QtGui.Qt.ItemDataRole.ToolTipRole:
                return self.image.tooltip(tag)

class ConflictTagsView(QtCore.QAbstractItemModel):
    def __init__(self, conflicts, image: ImageDatabase):
        super().__init__()
        self.image = image # never change anything in this object, it's only to gather information on the tags
        self.conflicts = []
        def remove_duplicates(d):
            result = {}
            for key, value in d.items():
                value = tuple(value)
                if value not in result or len(key) > len(result[value]):
                    result[value] = key
            return {v: d[v] for v in result.values()}

        conflicts = remove_duplicates(conflicts)
        for k, v in conflicts.items():
            self.conflicts.append({"name": k, "children": [{"name": tag} for tag in v]})

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            return len(self.conflicts)
        node = parent.internalPointer()
        if "children" in node:
            return len(node["children"])
        return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtGui.Qt.ItemDataRole.DisplayRole:
            return str(node["name"])

        if index.parent().isValid():
            tag = node["name"]
            if role == QtGui.Qt.ItemDataRole.FontRole:
                font = QtGui.QFont()
                if tag.manual:
                    font.setBold(True)
                if tag.rejected:
                    font.setStrikeOut(True)
                return font

            if role == QtGui.Qt.ItemDataRole.ForegroundRole and tag.color:
                red, green, blue, alpha = tag.color
                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
                return brush

            if role == QtGui.Qt.ItemDataRole.BackgroundRole and tag.highlight:
                brush = QtGui.QBrush(QtGui.QColor.fromRgb(199, 255, 255, 80))  # color: Azure (darker shade)
                brush.setStyle(QtCore.Qt.BrushStyle.Dense2Pattern)
                return brush

            if role == QtGui.Qt.ItemDataRole.ToolTipRole:
                return self.image.tooltip(tag)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            return self.createIndex(row, column, self.conflicts[row])
        else:
            parent_node = parent.internalPointer()
            try:
                child_node = parent_node["children"][row]
            except IndexError:
                return QtCore.QModelIndex()
            return self.createIndex(row, column, child_node)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        node = index.internalPointer()
        if node in self.conflicts:
            return QtCore.QModelIndex()

        for i, parent_node in enumerate(self.conflicts):
            if node in parent_node["children"]:
                return self.createIndex(i, 0, parent_node)

        return QtCore.QModelIndex()

class FrequencyTagsView(QtCore.QAbstractListModel):
    def __init__(self, frequency_tags: list[tuple[str, int]]):

        super().__init__()
        self.display_tags = frequency_tags

    def rowCount(self, parent=None):
        return len(self.display_tags)

    def data(self, index, role):
        tag, freq = self.display_tags[index.row()]
        if role == QtGui.Qt.ItemDataRole.DisplayRole:
            return f"{freq}: {tag}"

        if role == QtGui.Qt.ItemDataRole.ForegroundRole and type(tag) == str and tag in tag_categories.COLOR_DICT.keys():
            red, green, blue, alpha = tag_categories.COLOR_DICT[tag]
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
            return brush

class RectangleTagsView(QScrollArea):
    class RectangleItemView(QWidget, rectangleTagsBase.Ui_Form):

        ColorChanged = QtCore.Signal(tuple) # name, hexadecimal color
        EditRectClicked = QtCore.Signal(str)
        DeleteClicked = QtCore.Signal(str)
        def __init__(self, rectangle_item: RectElement):
            super().__init__()
            self.setupUi(self)

            self.rectangle_data: RectElement = rectangle_item
            # Image Label
            self.label_name.setText(self.rectangle_data.name)

            # sentence view
            self.plainTextEdit_sentence.setPlainText(self.rectangle_data.sentence_description.sentence)
            self.plainTextEdit_sentence.textChanged.connect(self.sentence_changed)

            # Full Tags View
            self.rectangle_data.full_tags.init_display_properties()
            self.rectangle_data.filter()
            full_tags_model = UniqueTagsView(self.rectangle_data.get_full_tags(), ImageDatabase(), {})
            self.listView_full_tags.setModel(full_tags_model)
            if parameters.PARAMETERS["double_click"]:
                self.listView_full_tags.doubleClicked.connect(self.remove_tag)
            else:
                self.listView_full_tags.clicked.connect(self.remove_tag)

            # Add Tag
            self.lineEdit_full_tags.returnPressed.connect(self.add_tags)
            self.lineEdit_full_tags.setCompleter(completer)

            # color button, color stored as hexadecimal value
            if self.rectangle_data.color:
                self.pushButton_pick_color.setStyleSheet("QPushButton { background-color: "+self.rectangle_data.color+" }"+self.pushButton_pick_color.styleSheet())
            self.pushButton_pick_color.clicked.connect(self.pick_new_color)

            # edit rect button
            self.pushButton_edit_rect.clicked.connect(lambda: self.EditRectClicked.emit(self.rectangle_data.name))

            # delete button
            self.pushButton_delete.clicked.connect(lambda: self.DeleteClicked.emit(self.rectangle_data.name))

        @Slot()
        def pick_new_color(self):
            dlg = QColorDialog(self)
            if self.rectangle_data.color:
                dlg.setCurrentColor(QtGui.QColor(self.rectangle_data.color))

            if dlg.exec() and dlg.result() == dlg.DialogCode.Accepted:
                parameters.log.info("Accepted Color Pick")
                self.rectangle_data.color = dlg.currentColor().name()
                blank_button = QPushButton()
                self.pushButton_pick_color.setStyleSheet("QPushButton { background-color: " + self.rectangle_data.color + " }"+blank_button.styleSheet())
                self.ColorChanged.emit((self.rectangle_data.name, self.rectangle_data.color))

        @Slot()
        def sentence_changed(self):
            new_text = self.plainTextEdit_sentence.toPlainText().strip()
            self.rectangle_data.sentence_description.sentence = new_text

        @Slot()
        def add_tags(self):
            new_tags = [tag.strip() for tag in self.lineEdit_full_tags.text().split(',') if tag.strip()]
            if new_tags:
                self.rectangle_data.add_new_tags(new_tags)
                self.reload_tags_view()
            self.lineEdit_full_tags.clear()
        @Slot()
        def remove_tag(self, index):
            if not index.isValid():
                return False
            remove_tag = index.data(role=QtCore.Qt.ItemDataRole.DisplayRole).strip()
            if remove_tag:
                self.rectangle_data.remove_tags(remove_tag)
                self.reload_tags_view()

        def reload_tags_view(self):
            self.rectangle_data.full_tags.init_display_properties()
            self.rectangle_data.filter()
            full_tags_model = UniqueTagsView(self.rectangle_data.get_full_tags(), ImageDatabase(), {})
            self.listView_full_tags.setModel(full_tags_model)



    editRectangleRequested = QtCore.Signal(str) # rectangle_name
    editColorRequested = QtCore.Signal(tuple) # rectangle_name, color_hex
    createRectangleRequested =  QtCore.Signal()
    deleteRectangleRequested = QtCore.Signal(str) # rectangle_name

    def __init__(self, rectangles: list[RectElement]=None):
        super().__init__()
        if rectangles is None:
            rectangles = []
        base_layout = QVBoxLayout()
        self.setLayout(base_layout)
        new_rectangle_button = QPushButton("+")
        new_rectangle_button.clicked.connect(self.create_new_rectangle)
        self.layout().addWidget(new_rectangle_button)

        # Hosts the widgets present in the layout
        self.rectangles_views: list = []

        self.image_rectangles = rectangles

        if rectangles:
            for rectangle in rectangles:
                self.add_rectangle(rectangle)

    def init_new_rectangles(self, rectangles: list[RectElement]):

        for rectangle_widget in self.rectangles_views:
            self.layout().removeWidget(rectangle_widget)
            rectangle_widget.hide()
            rectangle_widget.destroy()

        self.rectangles_views = []

        if rectangles:
            for rectangle in rectangles:
                self.add_rectangle(rectangle)



    def add_rectangle(self, rectangle: RectElement):
        new_rectangle_view = self.RectangleItemView(rectangle)
        new_rectangle_view.ColorChanged.connect(self.color_changed)
        new_rectangle_view.EditRectClicked.connect(self.edit_rect_requested)
        new_rectangle_view.DeleteClicked.connect(self.delete_requested)
        self.rectangles_views.append(new_rectangle_view)
        self.layout().insertWidget(0, new_rectangle_view)

    def create_new_rectangle(self):
        """
        Create an entirely new custom rectangle
        """
        self.createRectangleRequested.emit()

    def delete_rectangle(self, rectangle_name: str):
        r_o = False
        for i in range(len(self.rectangles_views)):
            if self.rectangles_views[i].rectangle_data.name == rectangle_name:
                r_o = self.rectangles_views.pop(i)
                break
        if not r_o:
            parameters.log.warning(f"Weird Behaviour, rectangle doesn't exist for name: {rectangle_name}")
            return

        self.layout().removeWidget(r_o)
        r_o.hide()
        r_o.destroy()

        self.deleteRectangleRequested.emit(rectangle_name)


    def get_rectangles_info(self):
        """
        Returns:
            all info in form of a list of dicts associated with the rectangles
        """
        parameters.log.warning("Not Implemented")

    @Slot()
    def color_changed(self, rectangle_info: tuple[str, str]):
        """

        Args:
            rectangle_info: (name, color as hexadecimal)
        """
        self.editColorRequested.emit(rectangle_info)

    @Slot()
    def edit_rect_requested(self, rectangle_name: str):
        self.editRectangleRequested.emit(rectangle_name)

    @Slot()
    def delete_requested(self, rectangle_name: str):
        self.delete_rectangle(rectangle_name)

class SortType(enum.Enum):
    # add sort name and the sort function here to add sort method to ui

    # Name, function, Tooltip description, Tooltip attribute
    TAGS_LEN = "Tags length", lambda x: len(x.full_tags), "Tags Length", ""
    TOKEN_LEN = "Token length", lambda x: x.get_token_length(), "Other", ""
    SENTENCE_TOKEN_LEN = "Sentence token length", lambda x: x.get_sentence_token_length(), "Other", ""
    SENTENCE_LEN = "Sentence length", lambda x: x.get_sentence_length(), "Other", ""
    MANUAL_TAGS_LEN = "Manual tags length", lambda x: len(x.manual_tags), "Other", ""
    FILE_NAME = "Filename", lambda x: x.get_filename(), "Other", ""
    CONFLICTS_LEN = "Conflicts length", lambda x: len(x.filtered_review.keys()), "Other", ""
    SCORE_RATING = "Aesthetic score", lambda x: x.get_score_sort_tuple(), "Other", "" # double sort (label, score)
    IMAGE_RATIO = "Image ratio", lambda x: x.image_ratio, "Other", ""
    IMAGE_PIXEL_COUNT = "Image pixel count", lambda x: x.image_width*x.image_height, "Other", ""
    IMAGE_WIDTH = "Image width", lambda x: (x.image_width, x.image_height), "Other", ""
    IMAGE_HEIGHT = "Image height", lambda x: (x.image_height, x.image_width), "Other", ""
    SIMILARITY_GROUP = "Similarity", lambda x: x.similarity_group, "Other", "similarity_probability"
    BRIGHTNESS_VALUE = "Brightness", lambda x: x.get_brightness(), "Other", "brightness_value"
    AVERAGE_PIXEL = "Average pixel", lambda x: x.get_average_pixel(), "Other", "average_pixel"
    CONTRAST_COMPOSITION = "Contrast", lambda x: x.get_contrast_composition(), "Other", "contrast_comp"
    UNDERLIGHTING_COMPOSITION = "Underlighting", lambda x: x.get_underlighting(), "Other", "underlighting"
    GRADIENT_COMPOSITION = "Gradient", lambda x: x.get_gradient(), "Other", "gradient", ""
    RECTANGLES_COUNT = "Rectangles Count", lambda x: len(x.rects), "Other"

 
    CHARACTER_COUNT = "Named characters count", lambda x: x.get_character_count(), "Other", ""
    RARE_TAGS_COUNT = "Rare tags count", lambda x: x.get_rare_tags_count(), "Other", ""
    UNKNOWN_TAGS = "Unknown tags", lambda x: x.get_unknown_tags_count(), "Other", ""

    def sort_function(self, image):
        return self.value[1](image)

    def get_attribute(self):
        return self.value[3]

def get_sort_member(text):
    for member in SortType:
        if member.value[0] == text:
            return member
    return SortType.TAGS_LEN

class BaseImageView(QtGui.QStandardItemModel):
    def __init__(self, images_dict):
        super().__init__()
        self.images_dict = images_dict
        self.row_count = len(self.images_dict.keys())
        for x in self.images_dict.keys():
            item = self.create_item(x)
            self.appendRow(item)
        self.selected_images: list[int] = [] # The index of the image from the database
        gradient = QtGui.QRadialGradient(0, 20, 100)
        gradient.setColorAt(0, QtCore.Qt.GlobalColor.red)
        gradient.setColorAt(0.2, QtCore.Qt.GlobalColor.yellow)
        gradient.setColorAt(0.4, QtCore.Qt.GlobalColor.green)
        gradient.setColorAt(0.6, QtCore.Qt.GlobalColor.cyan)
        gradient.setColorAt(0.8, QtCore.Qt.GlobalColor.blue)
        gradient.setColorAt(1.0, QtCore.Qt.GlobalColor.magenta)
        self.gradient_brush = QBrush(gradient)
        self.blank_brush = QBrush(QtGui.QColor(214, 214, 214, 255))

    def rowCount(self, parent=None):
        return self.row_count

    def apply_order(self, list_sort, attribute=""):
        self.beginResetModel()
        self.clear()
        self.row_count = len(list_sort)
        for x in list_sort:
            item = self.create_item(x[0], attribute)
            self.appendRow(item)
        self.endResetModel()


    def create_item(self, image_index, attribute=""):
        item = QStandardItem(str(image_index))
        item.setIcon(self.images_dict[image_index][0])
        if parameters.PARAMETERS["database_view_tooltip"]:
            if os.path.exists(self.images_dict[image_index][1].path):
                date_modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.images_dict[image_index][1].path))
                date_created = datetime.datetime.fromtimestamp(os.path.getctime(self.images_dict[image_index][1].path))
            else:
                date_modified = "DISCARDED"
                date_created = "DISCARDED"
            if attribute and hasattr(self.images_dict[image_index][1], attribute):
                tooltip = f'<b>{getattr(self.images_dict[image_index][1], attribute)}</b>\npath: {self.images_dict[image_index][1].path}, width: {self.images_dict[image_index][1].image_width}, height: {self.images_dict[image_index][1].image_height}, date modified: {date_modified}, date created: {date_created}<br><img src="{self.images_dict[image_index][1].path}" width={768 * self.images_dict[image_index][1].image_ratio} height={768}>'
            else:
                tooltip = f'<b>path: {self.images_dict[image_index][1].path}, width: {self.images_dict[image_index][1].image_width}, height: {self.images_dict[image_index][1].image_height}, date modified: {date_modified}, date created: {date_created}, </b><br><img src="{self.images_dict[image_index][1].path}" width={768 * self.images_dict[image_index][1].image_ratio} height={768}>'
            item.setToolTip(tooltip)
        return item

    def data(self, index, role):
        if role == QtGui.Qt.ItemDataRole.DecorationRole:
            return self.item(index.row()).data(QtGui.Qt.ItemDataRole.DecorationRole)
        if role == QtGui.Qt.ItemDataRole.ToolTipRole:
            return self.item(index.row()).data(QtGui.Qt.ItemDataRole.ToolTipRole)
        if role == QtGui.Qt.ItemDataRole.BackgroundRole:
            if self.db_index(index) in self.selected_images:
                return self.gradient_brush
            else:
                return self.blank_brush

    def db_index(self, index) -> int:
        return int(self.itemData(index)[0])

    def update_selected_images(self, selected_indexes: list[QtCore.QModelIndex]):
        self.selected_images = [self.db_index(i) for i in selected_indexes]

class DatabaseToolsBase(QWidget, databaseToolsBase.Ui_Form):
    clickedBatchFunction = Signal(tuple)
    clickedPopupWindow = Signal()
    clickedFavourites = Signal(TagElement)
    changedDatabaseSettings = Signal()
    frequencyTagSelected = Signal(str)
    removeTagsFrequencySelected = Signal(tuple)
    clickedSaveDatabase = Signal()

    def __init__(self, db: Database):
        super().__init__()
        self.setupUi(self)
        self.db = db
        # Output
        self.widget_to_output.set_trigger_tags(", ".join(self.db.trigger_tags["main_tags"]), ", ".join(self.db.trigger_tags["secondary_tags"]))
        self.widget_to_output.createTxtFiles.connect(self.create_txt_files_button)
        self.widget_to_output.createJsonTagFile.connect(self.create_meta_cap_button)
        self.widget_to_output.createSampleToml.connect(self.create_sample_toml_button)
        self.widget_to_output.createJsonLFile.connect(self.create_jsonl_button)

        self.widget_to_output.editedMainTriggerTag.connect(self.update_main_trigger_tags)
        self.widget_to_output.editedSecondaryTriggerTag.connect(self.update_secondary_trigger_tags)

        # Save
        self.pushButton_save_database.clicked.connect(lambda: self.clickedSaveDatabase.emit())

        # Batches
        self.pushButton_apply_filtering.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.apply_filter, self.comboBox_selection.currentText())))
        self.pushButton_apply_replacement_to_sentence.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.apply_sentence_filter, self.comboBox_selection.currentText())))

        self.pushButton_auto_tag.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.auto_tag, self.comboBox_selection.currentText())))
        self.pushButton_only_tag_characters.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.auto_tag_characters, self.comboBox_selection.currentText())))
        self.pushButton_auto_score.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.auto_score, self.comboBox_selection.currentText())))
        self.pushButton_auto_classify.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.auto_classify, self.comboBox_selection.currentText())))

        self.pushButton_cleanup_rejected_manual_tags.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.cleanup_rejected_manual, self.comboBox_selection.currentText())))
        self.pushButton_refresh_tags_from_gelbooru_and_rule34.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.refresh_unsafe_tags, self.comboBox_selection.currentText())))
        self.pushButton_reset_manual_score.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.reset_manual_score, self.comboBox_selection.currentText())))
        self.pushButton_purge_manual.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.purge_manual, self.comboBox_selection.currentText())))
        self.pushButton_remove_specific_source.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.remove_specific_source, self.comboBox_selection.currentText())))
        self.pushButton_resolve_manual_tags.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.resolve_manual_tags, self.comboBox_selection.currentText())))

        # Other Batches
        self.pushButton_export_images.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.export_images, self.comboBox_selection.currentText())))
        self.pushButton_discard_image.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.discard_images, self.comboBox_selection.currentText())))
        self.pushButton_open_in_default_program.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.open_default_program, self.comboBox_selection.currentText())))

        self.pushButton_flip_horizontally.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.flip_horizontally, self.comboBox_selection.currentText())))
  
        self.comboBox_selection.addItems(["Current Selection", "Visible Images", "Database"])
        self.comboBox_selection.setCurrentIndex(0)

        # Popup Window
        self.pushButton_popup_image.clicked.connect(lambda: self.clickedPopupWindow.emit())

        # Favourites
        self.init_favourites()
        self.treeView_favourites.clicked.connect(self.clicked_favourites)
        self.lineEdit_edit_favourites.returnPressed.connect(self.edit_favourites)

        # Tags Logic
        self.replace_lines: list[CustomWidgets.DatabaseTagsLogicWidget] = []
        base_replace_layout = QVBoxLayout()
        add_replace_line_button = QPushButton("Add Tags Logic")
        add_replace_line_button.clicked.connect(self.create_replace_line)
        base_replace_layout.addWidget(add_replace_line_button)
        self.scrollAreaWidgetContents.setLayout(base_replace_layout)
        self.comboBox_group_name_settings.currentTextChanged.connect(self.init_tags_logic)
        self.comboBox_group_name_settings.addItem("All")
        self.comboBox_group_name_settings.addItems([group.group_name for group in self.db.groups.values()])
        self.pushButton_export_settings.clicked.connect(self.export_settings)
        self.pushButton_import_settings.clicked.connect(self.import_settings)


        # Tags Frequency
        self.pushButton_refresh_tags_frequency.clicked.connect(self.refresh_tags_frequency)
        for category in ["ALL"] + list(tag_categories.TAG_CATEGORIES.keys()):
            self.comboBox_frequency_sort.addItem(category)
        self.comboBox_frequency_sort.currentTextChanged.connect(self.refresh_tags_frequency)
        self.lineEdit_tag_frequency_search.returnPressed.connect(self.refresh_tags_frequency)
        self.listView_tags_frequency.doubleClicked.connect(self.tag_from_tags_frequency_selected)
        self.pushButton_remove_tags_from_frequency_batch.clicked.connect(self.remove_tags_from_frequency)

        self.comboBox_batch_selection_frequency.addItems(["Current Selection", "Visible Images", "Database"])
        self.comboBox_batch_selection_frequency.setCurrentIndex(0)


    @Slot()
    def refresh_tags_frequency(self):
        frequency = self.db.get_frequency_of_all_tags()
        category = self.comboBox_frequency_sort.currentText()
        search_string = self.lineEdit_tag_frequency_search.text().strip().lower()
  
        if category != "ALL": # filter by category
            frequency = [tag_tuple for tag_tuple in frequency if category in tag_categories.TAG2CATEGORY.get(tag_tuple[0], [])]
        if search_string: # filter by string
            frequency = [tag_tuple for tag_tuple in frequency if search_string in tag_tuple[0]]
  
        refresh_model = FrequencyTagsView(frequency)
        self.listView_tags_frequency.setModel(refresh_model)

    @Slot()
    def tag_from_tags_frequency_selected(self, index):
        if not index.isValid():
            return False
        tag = self.listView_tags_frequency.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
        self.frequencyTagSelected.emit(tag)

    @Slot()
    def remove_tags_from_frequency(self):
        tags_to_remove = [self.listView_tags_frequency.model().data(
            self.listView_tags_frequency.model().index(model_index),
            QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
            for model_index in range(self.listView_tags_frequency.model().rowCount())]
        if not tags_to_remove:
            parameters.log.info("No tags were selected")
            return False
        self.removeTagsFrequencySelected.emit((tags_to_remove, self.comboBox_batch_selection_frequency.currentText()))

    def init_tags_logic(self):
        while len(self.replace_lines)>0:
            x = self.replace_lines.pop(-1)
            self.scrollAreaWidgetContents.layout().removeWidget(x)
            x.hide()
            x.destroy()
        group_name = self.comboBox_group_name_settings.currentText()
        if group_name == "All":
            if self.db.settings.tags_logics:
                for tags_logic in self.db.settings.tags_logics:
                    self.create_replace_line(tags_logic=tags_logic)
        else:
            if self.db.groups[group_name].settings.tags_logics:
                for tags_logic in self.db.groups[group_name].settings.tags_logics:
                    self.create_replace_line(tags_logic=tags_logic)


    @Slot()
    def create_replace_line(self,*, tags_logic: TagsLogic=None):
        group_name = self.comboBox_group_name_settings.currentText() if self.comboBox_group_name_settings.currentText() != "All" else None
        if tags_logic:
            one_widget = CustomWidgets.DatabaseTagsLogicWidget(tags_logic.conditions, tags_logic.added, index=len(self.replace_lines), completer=completer, keep_conditions=tags_logic.keep_conditions, group_name=group_name)
        else:
            one_widget = CustomWidgets.DatabaseTagsLogicWidget("", "",index=len(self.replace_lines), completer=completer)
            if not group_name:
                self.db.settings.add_tags_logic([], [], False)
            else:
                self.db.groups[group_name].settings.add_tags_logic([], [], False)
        if not group_name:
            one_widget.changedState.connect(lambda x: self.db.settings.tags_logics[x[0]].load(x[1]))
        else:
            one_widget.changedState.connect(lambda x: self.db.groups[group_name].settings.tags_logics[x[0]].load(x[1]))
        one_widget.changedState.connect(lambda: self.changedDatabaseSettings.emit())
        one_widget.deleted.connect(self.remove_replace_line)
        self.replace_lines.append(one_widget)
        self.scrollAreaWidgetContents.layout().insertWidget(0, one_widget)

    @Slot(tuple)
    def remove_replace_line(self, index_and_group_name: tuple[int, str]):
        x = self.replace_lines.pop(index_and_group_name[0])
        if not index_and_group_name[1]:
            self.db.settings.remove_tags_logic(index_and_group_name[0])
        else:
            self.db.groups[index_and_group_name[1]].settings.remove_tags_logic(index_and_group_name[0])
        self.scrollAreaWidgetContents.layout().removeWidget(x)
        x.hide()
        x.destroy()
        for i in range(index_and_group_name[0], len(self.replace_lines)):
            self.replace_lines[i].change_index(i)
        self.changedDatabaseSettings.emit()

    @Slot()
    def edited_groups(self):
        """
        When a group name has changed, or a new one, or a deleted one
        """
        previous_name = self.comboBox_group_name_settings.currentText()
        self.comboBox_group_name_settings.setCurrentIndex(0)
        while self.comboBox_group_name_settings.count()>1:
            self.comboBox_group_name_settings.removeItem(1)
        self.comboBox_group_name_settings.addItems([group.group_name for group in self.db.groups.values()])
        if previous_name in [group.group_name for group in self.db.groups.values()]:
            new_i = self.comboBox_group_name_settings.findText(previous_name, flags=QtCore.Qt.MatchFlag.MatchExactly)
            self.comboBox_group_name_settings.setCurrentIndex(new_i)

    @Slot()
    def export_settings(self):
        self.db.export_settings()

    @Slot()
    def import_settings(self):
        accepted_file = CustomWidgets.file_input_dialog(self, ["JSON Files (*.json)"])
        if not accepted_file:
            return False
        self.db.settings.load(files.load_settings(accepted_file))
        self.changedDatabaseSettings.emit()
        self.init_tags_logic()

    def init_favourites(self):
        favourites = TagsList(tags=files.get_favourites(), name="Favourites")
        blank_image = ImageDatabase()
        fav_dict = defaultdict(lambda: TagsList())
        used = []
        for fav in favourites:
            if fav in tag_categories.TAG2SUB_CATEGORY_EXCLUSIVE.keys():
                used.append(fav)
                for sub_category in tag_categories.TAG2SUB_CATEGORY_EXCLUSIVE[fav]:
                    fav_dict[sub_category] += fav
        favourites -= used
        if favourites:
            fav_dict["Other"] = TagsList(tags=favourites.tags)
        for fav_list in fav_dict.values():
            fav_list.init_display_properties()
            fav_list.init_manual_display_properties(False)
            fav_list.init_rejected_display_properties(False)
        fav_model = ConflictTagsView(fav_dict, blank_image)
        self.treeView_favourites.setModel(fav_model)
        self.treeView_favourites.expandAll()

    @Slot()
    def edit_favourites(self):
        edit = [tag.strip() for tag in self.lineEdit_edit_favourites.text().split(",")]
        if not edit:
            return False
        favourites = files.get_favourites()
        new_favourites = []
        for fav in favourites:
            if fav not in edit:
                new_favourites.append(fav)
            else:
                edit.remove(fav)
        if edit:
            new_favourites = new_favourites+edit
        files.save_favourites(new_favourites)
        self.init_favourites()
        self.lineEdit_edit_favourites.clear()

    @Slot()
    def clicked_favourites(self, index):
        if not index.isValid():
            return False
        if not index.parent().isValid():
            parameters.log.info("Can't add tag favourites categories to tags")
            return False
        tag = index.internalPointer()["name"]
        self.clickedFavourites.emit(tag)

    @Slot(str)
    def update_main_trigger_tags(self, text: str):
        tags = [tag.strip() for tag in text.split(",")]
        self.db.trigger_tags["main_tags"] = tags

    @Slot(str)
    def update_secondary_trigger_tags(self, text: str):
        tags = [tag.strip() for tag in text.split(",")]
        self.db.trigger_tags["secondary_tags"] = tags

    @Slot()
    def create_txt_files_button(self):
        self.db.create_txt_files(
            use_trigger_tags=self.widget_to_output.use_trigger_tags(),
            token_separator=self.widget_to_output.use_token_separator(),
            use_aesthetic_score=self.widget_to_output.use_aesthetic_score(),
            use_sentence=self.widget_to_output.use_sentence(),
            sentence_in_trigger=self.widget_to_output.use_sentence_in_token_separator(),
            remove_tags_in_sentence=self.widget_to_output.remove_tag_in_sentence(),
            score_trigger=self.widget_to_output.use_aesthetic_score_in_token_separator(),
            shuffle_tags=self.widget_to_output.shuffle_tags()
        )

    @Slot()
    def create_meta_cap_button(self):
        self.db.create_json_file(
            use_trigger_tags=self.widget_to_output.use_trigger_tags(),
            token_separator=self.widget_to_output.use_token_separator(),
            use_aesthetic_score=self.widget_to_output.use_aesthetic_score(),
            use_sentence=self.widget_to_output.use_sentence(),
            sentence_in_trigger=self.widget_to_output.use_sentence_in_token_separator(),
            remove_tags_in_sentence=self.widget_to_output.remove_tag_in_sentence(),
            score_trigger=self.widget_to_output.use_aesthetic_score_in_token_separator(),
            shuffle_tags=self.widget_to_output.shuffle_tags()
        )

    @Slot()
    def create_jsonl_button(self):
        self.db.create_jsonL_file(
            use_trigger_tags=self.widget_to_output.use_trigger_tags(),
            token_separator=self.widget_to_output.use_token_separator(),
            use_aesthetic_score=self.widget_to_output.use_aesthetic_score(),
            use_sentence=self.widget_to_output.use_sentence(),
            sentence_in_trigger=self.widget_to_output.use_sentence_in_token_separator(),
            remove_tags_in_sentence=self.widget_to_output.remove_tag_in_sentence(),
            score_trigger=self.widget_to_output.use_aesthetic_score_in_token_separator(),
            shuffle_tags=self.widget_to_output.shuffle_tags()
        )

    @Slot()
    def create_sample_toml_button(self):
        selected_resolution = self.widget_to_output.toml_resolution()
        resolution_dict = {
            "SDXL": (1024, 1024, 64),
            "SD1.5": (768, 768, 64),
            "SD1.0": (512, 512, 64),
            "Custom": (parameters.PARAMETERS['custom_export_width'],
                       parameters.PARAMETERS['custom_export_height'],
                       parameters.PARAMETERS['custom_export_bucket_steps'])
        }
        if selected_resolution in resolution_dict:
            res_info = resolution_dict[selected_resolution]
        else:
            parameters.log.error("Resolution string not found")
            res_info = resolution_dict["SDXL"]

        self.db.create_sample_toml(res_info[0], res_info[1], res_info[2])


    class BatchFunctions:
        update_image_frames_func_names = ["flip_horizontally"]
        @staticmethod
        def apply_filter(db: Database, image_indexes: list[int]):
            if len(image_indexes) > 0.6*len(db.images):
                db.filter_all()
            else:
                for index in image_indexes:
                    db.images[index].filter()

        @staticmethod
        def apply_sentence_filter(db: Database, image_indexes: list[int]):
            if len(image_indexes) > 0.6*len(db.images):
                db.filter_sentence_all()
            else:
                for index in image_indexes:
                    db.images[index].filter_sentence()

        @staticmethod
        def auto_tag(db: Database, image_indexes: list[int]):
            db.re_call_models(image_indexes, tag_images=True)

        @staticmethod
        def auto_tag_characters(db: Database, image_indexes: list[int]):
            db.call_models([db.images[index].path for index in image_indexes], tag_only_character=True)

        @staticmethod
        def auto_score(db: Database, image_indexes: list[int]):
            db.re_call_models(image_indexes, score_images=True)

        @staticmethod
        def auto_classify(db: Database, image_indexes: list[int]):
            db.call_models([db.images[index].path for index in image_indexes], classify_images=True)

        @staticmethod
        def cleanup_rejected_manual(db: Database, image_indexes: list[int]):
            db.cleanup_images_rejected_tags(image_indexes)

        @staticmethod
        def refresh_unsafe_tags(db: Database, image_indexes: list[int]):
            db.refresh_unsafe_tags(image_indexes)

        @staticmethod
        def reset_manual_score(db: Database, image_indexes: list[int]):
            db.reset_scores(image_indexes)

        @staticmethod
        def purge_manual(db: Database, image_indexes: list[int]):
            db.purge_manual_tags(image_indexes)

        @staticmethod
        def remove_specific_source(db: Database, image_indexes: list[int]):
            available_sources = db.available_sources(image_indexes)
            source_name_dialog = InputDialog()
            source_name_dialog.setWindowTitle("Source name")
            source_name_dialog.setToolTip(
                f"Remove a source from {len(image_indexes)} images.\nAvailable source names are: {', '.join(available_sources)}")
            if source_name_dialog.exec() == QDialog.DialogCode.Accepted:
                source_input = source_name_dialog.input_field.text().strip()
            else:
                parameters.log.warning("No specified source")
                return False
            if source_input not in available_sources:
                parameters.log.warning("Wrong source name")
                return False
            db.remove_source(source_input, image_indexes)

        @staticmethod
        def resolve_manual_tags(db: Database, image_indexes: list[int]):
            if len(image_indexes) > 1:
                if not CustomWidgets.confirmation_dialog(None,
                                                         f"You selected {len(image_indexes)} images to resolve the manual tags.\nThis will remove all added manual tags that are also in the rejected manual tags.\n\nTip: This button is affected by the 'apply to:' setting at the top right of the window."):
                    return False
            db.resolve_manual_tags(image_indexes)

        @staticmethod
        def open_default_program(db: Database, image_indexes: list[int]):
            if len(image_indexes) > 1:
                if not CustomWidgets.confirmation_dialog(None,
                                                         f"You selected {len(image_indexes)} images to open.\nAre you sure you want to open them ?\n\nTip: This button is affected by the 'apply to:' setting at the top right of the window."):
                    return False
            for index in image_indexes:
                image_path = db.images[index].path
                if not os.path.exists(image_path):
                    parameters.log.info(f"Image doesn't exist: {image_path}")
                elif parameters.PARAMETERS["external_image_editor_path"]:
                    subprocess.Popen([parameters.PARAMETERS["external_image_editor_path"], image_path])
                else:
                    os.startfile(image_path)

        @staticmethod
        def flip_horizontally(db: Database, image_indexes: list[int]):
            if len(image_indexes) > 1:
                if not CustomWidgets.confirmation_dialog(None,
                                                         f"You selected {len(image_indexes)} images to be flipped horizontally.\nAre you sure you want to flip them ?\n\nTip: This button is affected by the 'apply to:' setting at the top right of the window."):
                    return False
            error_path = []
            for index in image_indexes:
                image_path = db.images[index].path
                if not os.path.exists(image_path):
                    parameters.log.info(f"Image doesn't exist: {image_path}")
                else:
                    try:
                        image = Image.open(image_path)
                        flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
                        flipped_image.save(image_path)
                    except:
                        error_path.append(image_path)

            if error_path:
                parameters.log.error(f"Failed to flip {len(error_path)} images: {error_path}")
            else:
                parameters.log.info(f"Successfully flipped {len(image_indexes)} images")

            db.update_image_objects(min(parameters.PARAMETERS["image_load_size"], 512), image_indexes)
            return [image_index for image_index in image_indexes if image_index not in error_path]

        @staticmethod
        def discard_images(db: Database, image_indexes: list[int]):
            # todo: add a button to return temp_discarded images
            if len(image_indexes) > 1:
                if not CustomWidgets.confirmation_dialog(None, f"You selected {len(image_indexes)} images to discard.\nAre you sure you want to discard them ?\n\nTip: This button is affected by the 'apply to:' setting at the top right of the window."):
                    return False
            files.export_images(
                [db.images[i].path for i in image_indexes if os.path.exists(db.images[i].path)],
                db.folder, "TEMP_DISCARDED"
            )

        @staticmethod
        def export_images(db: Database, image_indexes: list[int]):
            export_path_dialog = InputDialog()
            export_path_dialog.setWindowTitle(f"Input path to export {len(image_indexes)} images")
            export_path_dialog.setToolTip("This is the folder where the images will be put.")
            if export_path_dialog.exec() == QDialog.DialogCode.Accepted:
                path_input = export_path_dialog.input_field.text()
            else:
                return False
            if not path_input or not os.path.exists(path_input):
                parameters.log.warning("The specified path doesn't exists")
                return False

            export_group_dialog = InputDialog()
            export_group_dialog.setWindowTitle("Input group name")
            export_group_dialog.setToolTip(
                "If no group is specified, it won't add images to the group and it will copy the images to the root folder of the database.")
            if export_group_dialog.exec() == QDialog.DialogCode.Accepted:
                group_input = export_group_dialog.input_field.text()
            else:
                parameters.log.warning("No specified group")
                return False
            db.export_database(image_indexes, path_input, group_input)

class ImageViewBase(QWidget, imageViewBase.Ui_Form):
    selectedImagesChanges = Signal(list) # list of images index selected
    areDisplayedRectangles = Signal(bool)
    editedRectangle = Signal(tuple) # coordinates (top, left, width, height) and name of the created rect
    editedGroups = Signal()

    def __init__(self, db: Database):
        super().__init__()
        self.setupUi(self)

        self.stackedWidget.widget(0).layout().removeWidget(self.listView_groups)
        self.stackedWidget.widget(0).layout().removeWidget(self.listView_other)
        self.other_splitter = QSplitter()
        self.other_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.other_splitter.addWidget(self.listView_groups)
        self.other_splitter.addWidget(self.listView_other)
        self.stackedWidget.widget(0).layout().insertWidget(2, self.other_splitter)

        self.db = db  # same as the one in the main, so changing this db will change the main one
        self.current_group = "All"
        self.current_sort: SortType = SortType.TAGS_LEN
        self.current_search_tags = []

        # Image Objects Settings
        self.image_load_size = min(parameters.PARAMETERS["image_load_size"], 512)
        self.images_widgets: dict[int: object] = {}
        self.min_image_size = 16

        # load the images that are in the DB
        self.db.create_images_objects(self.image_load_size)
        self.db.tokenize_all_images()

        # slider
        self.horizontalSlider_thumbnail_size.setMinimum(self.min_image_size)
        if parameters.PARAMETERS["doubling_image_thumbnail_max_size"]:
            self.horizontalSlider_thumbnail_size.setMaximum(self.image_load_size*2)
        else:
            self.horizontalSlider_thumbnail_size.setMaximum(self.image_load_size)
        self.horizontalSlider_thumbnail_size.setValue(self.image_load_size)
        self.horizontalSlider_thumbnail_size.valueChanged.connect(self.slider_thumbnail_size_changed)

        # group names
        self.comboBox_group_name.addItem("All")
        self.comboBox_group_name.addItems([group.group_name for group in self.db.groups.values()])
        self.comboBox_group_name.currentTextChanged.connect(self.selected_group_changed)

        # sort type
        k = 0
        for x in SortType:
            self.comboBox_sort_type.addItem(x.value[0])
            self.comboBox_sort_type.setItemData(k, x.value[2], QtCore.Qt.ItemDataRole.ToolTipRole)
            k += 1
        self.comboBox_sort_type.currentTextChanged.connect(self.selected_sort_changed)

        # sentence search and reverse search
        self.checkBox_reverse.stateChanged.connect(self.update_sorting)
        self.checkBox_include_sentence.stateChanged.connect(self.update_sorting)

        # tag search
        self.lineEdit_tag_search.editingFinished.connect(self.search_tags_changed)

        # selection updated
        self.listView_groups.clicked.connect(self.clicked_images_changed)
        self.checkBox_single_selection_mode.stateChanged.connect(self.selection_mode_changed)

        # show ungrouped images when selecting groups
        self.checkBox_toggle_ungrouped_images.clicked.connect(self.update_other_view)

        # add and remove selections to and from groups
        self.pushButton_remove_selection_from_group.clicked.connect(self.remove_selection_from_group)
        self.pushButton_add_selection_to_group.clicked.connect(self.add_selection_to_group)

        # create new group
        self.pushButton_add_group.clicked.connect(self.create_group)
        self.pushButton_edit_group_name.clicked.connect(self.edit_group_name)
        self.pushButton_deleted_group.clicked.connect(self.delete_group)

        # Single Image View
        self.pushButton_prev_image.clicked.connect(self.prev_single_image)
        self.single_image.leftClickedWithoutRectangle.connect(self.clicked_image_without_rectangle)
        self.pushButton_next_image.clicked.connect(self.next_single_image)
        self.current_edit_rect_name = ""
        self.single_image.rectangleCreated.connect(self.created_rectangle)
        self.checkBox_masking.stateChanged.connect(self.masking_checkbox_clicked)

        # create image objects and show them
        self.create_all_images_frames()


        model = BaseImageView(self.images_widgets)
        model_other = BaseImageView(self.images_widgets)
        self.listView_groups.setModel(model)
        self.listView_groups.setViewMode(self.listView_groups.ViewMode.ListMode)
        self.listView_groups.setFlow(self.listView_groups.Flow.LeftToRight)
        self.listView_groups.setWrapping(True)
        self.listView_groups.setResizeMode(self.listView_groups.ResizeMode.Adjust)
        self.listView_groups.setSelectionMode(self.listView_groups.SelectionMode.ExtendedSelection)
        self.listView_groups.setIconSize(QSize(self.image_load_size, self.image_load_size))
        self.listView_other.setModel(model_other)
        self.listView_other.setViewMode(self.listView_groups.ViewMode.ListMode)
        self.listView_other.setFlow(self.listView_groups.Flow.LeftToRight)
        self.listView_other.setWrapping(True)
        self.listView_other.setResizeMode(self.listView_groups.ResizeMode.Adjust)
        self.listView_other.setSelectionMode(self.listView_groups.SelectionMode.ExtendedSelection)
        self.listView_other.setIconSize(QSize(self.image_load_size, self.image_load_size))
        self.listView_other.hide()
        self.selected_sort_changed(self.comboBox_sort_type.currentText())

    @Slot(int)
    def slider_thumbnail_size_changed(self, new_value):
        self.listView_groups.setIconSize(QSize(new_value, new_value))
        self.listView_other.setIconSize(QSize(new_value, new_value))

    @Slot(str)
    def selected_group_changed(self, current_group):
        self.current_group = current_group
        self.update_sorting()

    @Slot(str)
    def selected_sort_changed(self, text):
        self.current_sort = get_sort_member(text)
        if self.current_sort == SortType.SIMILARITY_GROUP:
            self.db.find_similar_images()
        if self.current_sort == SortType.RARE_TAGS_COUNT:
            self.db.update_rare_tags()
        if self.current_sort == SortType.CONFLICTS_LEN:
            self.db.update_filter_review()
        self.update_sorting()

    @Slot()
    def search_tags_changed(self):
        search_tags = self.lineEdit_tag_search.text().split(',')
        self.current_search_tags = files.loose_tags_search_settings_from_tags_list(search_tags)
        parameters.log.info(self.current_search_tags)
        self.update_sorting()
        self.update_other_view()

    @Slot()
    def update_sorting(self):
        """
        Update the sorting view, and the other view
        """
        current_list_sort = sorted([(x, self.current_sort.sort_function(self.db.images[x])) for x in range(len(self.db.images)) if self.image_to_view(x)], key=lambda x: x[1], reverse=not self.checkBox_reverse.isChecked())
        self.listView_groups.model().apply_order(current_list_sort, self.current_sort.get_attribute())
        self.label_image_view_count.setText(f"{self.listView_groups.model().rowCount()} images")
        self.update_other_view()

    @Slot()
    def update_other_view(self):
        """
        Update the other model view
        """
        if self.current_group == "All":
            self.listView_other.hide()
            return

        current_list_sort = sorted([(x, self.current_sort.sort_function(self.db.images[x])) for x in range(len(self.db.images)) if self.image_to_other_view(x)], key=lambda x: x[1], reverse=not self.checkBox_reverse.isChecked())
        if len(current_list_sort)==0:
            self.listView_other.hide()
        else:
            self.listView_other.show()
            self.listView_other.model().apply_order(current_list_sort)

    def image_to_view(self, image_index: int):
        tag_to_search_through = self.db.images[image_index].get_search_tags()
        if self.checkBox_include_sentence.isChecked():
            tag_to_search_through = tag_to_search_through.union([self.db.images[image_index].sentence_description.sentence])
        if self.current_group == "All":
            if self.current_search_tags:
                if not files.loose_tags_check(self.current_search_tags, tag_to_search_through):
                    return False
                else:
                    return True
            else:
                return True
        elif self.db.images[image_index].md5 in self.db.groups[self.current_group]:
            if self.current_search_tags:
                if not files.loose_tags_check(self.current_search_tags, tag_to_search_through):
                    return False
                else:
                    return True
            else:
                return True
        return False

    def image_to_other_view(self, image_index: int):
        if self.db.images[image_index].md5 in self.db.groups[self.current_group]:
            return False
        tag_to_search_through = self.db.images[image_index].get_search_tags()
        if self.checkBox_include_sentence.isChecked():
            tag_to_search_through = tag_to_search_through.union([self.db.images[image_index].sentence_description.sentence])
        if self.checkBox_toggle_ungrouped_images.isChecked():
            if self.current_search_tags:
                if files.loose_tags_check(self.current_search_tags, tag_to_search_through):
                    return True
            else:
                return True
        else:
            if self.db.images[image_index].groups_length()==0:
                if self.current_search_tags:
                    if files.loose_tags_check(self.current_search_tags, tag_to_search_through):
                        return True
                else:
                    return True
        return False

    @Slot()
    def clicked_images_changed(self):
        selected_indexes = [self.listView_groups.model().db_index(index) for index in self.listView_groups.selectedIndexes()]
        self.apply_selection_gradient(self.listView_groups.selectedIndexes())
        self.update_selected_images_changed(selected_indexes)

    def apply_selection_gradient(self, selected_model_indexes:  list[QtCore.QModelIndex]):
        self.listView_groups.model().update_selected_images(selected_model_indexes)

    def update_selected_images_changed(self, selected_indexes):
        """
        Args:
            selected_indexes: indexes of the images inside the database images list
        """

        if len(selected_indexes) == 1 and self.checkBox_zoom_on_click.isChecked():
            self.stackedWidget.setCurrentIndex(1)
            image = self.db.images[selected_indexes[0]]
            if os.path.exists(image.path):
                self.single_image.update_image(image.path)
                # Do the label
                date_modified = datetime.datetime.fromtimestamp(os.path.getmtime(image.path))
                date_created = datetime.datetime.fromtimestamp(os.path.getctime(image.path))
                self.single_info_label.setText(
                    f'Width: {image.image_width}, Height: {image.image_height}, Date modified: {date_modified}, Date created: {date_created}')
            else:
                self.single_image.update_image("")
                self.single_info_label.setText("Image path doesn't exist")
            self.label_image_md5.setText(f"MD5: {image.md5}, Original MD5: {image.original_md5}")

        else:
            self.stackedWidget.setCurrentIndex(0)

        self.single_image.activated_drawing = False # in case of not doing the edit
        self.selectedImagesChanges.emit(selected_indexes)

    @Slot()
    def prev_single_image(self):
        if self.listView_groups.selectedIndexes()[0].row() == 0:
            parameters.log.info("First image, can't go back")
            return False
        next_index = self.listView_groups.model().index(self.listView_groups.selectedIndexes()[0].row()-1, self.listView_groups.selectedIndexes()[0].column())
        self.listView_groups.setCurrentIndex(next_index)
        self.clicked_images_changed()

    @Slot()
    def next_single_image(self):
        if self.listView_groups.selectedIndexes()[0].row() + 1 >= self.listView_groups.model().rowCount():
            parameters.log.info("Last image, can't go further")
            return False
        next_index = self.listView_groups.model().index(
            self.listView_groups.selectedIndexes()[0].row() + 1,
            self.listView_groups.selectedIndexes()[0].column())
        self.listView_groups.setCurrentIndex(next_index)
        self.clicked_images_changed()

    @Slot()
    def clicked_image_without_rectangle(self):
        self.stackedWidget.setCurrentIndex(0)

    @Slot()
    def selection_mode_changed(self):
        if self.checkBox_single_selection_mode.isChecked():
            self.listView_groups.setSelectionMode(self.listView_groups.SelectionMode.SingleSelection)
        else:
            self.listView_groups.setSelectionMode(self.listView_groups.SelectionMode.ExtendedSelection)

    @Slot()
    def remove_selection_from_group(self):
        if self.current_group == "All":
            parameters.log.info("No group selected.")
            return False
        if len(self.listView_groups.selectedIndexes())==0:
            parameters.log.info("No images selected.")
            return False
        for w_index in self.listView_groups.selectedIndexes():
            image_index = self.listView_groups.model().db_index(w_index)
            self.db.remove_image_from_group(self.current_group, image_index)
        self.listView_groups.clearSelection()
        self.update_sorting()
        self.update_other_view()

    @Slot()
    def add_selection_to_group(self):
        if self.current_group == "All":
            parameters.log.info("No group selected.")
            return False
        if len(self.listView_other.selectedIndexes())==0:
            parameters.log.info("No images selected.")
            return False
        for w_index in self.listView_other.selectedIndexes():
            image_index = self.listView_other.model().db_index(w_index)
            self.db.add_image_to_group(self.current_group, image_index)
        self.listView_other.clearSelection()
        self.update_sorting()
        self.update_other_view()

    @Slot()
    def create_group(self):
        create_group_dialog = InputDialog()
        if create_group_dialog.exec() == QDialog.DialogCode.Accepted:
            user_input = create_group_dialog.input_field.text()
        else:
            return False
        if not user_input or user_input in self.db.groups.keys():
            return False
        self.db.groups[user_input] = GroupElement(group_name=user_input)
        self.edited_groups(user_input)
        self.editedGroups.emit()

    @Slot()
    def edit_group_name(self):
        if self.current_group == "All":
            parameters.log.info("Select a group to edit its name")
            return False
        edit_group_dialog = InputDialog(default_text=self.current_group)
        if edit_group_dialog.exec() == QDialog.DialogCode.Accepted:
            user_input = edit_group_dialog.input_field.text()
        else:
            return False
        if not user_input or user_input in self.db.groups.keys():
            return False
        parameters.log.info(f"Changing from {self.current_group} to {user_input}")
        self.db.edit_group_name(current_group_name=self.current_group, new_group_name=user_input)
        self.edited_groups(user_input)
        self.editedGroups.emit()

    @Slot()
    def delete_group(self):
        if self.current_group == "All":
            parameters.log.info("No group selected")
            return False
        if not confirmation_dialog(self):
            return False
        self.db.remove_group(self.current_group)
        self.edited_groups()
        self.editedGroups.emit()

    def edited_groups(self, preferred_group=""):
        """
        When a group name has changed, or a new one, or a deleted one
        """
        previous_name = self.comboBox_group_name.currentText()
        self.comboBox_group_name.setCurrentIndex(0)
        while self.comboBox_group_name.count()>1:
            self.comboBox_group_name.removeItem(1)
        self.comboBox_group_name.addItems([group.group_name for group in self.db.groups.values()])
        if previous_name in [group.group_name for group in self.db.groups.values()]:
            new_i = self.comboBox_group_name.findText(previous_name, flags=QtCore.Qt.MatchFlag.MatchExactly)
            self.comboBox_group_name.setCurrentIndex(new_i)
        if preferred_group in [group.group_name for group in self.db.groups.values()]:
            new_i = self.comboBox_group_name.findText(preferred_group, flags=QtCore.Qt.MatchFlag.MatchExactly)
            self.comboBox_group_name.setCurrentIndex(new_i)

    @Slot()
    def history_changed(self):
        """When the history changes, then we need to change the groups name mainly, the rest is not interesting for now"""
        previous_name = self.comboBox_group_name.currentText()

        if self.comboBox_group_name.count() != len(self.db.groups)+1 or not all([True if self.comboBox_group_name.findText(group.group_name, flags=QtCore.Qt.MatchFlag.MatchExactly)!=-1 else False for group in self.db.groups.values()]):
            parameters.log.info("Changed Groups from History")
            self.comboBox_group_name.setCurrentIndex(0)
            while self.comboBox_group_name.count()>1:
                self.comboBox_group_name.removeItem(1)
            self.comboBox_group_name.addItems([group.group_name for group in self.db.groups.values()])
            if previous_name in [group.group_name for group in self.db.groups.values()]:
                new_i = self.comboBox_group_name.findText(previous_name, flags=QtCore.Qt.MatchFlag.MatchExactly)
                self.comboBox_group_name.setCurrentIndex(new_i)
            self.editedGroups.emit()



    def create_all_images_frames(self):
        for k in range(len(self.db.images)):
            image_object = QPixmap(self.db.images[k].get_image_object())
            if parameters.PARAMETERS["doubling_image_thumbnail_max_size"]:
                image_object = image_object.scaled(self.image_load_size * 2, self.image_load_size * 2,
                                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                   QtCore.Qt.TransformationMode.FastTransformation)
            else:
                image_object = image_object.scaled(self.image_load_size, self.image_load_size,
                                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                   QtCore.Qt.TransformationMode.FastTransformation)
            self.images_widgets[k] = (image_object, self.db.images[k])

    def update_image_frames(self, images_indexes):
        """
        When an image has been changed, permits to recreate the images frames for these specific indexes
        """
        for k in images_indexes:
            image_object = QPixmap(self.db.images[k].get_image_object())
            if parameters.PARAMETERS["doubling_image_thumbnail_max_size"]:
                image_object = image_object.scaled(self.image_load_size * 2, self.image_load_size * 2,
                                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                   QtCore.Qt.TransformationMode.FastTransformation)
            else:
                image_object = image_object.scaled(self.image_load_size, self.image_load_size,
                                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                                   QtCore.Qt.TransformationMode.FastTransformation)
            self.images_widgets[k] = (image_object, self.db.images[k])

        model = BaseImageView(self.images_widgets)
        model_other = BaseImageView(self.images_widgets)
        self.listView_groups.setModel(model)
        self.listView_other.setModel(model_other)
        self.selected_sort_changed(self.comboBox_sort_type.currentText())

    def all_visible_images(self) -> list[int]:
        """
        Returns: list of indexes of all visible images
        """
        return [self.listView_groups.model().db_index(self.listView_groups.model().index(index, 0)) for index in range(self.listView_groups.model().rowCount())]


    def visualise_rectangles(self, rects: list[RectElement]):
        """
        Visualise the rectangles (if not in single image view emit it: notDisplayedRectangles)
        Args:
            rects: List of RectElement to be displayed
        """
        self.single_image.activated_drawing = False
        if not self.stackedWidget.currentIndex() == 1:
            self.areDisplayedRectangles.emit(False)
            return

        self.single_image.clear_rectangles()
        for rect in rects:
            self.single_image.add_rectangle((rect.top, rect.left, rect.width, rect.height), name=rect.name, color=QtGui.QColor(rect.color))
        if self.checkBox_masking.isChecked():
            self.areDisplayedRectangles.emit(True)
        else:
            self.areDisplayedRectangles.emit(False)

    def masking_checkbox_clicked(self):
        """
        Show the rectangles view if necessary (by emitting the corresponding signal)
        """
        if self.checkBox_masking.isChecked():
            self.areDisplayedRectangles.emit(True)
        else:
            self.areDisplayedRectangles.emit(False)
    def edit_rectangle(self, rect_name: str):
        """
        Enable the Edit Effect
        """
        parameters.log.info(f"rect_name: {rect_name}")
        if not self.stackedWidget.currentIndex() == 1:
            return
        self.single_image.edit_rectangle()
        self.current_edit_rect_name = rect_name

    @Slot(tuple)
    def created_rectangle(self, coordinates):
        self.editedRectangle.emit((self.current_edit_rect_name, coordinates))
        self.current_edit_rect_name = ""

class TagsViewBase(QWidget, tagsViewBase.Ui_Form):
    askForRareTags = Signal()
    visualiseRectangles = Signal(list) # Send a list of all rectangles that should be visible (list of RectElements)
    editRectangleRequested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.image: ImageDatabase = None

        self.layout().removeWidget(self.listView_rejected)
        self.layout().removeWidget(self.widget_2)
        self.layout().removeWidget(self.listView_tags)
        self.layout().removeWidget(self.treeView_conflicts)
        self.layout().removeWidget(self.listView_recommendations)

        right_splitter = QSplitter()
        right_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        right_splitter.addWidget(self.treeView_conflicts)
        right_splitter.addWidget(self.listView_recommendations)

        tags_splitter = QSplitter()
        tags_splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        tags_splitter.addWidget(self.listView_tags)
        tags_splitter.addWidget(right_splitter)

        splitter = QSplitter()
        splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        splitter.addWidget(self.widget_2)
        splitter.addWidget(self.listView_rejected)
        splitter.addWidget(tags_splitter)

        rectangle_splitter = QSplitter()
        rectangle_splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        rectangle_splitter.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding))

        self.rectangle_view = RectangleTagsView()
        self.rectangle_view.editRectangleRequested.connect(lambda name: self.editRectangleRequested.emit(name))
        self.rectangle_view.deleteRectangleRequested.connect(self.deleted_rectangle)
        self.rectangle_view.createRectangleRequested.connect(self.created_rectangle)
        self.rectangle_view.editColorRequested.connect(self.edited_color)
        self.rectangle_view.hide()

        rectangle_splitter.addWidget(self.rectangle_view)
        rectangle_splitter.addWidget(splitter)

        self.layout().insertWidget(4, rectangle_splitter)


        self.comboBox_score_tags.addItem("NONE")
        self.comboBox_score_tags.addItems(tag_categories.QUALITY_LABELS)
        self.comboBox_score_tags.currentTextChanged.connect(self.changed_aesthetic_score)

        # Configs
        self.highlight_tags = []
        self.lineEdit_tag_highlight.editingFinished.connect(self.changed_highlight)
        self.lineEdit_add_tags.returnPressed.connect(self.add_tags)
        self.checkBox_reviewed.stateChanged.connect(self.changed_reviewed)
        self.plainTextEdit_sentence.textChanged.connect(self.sentence_changed)

        # Clicks on base tags
        if parameters.PARAMETERS["double_click"]:
            self.listView_tags.doubleClicked.connect(self.full_tags_clicked)
            self.listView_rejected.doubleClicked.connect(self.rejected_tags_clicked)
            self.listView_recommendations.doubleClicked.connect(self.recommendations_tags_clicked)
            self.treeView_conflicts.doubleClicked.connect(self.conflicts_tags_clicked)
        else:
            self.listView_tags.clicked.connect(self.full_tags_clicked)
            self.listView_rejected.clicked.connect(self.rejected_tags_clicked)
            self.listView_recommendations.clicked.connect(self.recommendations_tags_clicked)
            self.treeView_conflicts.clicked.connect(self.conflicts_tags_clicked)

        # Highlight rare tags
        self.checkBox_highligh_rare_tags.stateChanged.connect(self.highlight_rare_tags_clicked)
        self.rare_tags = set()

        self.listView_tags.keyPressEvent = lambda event: self.on_key_press(event, self.listView_tags)
        self.listView_rejected.keyPressEvent = lambda event: self.on_key_press(event, self.listView_rejected)
        self.listView_recommendations.keyPressEvent = lambda event: self.on_key_press(event, self.listView_recommendations)
        self.treeView_conflicts.keyPressEvent = lambda event: self.on_key_press(event, self.treeView_conflicts)
        self.treeView_conflicts.rightClicked.connect(self.right_clicked_conflicts)

        # Tree View Update
        #self.pushButton_refresh_tree.clicked.connect(self.refresh_tree_clicked)

    def on_key_press(self, event, view):
        if event.key() == QtCore.Qt.Key.Key_W:
            parameters.log.info("Pressed Key")
            selected_index = view.currentIndex()
            if selected_index.isValid():
                webbrowser.open(f"https://danbooru.donmai.us/wiki_pages/{selected_index.data(QtGui.Qt.ItemDataRole.DisplayRole).replace(' ', '_')}")
        else:
            super().keyPressEvent(event)

    def view_image(self, image: ImageDatabase):
        self.image = image
        self.image.filter(update_review=True)
        if self.checkBox_highligh_rare_tags.isChecked():
            self.askForRareTags.emit()

        # Tags Label Updates
        if self.image.path and os.path.exists(self.image.path):
            self.label_image_path.setText(self.image.path)
            self.label_image_path.show()
            self.label_image_ext.setText(os.path.splitext(self.image.path)[1])
            self.label_image_ext.show()
            self.label_image_size.setText(f"{round(os.path.getsize(self.image.path)/(1024*1024), ndigits=4)} MB")
            self.label_image_size.show()
        else:
            self.label_image_path.hide()
            self.label_image_ext.hide()
            self.label_image_size.hide()

        self.label_tags_len.setText(f"{len(self.image.full_tags)} tags")
        self.label_sentence_len.setText(f"{self.image.sentence_description.get_token_length()} tokens")
        token_len = self.image.full_tags.get_token_length()
        self.label_token_len.setText(f"{token_len} tokens")
        if token_len > 225:
            style = "QLabel { color : red; }" + self.label_image_path.styleSheet()
            self.label_token_len.setStyleSheet(style)
        elif token_len > 223:
            style = "QLabel { color : orange; }" + self.label_image_path.styleSheet()
            self.label_token_len.setStyleSheet(style)
        else:
            style = self.label_image_path.styleSheet()
            self.label_token_len.setStyleSheet(style)

        # Display Rejected tags
        self.image.rejected_tags.init_display_properties()
        self.image.rejected_tags.init_manual_display_properties(self.image.manual_tags+self.image.rejected_manual_tags)
        self.image.rejected_tags.init_rejected_display_properties(True)
        self.image.rejected_tags.init_highlight_display_properties(self.highlight_tags)
        rejected_tags_model = UniqueTagsView(self.image.rejected_tags, self.image, {})
        self.listView_rejected.setModel(rejected_tags_model)

        # Display Full Tags
        self.image.full_tags.init_display_properties()
        self.image.full_tags.init_manual_display_properties(self.image.manual_tags+self.image.rejected_manual_tags)
        self.image.full_tags.init_rejected_display_properties(self.image.rejected_tags)

        # Check for rare tags
        if self.checkBox_highligh_rare_tags.isChecked():
            self.image.full_tags.init_highlight_display_properties(self.rare_tags.union(self.highlight_tags))
        else:
            self.image.full_tags.init_highlight_display_properties(self.highlight_tags)
        full_tags_model = UniqueTagsView(self.image.full_tags, self.image, self.image.uncommon_tags)
        self.listView_tags.setModel(full_tags_model)

        # Display Conflicts
        for conflict in self.image.filtered_review.values():
            conflict.init_display_properties()
            conflict.init_manual_display_properties(self.image.manual_tags+self.image.rejected_manual_tags)
            conflict.init_rejected_display_properties(self.image.rejected_tags)
        conflict_tags_model = ConflictTagsView(self.image.filtered_review, self.image)
        if not self.image.filtered_review:
            self.treeView_conflicts.hide()
        else:
            self.treeView_conflicts.show()
        self.treeView_conflicts.setModel(conflict_tags_model)
        self.treeView_conflicts.expandAll()


        # Display Sentence
        self.plainTextEdit_sentence.setPlainText(str(self.image.sentence_description))

        # Display Recommendations
        recommendations = image.get_recommendations()
        recommendations.init_display_properties()
        recommendation_tags_model = UniqueTagsView(recommendations, self.image, {})
        if not recommendations:
            self.listView_recommendations.hide()
        else:
            self.listView_recommendations.show()
        self.listView_recommendations.setModel(recommendation_tags_model)

        # Display Aesthetic Score
        if self.image.score_label and self.image.score_label in tag_categories.QUALITY_LABELS:
            self.comboBox_score_tags.setCurrentIndex(tag_categories.QUALITY_LABELS.index(self.image.score_label)+1)
        else:
            self.comboBox_score_tags.setCurrentIndex(0)
        for index in range(self.comboBox_score_tags.count()):
            self.comboBox_score_tags.setItemData(index, QtGui.QColor(0, 0, 0, 255),role=QtCore.Qt.ItemDataRole.BackgroundRole)
            if index == self.comboBox_score_tags.currentIndex():
                self.comboBox_score_tags.setItemData(index, QtGui.QColor(0,206,209,255),role=QtCore.Qt.ItemDataRole.BackgroundRole)

        # Display reviewed
        if self.image.manually_reviewed:
            self.checkBox_reviewed.setChecked(True)
        else:
            self.checkBox_reviewed.setChecked(False)

        # Display rectangles
        if self.image.rects:
            self.rectangle_view.show()
            self.visualiseRectangles.emit(self.image.rects)
            self.rectangle_view.init_new_rectangles(self.image.rects)
        else:
            self.rectangle_view.hide()
            self.visualiseRectangles.emit(self.image.rects)
            self.rectangle_view.init_new_rectangles(self.image.rects)

    def apply_rectangle_coordinates(self, name_coordinates):
        self.image.rects[[rect.name for rect in self.image.rects].index(name_coordinates[0])].apply_from_dict({"coordinates": name_coordinates[1]})
        self.visualiseRectangles.emit(self.image.rects)
        self.rectangle_view.init_new_rectangles(self.image.rects)

    @Slot(str)
    def deleted_rectangle(self, rectangle_name: str):
        self.image.rects.pop([rect.name for rect in self.image.rects].index(rectangle_name))
        self.view_image(self.image)

    @Slot()
    def created_rectangle(self):
        new_name = "manual_"
        i = 0
        while new_name+str(i) in [x.name for x in self.image.rects]:
            i+=1
        new_name = new_name+str(i)
        new_rectangle = RectElement(new_name)
        self.image.rects.append(new_rectangle)
        self.view_image(self.image)

    @Slot(tuple)
    def edited_color(self, rectangle_info: tuple[str, str]):
        """

        Args:
            rectangle_info: tuple of the name and the hexadecimal color

        Returns:

        """
        self.image.rects[[rect.name for rect in self.image.rects].index(rectangle_info[0])].color = rectangle_info[1]
        self.view_image(self.image)


    def return_image(self) -> ImageDatabase:
        return self.image

    @Slot()
    def changed_highlight(self):
        self.highlight_tags = TagsList(tags=[], name="highlight_tags")
        for t in [t.strip() for t in self.lineEdit_tag_highlight.text().split(",") if t.strip()]:
            # Highlight tags when category name is explicit
            if self.image and t in self.image.auto_tags.names():
                self.highlight_tags+=self.image.auto_tags[t]
            elif self.image and t in self.image.external_tags.names():
                self.highlight_tags+=self.image.external_tags[t]
            else:
                self.highlight_tags+=t
        if self.image:
            self.view_image(self.image)

    @Slot()
    def highlight_rare_tags_clicked(self):
        if self.image:
            self.view_image(self.image)

    @Slot()
    def full_tags_clicked(self, index):
        if not index.isValid():
            return False
        tag = self.listView_tags.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)
        self.image.manual_tags -= TagElement(tag)
        self.image.rejected_manual_tags += TagElement(tag)
        self.view_image(self.image)

    @Slot()
    def rejected_tags_clicked(self, index):
        if not index.isValid():
            return False
        tag = self.listView_rejected.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)
        self.image.manual_tags += TagElement(tag)
        self.image.rejected_manual_tags -= TagElement(tag)
        self.view_image(self.image)
    @Slot()
    def recommendations_tags_clicked(self, index):
        if not index.isValid():
            return False
        tag = self.listView_recommendations.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)
        self.image.manual_tags += TagElement(tag)
        self.image.rejected_manual_tags -= TagElement(tag)
        self.view_image(self.image)

    @Slot()
    def right_clicked_conflicts(self):
        index = self.treeView_conflicts.currentIndex()
        if not index.isValid():
            return False
        if not index.parent().isValid():
            self.image.append_resolved_conflict(index.internalPointer()["name"])
            self.view_image(self.image)
            return True
        tag = index.internalPointer()["name"]
        self.image.append_rejected_manual_tags(tag)
        self.view_image(self.image)

    @Slot()
    def conflicts_tags_clicked(self, index):
        if not index.isValid():
            return False
        if not index.parent().isValid():
            self.image.append_resolved_conflict(index.internalPointer()["name"])
            self.view_image(self.image)
            return True
        tag = index.internalPointer()["name"]
        sub_category = index.parent().internalPointer()
        to_remove = [x["name"] for x in sub_category["children"] if x["name"] != tag]
        self.image.append_rejected_manual_tags(to_remove)
        self.image.remove_manual_tags(to_remove)
        self.view_image(self.image)

    @Slot()
    def changed_aesthetic_score(self):
        if isinstance(self.image, ImageDatabase):
            text = self.comboBox_score_tags.currentText()
            self.image.score_label = TagElement(text)

    @Slot()
    def add_tags(self):
        text = self.lineEdit_add_tags.text()
        tags = [tag.strip() for tag in text.split(",")]
        if isinstance(self.image, ImageDatabase):
            self.image.manual_tags += tags
            self.image.rejected_manual_tags -= tags
            self.view_image(self.image)
            if self.checkBox_clear_on_add.isChecked():
                self.lineEdit_add_tags.clear()

    @Slot()
    def changed_reviewed(self):
        if isinstance(self.image, ImageDatabase):
            if self.checkBox_reviewed.isChecked():
                self.image.manually_reviewed = True
            else:
                self.image.manually_reviewed = False

    @Slot()
    def sentence_changed(self):
        if isinstance(self.image, ImageDatabase):
            self.image.sentence_description.sentence = self.plainTextEdit_sentence.toPlainText().strip()

    def clicked_favourites(self, tag):
        if isinstance(self.image, ImageDatabase):
            self.image.append_manual_tags(tag)
            self.image.remove_rejected_manual_tags(tag)
            self.view_image(self.image)

    def copy_tags_to_clipboard(self):
        clipboard = QApplication.clipboard()
        tags = [str(self.listView_tags.model().data(self.listView_tags.model().index(index, 0), QtCore.Qt.ItemDataRole.DisplayRole)) for index in range(self.listView_tags.model().rowCount())]
        text = ', '.join(tags)
        clipboard.setText(text)

    """
    @Slot()
    def refresh_tree_clicked(self):
        if isinstance(self.image, ImageDatabase):
            self.image.get_full_only_tags()
            t0 = time.time()
            graph = TreeClass.Graph()
            graph.create_graph()
            t1 = time.time()
            unused_tags = graph.activate(self.image.get_full_only_tags())
            t2 = time.time()
            rough_results = graph.rough_sentence()
            t3 = time.time()

            parameters.log.info(f"Time to Create Graph: {t1-t0}s")
            parameters.log.info(f"Time to Activate Graph: {t2-t1}s")
            parameters.log.info(f"Time to Print Graph: {t3-t2}s")

            self.label_tree_full_tags.setText("Full Tags: "+", ".join(self.image.get_full_only_tags()))
            self.label_tree_unused_tags.setText("Unused Tags: "+", ".join(unused_tags))
            self.plainTextEdit_tree_result.setPlainText("\n".join(rough_results))
    """

class DatabaseViewBase(QWidget):
    def __init__(self, db: Database):
        super().__init__()

        self.db = db
        self.db_on_load = copy.deepcopy(self.db)

        # history, the most ancient one is the first one, the most recent one is on index -1, only the first one is a database the others are the difference between the older database and the most recent one at the time of making the update
        self.db_history: list[tuple[Database|dict, str]] = []
        self.db_last_saved_changes: dict = {}
        self.currently_selected_database = 0


        # create the big 3 layout
        splitter = QSplitter()
        simple_layout = QHBoxLayout()
        simple_layout.setContentsMargins(0,0,0,0)
        simple_layout.setSpacing(0)
        self.stacked_widget = QStackedWidget()
        self.image_view = ImageViewBase(self.db)
        self.tags_view = TagsViewBase()
        self.database_tools = DatabaseToolsBase(self.db)
        self.stacked_widget.addWidget(self.image_view)
        splitter.addWidget(self.stacked_widget)
        splitter.addWidget(self.tags_view)
        splitter.addWidget(self.database_tools)
        simple_layout.addWidget(splitter)
        self.setLayout(simple_layout)

        # Connect signal from ImageViewBase to self
        self.image_view.selectedImagesChanges.connect(self.selected_images_changed)
        self.selected_images = []

        self.database_tools.clickedBatchFunction.connect(self.execute_batch_func)

        # Popup Window
        self.database_tools.clickedPopupWindow.connect(self.open_popup_window)
        self.popup_window = None

        # Favourites
        self.database_tools.clickedFavourites.connect(self.clicked_favourites)

        # Ask for rare tags
        self.tags_view.askForRareTags.connect(self.get_rare_tags)

        # Replace Button
        self.database_tools.changedDatabaseSettings.connect(self.changed_database_settings)

        # Frequency
        self.database_tools.frequencyTagSelected.connect(self.frequency_tag_clicked)
        self.database_tools.removeTagsFrequencySelected.connect(self.tags_to_remove_frequency_selected)

        # Save Database
        self.database_tools.clickedSaveDatabase.connect(self.save_database)

        # History View
        self.history_buttons = QButtonGroup()
        self.history_buttons.addButton(QRadioButton(f"Database on load"), id=0)
        self.history_buttons.button(0).setChecked(True)
        self.history_buttons.idClicked.connect(self.change_to_history)
        self.database_tools.scrollAreaWidgetContents_history.layout().addWidget(self.history_buttons.button(0))
        #self.database_tools.tabWidget.setTabEnabled(4, False)
        self.database_tools.pushButton_clean_history.clicked.connect(self.clean_history)

        # Auto Completion
        self.tags_view.lineEdit_add_tags.setCompleter(completer)
        self.tags_view.lineEdit_tag_highlight.setCompleter(completer)

        # Asked for the visualisation of rectangles
        self.tags_view.visualiseRectangles.connect(self.image_view.visualise_rectangles)
        # No rectangle Visualised
        self.image_view.areDisplayedRectangles.connect(lambda x: self.tags_view.rectangle_view.show() if x else self.tags_view.rectangle_view.hide())
        # Edit Rectangle Name
        self.tags_view.editRectangleRequested.connect(self.image_view.edit_rectangle)
        self.image_view.editedRectangle.connect(self.tags_view.apply_rectangle_coordinates)

        # Edited Groups
        self.image_view.editedGroups.connect(self.database_tools.edited_groups)

    @Slot()
    def save_database(self):
        self.save_image()
        current_changes = self.db.get_changes(self.db_on_load)
        if self.db_last_saved_changes == current_changes:
            parameters.log.info("No changes detected in the database")
            return False
        self.db.save_database()
        self.db_last_saved_changes = current_changes


    def database_changed(self, changed_indexes):
        """
        All functions that do any changes to a specific index should report it to this function
        If it applies only to the selected image it's not necessary though
        """
        if any(changed_index in self.selected_images for changed_index in changed_indexes):
            self.selected_images_changed(self.selected_images)

    @Slot(list)
    def selected_images_changed(self, image_indexes, history=False):
        if not history:
            self.save_image()
        self.change_popup_window(image_indexes)
        if len(image_indexes) == 1:
            self.selected_images = image_indexes
            self.tags_view.view_image(self.db.images[self.selected_images[0]])
        elif len(image_indexes) > 1:
            self.selected_images = image_indexes
            common_image = self.db.get_common_image(self.selected_images)
            self.tags_view.view_image(common_image)

    def save_image(self):
        if self.selected_images:
            current_image = self.tags_view.return_image()
            self.db.changed_common_image(current_image, self.selected_images)

    @Slot(tuple)
    def execute_batch_func(self, inherent):
        """
        This slot is called to execute the batch functions
        Args:
            inherent: [0]: function that executes the batch operation, [1]: the text that is in the Apply to

        Returns:

        """
        selected_indexes = self.get_selected_indexes(inherent[1])
        if not selected_indexes:
            parameters.log.info("No valid images selected for batch button")
            return False
        result = inherent[0](self.db, selected_indexes)

        # Update the image frames if a function updates it
        if result:
            if str(inherent[0].__name__) in DatabaseToolsBase.BatchFunctions.update_image_frames_func_names:
                self.image_view.update_image_frames(result)

        parameters.log.info("Applied")
        self.add_db_to_history(str(inherent[0].__name__)+": "+str(selected_indexes))
        self.database_changed(selected_indexes)

    def get_selected_indexes(self, text) -> list[int]:
        match text:
            case "Current Selection":
                return self.selected_images
            case "Visible Images":
                return self.image_view.all_visible_images()
            case "Database":
                return [i for i in range(len(self.db.images))]
        parameters.log.error("Incorrect Combobox selected text")

    @Slot()
    def get_rare_tags(self):
        self.tags_view.rare_tags = self.db.get_rare_tags()


    @Slot()
    def open_popup_window(self):
        if isinstance(self.popup_window,CustomWidgets.ImageWindow):
            if self.popup_window.isVisible():
                self.popup_window.hide()
            elif self.selected_images:
                self.popup_window.update_image(self.db.images[self.selected_images[0]].path)
                self.popup_window.show()
        elif self.selected_images:
            self.popup_window = CustomWidgets.ImageWindow(self.db.images[self.selected_images[0]].path)
            self.popup_window.show()
        else:
            parameters.log.info("No selected image")

    def change_popup_window(self, selected_indexes):
        if isinstance(self.popup_window, CustomWidgets.ImageWindow) and self.popup_window.isVisible():
            if len(selected_indexes) == 1:
                self.popup_window.update_image(self.db.images[selected_indexes[0]].path)
            elif any([x not in self.selected_images for x in selected_indexes]):
                new_indexes = [x for x in selected_indexes if x not in self.selected_images]
                self.popup_window.update_image(self.db.images[new_indexes[-1]].path)
            elif any([x not in selected_indexes for x in self.selected_images]):
                self.popup_window.update_image(self.db.images[selected_indexes[0]].path)

    @Slot()
    def clicked_favourites(self, tag):
        self.tags_view.clicked_favourites(tag)

    @Slot()
    def changed_database_settings(self):
        if isinstance(self.tags_view.image, ImageDatabase):
            self.tags_view.view_image(self.tags_view.image)
        self.add_db_to_history("Changed Database Settings")

    @Slot()
    def frequency_tag_clicked(self, tag):
        all_corresponding_images = [] # list of a tuple corresponding to (db_image_index, model_index)
        for base_index in range(self.image_view.listView_groups.model().rowCount()):
            index = self.image_view.listView_groups.model().index(base_index, 0)
            db_index = self.image_view.listView_groups.model().db_index(index)
            if tag in self.db.images[db_index].get_full_tags():
                all_corresponding_images.append((db_index, index))
        if not all_corresponding_images:
            parameters.log.info("No currently visible images have this tag")
            return False

        self.image_view.apply_selection_gradient([x[1] for x in all_corresponding_images])
        self.image_view.update_selected_images_changed([x[0] for x in all_corresponding_images])

    @Slot()
    def tags_to_remove_frequency_selected(self, info_tuple: tuple[list[str], str]):
        images_index = self.get_selected_indexes(info_tuple[1])
        if not images_index:
            parameters.log.warning("No images were valid for batch modification")
            return False
        if not CustomWidgets.confirmation_dialog(self):
            return False
        for index in images_index:
            self.db.images[index].remove_manual_tags(info_tuple[0])
            self.db.images[index].append_rejected_manual_tags(info_tuple[0])
        self.add_db_to_history("Frequency remove "+str(info_tuple[0])+"on "+info_tuple[1])
        self.database_changed(images_index)

    @Slot()
    def clean_history(self):
        if len(self.db_history) < 2:
            return False
        self.remove_history_starting_from(0)
        self.currently_selected_database = 0
        self.history_buttons.button(0).setChecked(True)
        self.add_db_to_history("Clean history")

    def add_db_to_history(self, short_description="default name") -> bool:
        """

        Args:
            short_description:

        Returns:
            True if the tags view is reset/the selected images indexes are updated, False otherwise

        """
        current_changes = self.db.get_changes(self.db_on_load)

        if self.currently_selected_database != len(self.db_history) and self.history_buttons.checkedId() != len(self.db_history):
            parameters.log.info("Remove newer changes")
            current_id = self.history_buttons.checkedId()
            self.remove_history_starting_from(current_id)
            self.database_tools.scrollAreaWidgetContents_history.update()

        if not current_changes or (len(self.db_history) > 0 and current_changes == self.db_history[self.history_buttons.checkedId()-1][0]):
            parameters.log.info("No changes requires the creation of a return point.")
            return False

        self.db_history.append((current_changes, short_description))
        self.add_history_view(len(self.db_history))
        self.history_buttons.button(len(self.db_history)).setChecked(True)
        self.database_tools.scrollAreaWidgetContents_history.update()

    def add_history_view(self, history_index):
        parameters.log.info(f"history_index: {history_index}")
        self.history_buttons.addButton(QRadioButton(f"{history_index}: {self.db_history[history_index-1][1]}"), id=history_index)
        self.database_tools.scrollAreaWidgetContents_history.layout().insertWidget(history_index,self.history_buttons.button(history_index))

    def remove_history_starting_from(self, history_index):
        """
        Remove all buttons and reference in the history to the database with specified index
        Args:
            history_index:

        Returns:

        """
        for button in self.history_buttons.buttons():
            if self.history_buttons.id(button) > history_index:
                self.database_tools.scrollAreaWidgetContents_history.layout().removeWidget(button)
                self.history_buttons.removeButton(button)
                button.hide()
                button.destroy()
        for k in reversed(range(history_index, len(self.db_history))):
            #self.db_history = self.db_history[:history_index+1]
            del self.db_history[k]
        parameters.log.info("Correct length of button group and db_history: "+str(len(self.db_history)+1==len(self.history_buttons.buttons())))

    @Slot()
    def change_to_history(self, history_index):
        parameters.log.info(f'selected history index: {history_index}')
        self.save_image()
        current_changes = self.db.get_changes(self.db_on_load)
        if all([current_changes != self.db_history[k][0] for k in range(len(self.db_history))]):
            self.add_db_to_history("Recent database when selecting older one")
        # selected the most recent database
        if history_index <= 0:
            self.db = copy.deepcopy(self.db_on_load)
            self.image_view.db = self.db
            self.database_tools.db = self.db
            self.currently_selected_database = 0
            self.image_view.history_changed()
            self.database_tools.init_tags_logic()
            self.selected_images_changed(self.selected_images, history=True)
            return
        self.db = copy.deepcopy(self.db_on_load)
        self.image_view.db = self.db
        self.database_tools.db = self.db
        self.db.apply_changes(self.db_history[history_index-1][0])
        self.currently_selected_database = history_index
        self.image_view.history_changed()
        self.database_tools.init_tags_logic()
        self.selected_images_changed(self.selected_images, history=True)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_S and QtCore.Qt.KeyboardModifier.ControlModifier in event.modifiers():
            # CTRL+S: Save Database
            self.save_database()
        elif event.key() == QtCore.Qt.Key.Key_Right and self.image_view.stackedWidget.currentIndex()==1 and self.focusWidget() != self.tags_view.lineEdit_add_tags:
            # CTRL+Next: Next image in single view
            self.image_view.next_single_image()
        elif event.key() == QtCore.Qt.Key.Key_Left and self.image_view.stackedWidget.currentIndex()==1 and self.focusWidget() != self.tags_view.lineEdit_add_tags:
            # CTRL+Prev: Prev image in single view
            self.image_view.prev_single_image()
        elif event.key() == QtCore.Qt.Key.Key_C and QtCore.Qt.KeyboardModifier.ControlModifier in event.modifiers() and self.selected_images:
            # CTRL+C: Copy the current full tags in the order that is visible
            self.tags_view.copy_tags_to_clipboard()
        else:
            super().keyReleaseEvent(event)
