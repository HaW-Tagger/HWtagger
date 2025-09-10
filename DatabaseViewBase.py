import copy
import os
import time
import webbrowser
import subprocess
import enum
import datetime
import concurrent.futures
from collections import Counter

import PySide6.QtGui as QtGui
from PySide6.QtWidgets import QWidget, QCompleter, QStyle, QSizePolicy, QSplitter,QHBoxLayout, QLabel, QColorDialog,\
    QVBoxLayout, QDialog, QPushButton, QLineEdit, QStackedWidget, QButtonGroup, QRadioButton, \
        QScrollArea,QAbstractItemView,QTreeView, QApplication
from PySide6.QtGui import QPixmap, QStandardItem, QBrush
import PySide6.QtCore as QtCore
from PySide6.QtCore import Slot, QStringListModel, QSize, Signal

import CustomWidgets
from classes.class_database import Database
from classes.class_image import *
import classes.class_tree_filter as TreeClass

from interfaces import databaseToolsBase, imageViewBase, tagsViewBase, rectangleTagsBase
from resources import parameters, tag_categories
from tools import files
from CustomWidgets import confirmation_dialog, InputDialog, CheckComboBox

from PIL import Image
from clip import tokenize

wordlist = QStringListModel()
tags_wordlist = set([tag for tag, freq in tag_categories.DESCRIPTION_TAGS_FREQUENCY.items() if int(freq) > 50] + list(
    tag_categories.COLOR_DICT.keys()))

# order the tags by frequency, any unknown or low frequency tags are added at the end
ordered_tags = []
if (parameters.PARAMETERS["sort_autocompletion_by_frequency"]
    # the tag_frequency was generated using the the checkpoint data (before most checks in May 2025) 
    and os.path.exists(os.path.join(parameters.MAIN_FOLDER, "resources/tag_frequency.txt"))):
    with open(os.path.join(parameters.MAIN_FOLDER, "resources/tag_frequency.txt"), 'r') as f:
        ordered_tags = [line.split(":")[0].strip() for line in f]
    ordered_set = set(ordered_tags)
    tags_wordlist = ordered_tags + [tag for tag in tags_wordlist if tag not in ordered_set]
else:
    # default is alphabetical order
    tags_wordlist = sorted(tags_wordlist)

# setup the autocompletion
wordlist.setStringList(tags_wordlist)
completer = CustomWidgets.CustomQCompleter(wordlist)
completer.setModelSorting(QCompleter.ModelSorting.CaseSensitivelySortedModel)
completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
completer.setMaxVisibleItems(10)

w_font_font = parameters.PARAMETERS['font_name'] 
w_font_size = int(parameters.PARAMETERS['font_size'])
base_font = "font: {w_font_font}; font-size: {w_font_size};"
mini_font = "font: {w_font_font}; font-size: {w_font_size};"

class UniqueTagsView(QtCore.QAbstractListModel):
    def __init__(self, display_tags: TagsList, image: ImageDatabase):
        super().__init__()
        self.display_tags = TagsList(tags=display_tags)
        self.display_tags.priority_sort()
        self.image = image # Only used for the tooltips

    def rowCount(self, parent=None):
        return len(self.display_tags)

    def data(self, index, role):
        tag = self.display_tags[index.row()]
        if role == QtGui.Qt.ItemDataRole.DisplayRole:
            return tag.tag

        if role == QtGui.Qt.ItemDataRole.FontRole:
            font = QtGui.QFont()
            if tag.manual:
                font.setBold(True)
            if tag.rejected:
                font.setStrikeOut(True)
            # todo: uncommon tags
            return font

        if role == QtGui.Qt.ItemDataRole.ForegroundRole:
            red, green, blue, alpha = tag.color
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
            return brush

        if role == QtGui.Qt.ItemDataRole.BackgroundRole and tag.highlight:
            brush = QtGui.QBrush(QtGui.QColor.fromRgb(199,255,255, 20)) # color: Azure (darker shade)
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
                brush = QtGui.QBrush(QtGui.QColor.fromRgb(199, 255, 255, 40))  # color: Azure (darker shade)
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
            #if node in parent_node["children"]:
            #    return self.createIndex(i, 0, parent_node)
            
            # modified to check for exact object identity, prev code above checked content which caused bugs
            for child in parent_node["children"]:
                if child is node:
                    return self.createIndex(i, 0, parent_node)
            

        return QtCore.QModelIndex()

class ConflictCategoryView(QtGui.QStandardItemModel):
    # a model that displays a list of conflicting categories, the user can select which one to discard
    # a model with two columns, each row is a pair of conflicting categories, the user can select 
    # one of the two categories to discard and the model will return a list of selected categories
    def __init__(self, conflicts=[("leotard", "swimsuit")]):
        super().__init__()
        self.conflicts = conflicts
        self.setHorizontalHeaderLabels(['Category A', 'Category B'])
        self.items = []  # Store (left_item, right_item) pairs
        for (left, right) in self.conflicts:
            def make_item(option):
                category_text = ", ".join(option) if isinstance(option, tuple) else option
                item = QtGui.QStandardItem(category_text)
                item.setCheckable(True)
                item.setEditable(False)
                return item
            
            left_item = make_item(left)
            right_item = make_item(right)
            
            self.appendRow([left_item, right_item])
            self.items.append((left_item, right_item))
        # Connect exclusivity logic
        self.itemChanged.connect(self._on_item_changed)
        
    def _on_item_changed(self, changed_item):
        # Find the row that was changed
        for left_item, right_item in self.items:
            if changed_item is left_item and changed_item.checkState() == QtCore.Qt.Checked:
                right_item.setCheckState(QtCore.Qt.Unchecked)
            elif changed_item is right_item and changed_item.checkState() == QtCore.Qt.Checked:
                left_item.setCheckState(QtCore.Qt.Unchecked)
            
    def get_selected_categories(self):
        """Returns a list of tuples (1st discarded, 2nd kept), or None if undecided."""
        selections = []
        for left_item, right_item in self.items:
            if left_item.checkState() == QtCore.Qt.Checked:
                selections.append((left_item.text(), right_item.text()))
            elif right_item.checkState() == QtCore.Qt.Checked:
                selections.append((right_item.text(), left_item.text()))
            else:
                pass
        return selections

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
            full_tags_model = UniqueTagsView(self.rectangle_data.get_full_tags(), ImageDatabase())
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
            full_tags_model = UniqueTagsView(self.rectangle_data.get_full_tags(), ImageDatabase())
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

def untagged_potential_characters(tag_list):
    # here we list potentially untagged characters with their semi-unique identifiers,
    # the actual recomendation system is in the recommendation system, and this is a way to 
    from resources import minorChar_conflictString
    char_list = minorChar_conflictString.char_list
    
    return sum([1 for (char, attribute_tags) in char_list if all([tag in tag_list for tag in attribute_tags])])

def deprecation_count(tag_list):
    return sum([1 for tag in tag_list if tag in tag_categories.DEPRECIATED])

class SortType(enum.Enum):
    # add sort name and the sort function here to add sort method to ui

    # Name, function, Tooltip description, Tooltip attribute
    ORDER_ADDED =  "Order Added", lambda x: int(x.order_added), "Order Added", ""
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
    # sort by group then size, so smaller images are at the end
    SIMILARITY_GROUP = "Similarity", lambda x: (x.similarity_group, x.image_height), "Other", "similarity_probability" 
    BRIGHTNESS_VALUE = "Brightness", lambda x: x.get_brightness(), "Other", "brightness_value"
    AVERAGE_PIXEL = "Average pixel", lambda x: x.get_average_pixel(), "Other", "average_pixel"
    CONTRAST_COMPOSITION = "Contrast", lambda x: x.get_contrast_composition(), "Other", "contrast_comp"
    UNDERLIGHTING_COMPOSITION = "Underlighting", lambda x: x.get_underlighting(), "Other", "underlighting"
    GRADIENT_COMPOSITION = "Gradient", lambda x: x.get_gradient(), "Other", "gradient", ""
    RECTANGLES_COUNT = "Rectangles Count", lambda x: len(x.rects), "Other"
    
    DEPRECIATED_TAG_COUNT = "Depreciated tag count", lambda x: deprecation_count(x.full_tags), "Other", ""
    UNTAGGED_POTENTIAL_CHAR = "Untagged Potential Characters", lambda x: untagged_potential_characters(x.full_tags), "Other", ""
    CHARACTER_COUNT = "Named characters count", lambda x: x.get_character_count(), "Other", ""
    CHATACTER_NUMBER_COUNT = "# of implied characters", lambda x: x.get_implied_character_count(), "Other", ""
    RARE_TAGS_COUNT = "Rare tags count", lambda x: x.get_rare_tags_count(), "Other", ""
    UNKNOWN_TAGS = "Unknown tags", lambda x: x.get_unknown_tags_count(), "Other", ""
    
    DEVELOPER_VALUE = "Developer Value",  lambda x: x.get_dev_value(), "For Developer, used to sort numerical values", ""

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
    # the class obj that holds the many images in the main and sub view, page feature is implimented
    def __init__(self, images_dict, current_page = 0, items_per_page = 100):
        super().__init__()
        self.images_dict = images_dict
        self.items_per_page = items_per_page
        self.current_page = current_page # page is 0 based index in the code and 1 based on the interface
        self.total_count = len(self.images_dict.keys()) # synonymous with total item count
        
        # this stores the ordered indicies to show users, also stores the current "view" ignoring pages
        # the page feaure is sampling spaced slices from this list
        self.curr_list_order = [(img_idx, 0) for img_idx in self.images_dict.keys()] 
        
        self.max_pages = self.get_last_page()
        self.page_first_item, self.page_last_item = self.get_first_and_last_indicies()
        self.row_count = self.page_last_item - self.page_first_item
        self.add_index_items_to_view(self.curr_list_order)    
    
    def get_first_and_last_indicies(self):
        #parameters.log.info(f"curr page {self.current_page}")
        return self.current_page * self.items_per_page, min((self.current_page + 1) * self.items_per_page, self.total_count)
    
    def get_last_page(self):
        return math.floor(self.total_count/self.items_per_page)
    
    def rowCount(self, parent=None):
        return self.row_count
    
    def add_index_items_to_view(self, index_list, attribute=""):
        # index list is a list of tuples storing the coordinates, the column is 0 so all entries are (n, 0)
        # n is the element in the main db that gets loaded
        for i in range(self.page_first_item, self.page_last_item):
            x = index_list[i]
            item = self.create_item(x[0], attribute)
            self.appendRow(item)
    
    def load_page(self, page_num, attribute=""):
        # called when we move across different pages, we clear the content and replace with items on the new page
        self.beginResetModel()
        self.clear()
        self.current_page = page_num
        self.total_count = len(self.curr_list_order)
        self.page_first_item, self.page_last_item = self.get_first_and_last_indicies()
        self.row_count = self.page_last_item - self.page_first_item
        self.add_index_items_to_view(self.curr_list_order, attribute)
        self.endResetModel()
    
    def apply_order(self, list_sort, attribute=""):
        """
        list_sort: a sorted list storing tuple (db_index, numerical val used by sort)
        
        this is called when the user searched or filtered groups, then we get a list of indicies that matches the criteria
        then the curr_list_order is updated and the view is the filtered version. 
        Moving pages within the same filter condtion, is handled above
        """ 
        
        self.curr_list_order = list_sort
        self.total_count = len(list_sort)
        self.max_pages = self.get_last_page()
        self.current_page = 0
        self.load_page(self.current_page, attribute)

    def get_db_indices_of_view(self):
        # curr_list_order stores idx and value used to sort as a tuple
        return [x[0] for x in self.curr_list_order]
    
    def get_db_indices_of_curr_page(self):
        # first value of the tuple is the img index in the database
        return [self.curr_list_order[i][0] for i in range(self.page_first_item, self.page_last_item)]
    
    def create_item(self, image_index, attribute=""):
        # image index is a list of sorted indicies to sample from the main database
        # attribute contains the calculated (similarity, brightness, etc) values, when those are selected for the sorting type
        item = QStandardItem(str(image_index))
        item.setIcon(self.images_dict[image_index][0])
        if os.path.exists(self.images_dict[image_index][1].path):
            date_modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.images_dict[image_index][1].path))
            date_created = datetime.datetime.fromtimestamp(os.path.getctime(self.images_dict[image_index][1].path))
        else:
            date_modified = "DISCARDED"
            date_created = "DISCARDED"
        if parameters.PARAMETERS["database_view_tooltip"]:
            if attribute and hasattr(self.images_dict[image_index][1], attribute):
                tooltip = f'<b>{getattr(self.images_dict[image_index][1], attribute)}</b>\npath: {self.images_dict[image_index][1].path}, width: {self.images_dict[image_index][1].image_width}, height: {self.images_dict[image_index][1].image_height}, date modified: {date_modified}, date created: {date_created}<br><img src="{self.images_dict[image_index][1].path}" width={768 * self.images_dict[image_index][1].image_ratio} height={768}>'
            else:
                tooltip = f'<b>path: {self.images_dict[image_index][1].path}, width: {self.images_dict[image_index][1].image_width}, height: {self.images_dict[image_index][1].image_height}, date modified: {date_modified}, date created: {date_created}, </b><br><img src="{self.images_dict[image_index][1].path}" width={768 * self.images_dict[image_index][1].image_ratio} height={768}>'
            item.setToolTip(tooltip)
        return item

    def data(self, index, role):
        # modifying color when clicked and showing tooltip rules
        if role == QtGui.Qt.ItemDataRole.DecorationRole:
            return self.item(index.row()).data(QtGui.Qt.ItemDataRole.DecorationRole)
        if role == QtGui.Qt.ItemDataRole.ToolTipRole:
            return self.item(index.row()).data(QtGui.Qt.ItemDataRole.ToolTipRole)
        if role == QtGui.Qt.ItemDataRole.BackgroundRole:
            return self.item(index.row()).data(QtGui.Qt.ItemDataRole.BackgroundRole)

class DatabaseToolsBase(QWidget, databaseToolsBase.Ui_Form):
    clickedBatchFunction = Signal(tuple)
    clickedPopupWindow = Signal()
    clickedFavourites = Signal(TagElement)
    clickedReplace = Signal(tuple)
    frequencyTagSelected = Signal(str)
    removeTagsFrequencySelected = Signal(tuple)
    clickedSaveDatabase = Signal()
    clickedGenerateReport = Signal()
    
    get_curr_group = Signal()
    checkedHighlightFunction = Signal(tuple)
    clicked_manual_info = Signal()
    clicked_copy_to_clipboard = Signal(tuple)
    clickedPrintImageInfo = Signal()
    clicked_recommendation_info = Signal()
    clicked_discard_tag_group = Signal(tuple)
    
    def __init__(self, db: Database):
        super().__init__()
        self.setupUi(self)
        self.db = db
        # Output widget
        self.widget_to_output.set_trigger_tags(", ".join(self.db.get_triggers("main_tags")), 
                                               ", ".join(self.db.get_triggers("secondary_tags")))
        self.widget_to_output.createTxtFiles.connect(self.create_txt_files_button)
        self.widget_to_output.createJsonTagFile.connect(self.create_meta_cap_button)
        self.widget_to_output.createSampleToml.connect(self.create_sample_toml_button)
        self.widget_to_output.createJsonLFile.connect(self.create_jsonl_button)

        self.widget_to_output.editedMainTriggerTag.connect(self.update_main_trigger_tags)
        self.widget_to_output.editedSecondaryTriggerTag.connect(self.update_secondary_trigger_tags)

        self.widget_to_output.copyTagsToClipboard.connect(lambda: self.clicked_copy_to_clipboard.emit((
            self.widget_to_output.use_trigger_tags(),
            self.widget_to_output.use_token_separator(),
            self.widget_to_output.use_aesthetic_score(),
            self.widget_to_output.use_sentence(),
            self.widget_to_output.use_aesthetic_score_in_trigger_section(),
            self.widget_to_output.use_random_shuffle()
        )))
        
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

        # Other Batches
        self.pushButton_export_images.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.export_images, self.comboBox_selection.currentText())))
        self.pushButton_discard_image.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.discard_images, self.comboBox_selection.currentText())))
        self.pushButton_open_in_default_program.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.open_default_program, self.comboBox_selection.currentText())))

        self.pushButton_flip_horizontally.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.flip_horizontally, self.comboBox_selection.currentText())))

        self.pushButton_remove_single_source_autotags.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.remove_single_source_autotags, self.comboBox_selection.currentText())))
        self.pushButton_remove_rejected_manual.clicked.connect(lambda: self.clickedBatchFunction.emit((self.BatchFunctions.remove_rejected_manuals, self.comboBox_selection.currentText())))
        
        
        self.comboBox_selection.addItems(["Current Selection", "Visible Images (Current Page)", "Visible Images (All Pages)", "Database"])
        self.comboBox_selection.setCurrentIndex(0)

        # Popup Window
        self.pushButton_popup_image.clicked.connect(lambda: self.clickedPopupWindow.emit())

        # Favourites
        self.init_favourites()
        self.treeView_favourites.clicked.connect(self.clicked_favourites)
        self.lineEdit_edit_favourites.returnPressed.connect(self.edit_favourites)

        # Replace
        self.replace_lines: list[QWidget] = []
        base_replace_layout = QVBoxLayout()
        add_replace_line_button = QPushButton("Add replace line")
        remove_replace_line_button = QPushButton("Remove last replace lines")
        add_replace_line_button.clicked.connect(self.create_replace_line)
        remove_replace_line_button.clicked.connect(self.remove_last_replace_line)
        base_replace_layout.addWidget(add_replace_line_button)
        base_replace_layout.addWidget(remove_replace_line_button)
        self.scrollAreaWidgetContents.setLayout(base_replace_layout)
        self.pushButton_replace.clicked.connect(self.replace_tags)

        # Tags Frequency
        self.tag_freq_group = "All"
        self.pushButton_refresh_tags_frequency.clicked.connect(self.refresh_tags_frequency)
        for category in ["ALL", "UNKNOWN"] + list(tag_categories.TAG_CATEGORIES.keys()):
            self.comboBox_frequency_sort.addItem(category)
        self.comboBox_frequency_sort.currentTextChanged.connect(self.refresh_tags_frequency)
        self.lineEdit_tag_frequency_search.returnPressed.connect(self.refresh_tags_frequency)
        self.listView_tags_frequency.doubleClicked.connect(self.tag_from_tags_frequency_selected)
        self.pushButton_remove_tags_from_frequency_batch.clicked.connect(self.remove_tags_from_frequency)

        view_options = ["Current Selection", "Visible Images (Current Page)", "Visible Images (All Pages)", "Database"]
        self.comboBox_batch_selection_frequency.addItems(view_options)
        self.comboBox_batch_selection_frequency.setCurrentIndex(0)

        # misc features tabs options
        # highlight section, emits a tuple of tuple, first element is the checkbox, second is the value
        def emit_highlight_state():
            self.checkedHighlightFunction.emit(
                ((self.checkBox_highlight1.isChecked(), self.comboBox_sources1.currentText()),
                (self.checkBox_highlight2.isChecked(), self.doubleSpinBox_value2.value()),
                (self.checkBox_highlight3.isChecked(), self.spinBox_tokencount3.value()))
            )
        self.checkBox_highlight1.stateChanged.connect(emit_highlight_state)
        self.comboBox_sources1.currentTextChanged.connect(emit_highlight_state)
        self.checkBox_highlight2.stateChanged.connect(emit_highlight_state)
        self.doubleSpinBox_value2.valueChanged.connect(emit_highlight_state)
        self.checkBox_highlight3.stateChanged.connect(emit_highlight_state)
        self.spinBox_tokencount3.valueChanged.connect(emit_highlight_state)
        self.pushButton_print_manual.clicked.connect(lambda: self.clicked_manual_info.emit())
        self.pushButton_print_recommendations.clicked.connect(lambda: self.clicked_recommendation_info.emit())
        self.pushButton_print_curr_img_data.clicked.connect(lambda: self.clickedPrintImageInfo.emit())
        
        # Notes and Reports:
        self.plainTextEdit_notes.setPlainText(self.db.note)
        self.plainTextEdit_reports.setPlainText(self.db.report)
        self.plainTextEdit_notes.textChanged.connect(self.note_changed)
        self.plainTextEdit_reports.textChanged.connect(self.report_changed)
        
        self.pushButton_generate_report.clicked.connect(lambda: self.clickedGenerateReport.emit())
        self.pushButton_tfidf_comp.clicked.connect(self.print_tfidf_comparison)

        # Tag category filter
        self.comboBox_selection_2.addItems(view_options)
        self.comboBox_selection_2.setCurrentIndex(0)
        self.init_category_conflicts()
        self.pushButton_discardTagGroup.clicked.connect(self.discard_tag_group)
        
        self.load_note_to_self()
    
    def init_category_conflicts(self):
        # add rows with opposing category, ex leotard vs swimsuit, to the tree view and 
        # make them selectable so the user can decide to discard an entire group of tags based off keywords/partal tag match
        
        # list of conflicting categories, 1st vs 2nd, category can be a tuple of keywords
        # when the ui loads, the 2nd category expand to fill space, so put long categories in the 2nd category
        # we detect them via split(" ") so be careful with tags like 1other
        
        # we will make a tree view with the categories and the user can select which one to discard
        from resources import minorChar_conflictString
        self.treeView_category_conflicts.setModel(ConflictCategoryView(minorChar_conflictString.conflict_categories))
        
    
    def discard_tag_group(self):
        # we get the list of rejected categories, then emit a signal with the list
        # so that those categories are cleaned up in the main databaseView
        rejected_categories = self.treeView_category_conflicts.model().get_selected_categories()
        selected_indexes = self.comboBox_selection_2.currentText() 
        self.clicked_discard_tag_group.emit((rejected_categories, selected_indexes))
    
    def load_note_to_self(self):
        
        note_file = os.path.join(resources.parameters.MAIN_FOLDER, 'resources/noteToSelf.txt')
        note = ""
        if os.path.exists(note_file):
            with open(note_file, 'r') as f:
                note = f.read()
            
        self.plainTextEdit_noteToSelf.setPlainText(note)
    
    @Slot()
    def refresh_tags_frequency(self):
        self.get_curr_group.emit() # updates tag_freq_group
        curr_group = self.tag_freq_group
        parameters.log.info(f"Refreshing tags frequency for group {curr_group}")
        if curr_group != "All":
            frequency = self.db.get_frequency_of_all_tags(curr_group)
        else:
            frequency = self.db.get_frequency_of_all_tags()
        category = self.comboBox_frequency_sort.currentText()
        search_string = self.lineEdit_tag_frequency_search.text().strip().lower()
        
        if category == "UNKNOWN":
            frequency = [tag_tuple for tag_tuple in frequency if tag_tuple[0] not in tag_categories.COLOR_DICT.keys()]
        elif category != "ALL": # filter by category
            frequency = [tag_tuple for tag_tuple in frequency if category in tag_categories.TAG2CATEGORY.get(tag_tuple[0], [])]
        
        
        if search_string: # filter by string
            frequency = [tag_tuple for tag_tuple in frequency if search_string in tag_tuple[0]]
  
        refresh_model = FrequencyTagsView(frequency)
        self.listView_tags_frequency.setModel(refresh_model)
        # Enable multiple selection with Ctrl+click
        self.listView_tags_frequency.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    @Slot()
    def tag_from_tags_frequency_selected(self, index):
        if not index.isValid():
            return False
        tag = self.listView_tags_frequency.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
        self.frequencyTagSelected.emit(tag)

    @Slot()
    def remove_tags_from_frequency(self):
        selected_indexes = self.listView_tags_frequency.selectionModel().selectedIndexes()
        
        # old code deleted all tags
        #tags_to_remove = [self.listView_tags_frequency.model().data(
        #    self.listView_tags_frequency.model().index(model_index),
        #    QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
        #    for model_index in range(self.listView_tags_frequency.model().rowCount())]
        if not selected_indexes:
            confirmation = CustomWidgets.confirmation_dialog(self, "Do you wish to remove all tags from the view?")
            if not confirmation:
                return False
            # removing all tags in the lists from the current view (group)
            tags_to_remove = [self.listView_tags_frequency.model().data(
                self.listView_tags_frequency.model().index(model_index),
                QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
                for model_index in range(self.listView_tags_frequency.model().rowCount())]
        else:
            tags_to_remove = [
                self.listView_tags_frequency.model().data(
                    index, QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
                for index in selected_indexes
            ] 

        self.removeTagsFrequencySelected.emit((tags_to_remove, self.comboBox_batch_selection_frequency.currentText()))
    @Slot()
    def create_replace_line(self):
        one_widget = QWidget()
        h_layout = QHBoxLayout()
        first_line_edit = QLineEdit()
        first_line_edit.setCompleter(completer)
        h_layout.addWidget(first_line_edit)
        h_layout.addWidget(QLabel("->"))
        second_line_edit = QLineEdit()
        second_line_edit.setCompleter(completer)
        h_layout.addWidget(second_line_edit)
        one_widget.setLayout(h_layout)
        self.replace_lines.append(one_widget)
        self.scrollAreaWidgetContents.layout().insertWidget(0, one_widget)

    @Slot()
    def remove_last_replace_line(self):
        if len(self.replace_lines) < 1:
            parameters.log.info("No replace line to remove")
            return False
        x = self.replace_lines.pop(-1)
        self.scrollAreaWidgetContents.layout().removeWidget(x)
        x.hide()
        x.destroy()

    @Slot()
    def replace_tags(self):
        if len(self.replace_lines) < 1:
            parameters.log.info("No replacement line created")
            return False
        result = defaultdict(lambda: {"from_tags":[], "to_tags":[]})
        for index, line in enumerate(self.replace_lines):
            from_tags = [tag.strip() for tag in line.layout().itemAt(0).widget().text().split(',') if tag != ""]
            to_tags = [tag.strip() for tag in line.layout().itemAt(2).widget().text().split(',') if tag != ""]
            if not from_tags and not to_tags:
                parameters.log.info("Blank replace line")
                continue
            result[index]["from_tags"] = from_tags
            result[index]["to_tags"] = to_tags
        self.clickedReplace.emit((result, self.comboBox_selection.currentText()))

    def init_favourites(self):
        favourites = TagsList(tags=files.get_favourites(), name="Favourites")
        
        blank_image = ImageDatabase()
        fav_dict = defaultdict(lambda: TagsList())
        used = []
  
        for fav in favourites:
            if fav in tag_categories.TAG2SUB_CATEGORY_EXCLUSIVE:
                used.append(fav)
                subcategories = tag_categories.TAG2SUB_CATEGORY_EXCLUSIVE[fav]
                # the character list is long so we try to use any 
                # that's not in known_characters + minor_character list

                if len(subcategories) > 1:
                    # filter characters from large general groups
                    new_subcategories = [subcat for subcat in subcategories 
                                     if "CHARACTER_MINOR" not in subcat and "KNOWN CHARACTERS" not in subcat]
                    
                    rem_repl = ("removal", "replace", "remove")
                    non_removal_categories = [subcat for subcat in subcategories if not subcat.lower().endswith(rem_repl)]
                    if len([sc for sc in subcategories if sc in non_removal_categories]):
                        new_subcategories = non_removal_categories
                    
                    
                    if "COSPLAY_LIST" in new_subcategories:
                        new_subcategories = ["COSPLAY_LIST"]
                    
                    
                    if new_subcategories:
                        subcategories = new_subcategories
                
                
                for sub_category in subcategories:
                    fav_dict[sub_category] += fav
                  
        favourites -= used
        
            
        # here we reorder the fav list to be in alphabetical order of tag group, then sub group
        sub_categories = fav_dict.keys()
        sorted_sub_categories = []
        # technically the order is defined by which category showed up first so the main category might
        # not be sorted properly, but it's not a big deal because sub categories are sorted
        for _, sub_cat_data in tag_categories.TAG_CATEGORIES.items():
            sub_cat_names = sub_cat_data.keys()
            # get all subcategories in the current main category that should be used in favourites
            used_subcat = [scn for scn in sub_cat_names if scn in sub_categories]
            sorted_sub_categories.extend(sorted(used_subcat))

        # we make a new ordered dict with sorted values, and add the "other" category for the leftover tags
        ordered_fav_dict = dict()
        for sub_category in sorted_sub_categories:
            
            ordered_fav_dict[sub_category] = fav_dict[sub_category]
        if favourites:
            ordered_fav_dict["Other"] = TagsList(tags=favourites.tags)
        
        # here we define the display properties
        for _, fav_list in ordered_fav_dict.items():
            fav_list.init_display_properties()
            fav_list.init_manual_display_properties(False)
            fav_list.init_rejected_display_properties(False)
        fav_model = ConflictTagsView(ordered_fav_dict, blank_image)
        self.treeView_favourites.setModel(fav_model)
        self.treeView_favourites.expandAll()
        
        # collapse all parents with more than 5 children
        #root = self.treeView_favourites.model().index(0, 0, QtCore.QModelIndex())
        collapse_threshold = 5
        for i in range(self.treeView_favourites.model().rowCount()):
            parent_index = self.treeView_favourites.model().index(i, 0, QtCore.QModelIndex())
            parent_node = parent_index.internalPointer()
            # Check if this parent has more than 5 children
            if len(parent_node["children"]) > collapse_threshold:
                # Collapse this parent
                self.treeView_favourites.collapse(parent_index)
        
    @Slot()
    def note_changed(self):
        text = self.plainTextEdit_notes.toPlainText()
        if self.db.note != text:
            self.db.set_notes(text)
        
    @Slot()
    def report_changed(self):
        text = self.plainTextEdit_reports.toPlainText()
        if self.db.report != text:
            self.db.set_reports(text)
    
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
        self.db.set_triggers("main_tags", text)

    @Slot(str)
    def update_secondary_trigger_tags(self, text: str):
        self.db.set_triggers("secondary_tags", text)
        
    @Slot()
    def create_txt_files_button(self):
        if self.widget_to_output.checkBox_current_group.isChecked():
            self.get_curr_group.emit() # updates tag_freq_group
            curr_group = self.tag_freq_group
            parameters.log.info(f"Creating txt files for current group: {curr_group}")
            if curr_group == "All":
                specific_indexes = []
            else:
                hashes = self.db.groups[curr_group]
                specific_indexes = self.db.index_of_images_by_md5(hashes)
        else:
            specific_indexes = []
        
        file_count = len(specific_indexes) if specific_indexes else len(self.db.images)
        parameters.log.info(f"Creating txt files for {file_count} images")
        
        self.db.create_txt_files(
            use_trigger_tags=self.widget_to_output.use_trigger_tags(),
            token_separator=self.widget_to_output.use_token_separator(),
            use_aesthetic_score=self.widget_to_output.use_aesthetic_score(),
            use_sentence=self.widget_to_output.use_sentence(),
            sentence_in_trigger=self.widget_to_output.use_sentence_in_token_separator(),
            remove_tags_in_sentence=self.widget_to_output.remove_tag_in_sentence(),
            score_trigger=self.widget_to_output.use_aesthetic_score_in_trigger_section(),
            specific_indexes=specific_indexes,
            shuffle_tags=self.widget_to_output.use_random_shuffle()
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
            score_trigger=self.widget_to_output.use_aesthetic_score_in_trigger_section(),
            shuffle_tags=self.widget_to_output.use_random_shuffle()
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
            score_trigger=self.widget_to_output.use_aesthetic_score_in_trigger_section(),
            shuffle_tags=self.widget_to_output.use_random_shuffle()
        )

    @Slot()
    def create_sample_toml_button(self):
        selected_resolution = self.widget_to_output.toml_resolution()
        
        res_info = self.db.get_resolution_info(selected_resolution)
        self.db.create_sample_toml(res_info[0], res_info[1], res_info[2], prepend_tags=res_info[4], negative_prompts=res_info[3])

    def print_tfidf_comparison(self):
        # calculate the tfidf for the general danbooru tags and the current database, print tags with differing tfidf
        
        self.db.print_tfidf_comparison()

    class BatchFunctions:
        update_image_frames_func_names = ["flip_horizontally"]
        def apply_filter(self, db: Database, image_indexes: list[int]):
            if len(image_indexes) > 0.6*len(db.images):
                db.filter_all()
            else:
                for index in image_indexes:
                    db.images[index].filter()

        def apply_sentence_filter(self, db: Database, image_indexes: list[int]):
            if len(image_indexes) > 0.6*len(db.images):
                db.filter_sentence_all()
            else:
                for index in image_indexes:
                    db.images[index].filter_sentence()

        def auto_tag(self, db: Database, image_indexes: list[int]):
            db.re_call_models(image_indexes, tag_images=True)

        def auto_tag_characters(self, db: Database, image_indexes: list[int]):
            db.call_models([db.images[index].path for index in image_indexes], tag_only_character=True)

        def auto_score(self, db: Database, image_indexes: list[int]):
            db.re_call_models(image_indexes, score_images=True)

        def auto_classify(self, db: Database, image_indexes: list[int]):
            db.call_models([db.images[index].path for index in image_indexes], classify_images=True)

        def cleanup_rejected_manual(self, db: Database, image_indexes: list[int]):
            db.cleanup_images_rejected_tags(image_indexes)

        def refresh_unsafe_tags(self, db: Database, image_indexes: list[int]):
            db.refresh_unsafe_tags(image_indexes)

        def reset_manual_score(self, db: Database, image_indexes: list[int]):
            db.reset_scores(image_indexes)

        def purge_manual(self, db: Database, image_indexes: list[int]):
            db.purge_manual_tags(image_indexes)

        def open_default_program(self, db: Database, image_indexes: list[int]):
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

        def flip_horizontally(self, db: Database, image_indexes: list[int]):
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

        def remove_single_source_autotags(self, db: Database, image_indexes: list[int]):
            parameters.log.info(f"Removing single source autotags with low threashold from {len(image_indexes)} images")
            for index in image_indexes:
                db.images[index].drop_low_single_source_autotags()
        
        
        def discard_images(self, db: Database, image_indexes: list[int]):
            # todo: add a button to return temp_discarded images
            if len(image_indexes) > 1:
                if not CustomWidgets.confirmation_dialog(None, f"You selected {len(image_indexes)} images to discard.\nAre you sure you want to discard them ?\n\nTip: This button is affected by the 'apply to:' setting at the top right of the window."):
                    return False
            files.export_images(
                [db.images[i].path for i in image_indexes if os.path.exists(db.images[i].path)],
                db.folder, "TEMP_DISCARDED"
            )

        def export_images(self, db: Database, image_indexes: list[int]):
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
        
        def remove_rejected_manuals(self, db: Database, image_indexes: list[int]):
            if len(image_indexes) > 1:
                if not CustomWidgets.confirmation_dialog(None, f"You selected {len(image_indexes)} images to remove rejected manual tags.\nAre you sure you want to remove them?"):
                    return False
            removed_tags = Counter()
            for index in image_indexes:
                if db.images[index].rejected_manual_tags:
                    removed_tags.update(db.images[index].rejected_manual_tags.simple_tags())
                    
                    db.images[index].rejected_manual_tags.clear()
                    db.images[index].filter(update_review=True)
            parameters.log.info(f"{sum(removed_tags.values())} tags were removed from rejected_manual")
        
class ImageViewBase(QWidget, imageViewBase.Ui_Form):
    selectedImagesChanges = Signal(list) # list of images index selected
    areDisplayedRectangles = Signal(bool)
    editedRectangle = Signal(tuple) # coordinates (top, left, width, height) and name of the created rect
    group_count_changed = Signal()
    search_sorting_changed = Signal(list)
    
    def __init__(self, db: Database):
        super().__init__()
        self.setupUi(self)

        self.stackedWidget.widget(0).layout().removeWidget(self.listView_groups)
        self.stackedWidget.widget(0).layout().removeWidget(self.listView_other)
        self.stackedWidget.widget(0).layout().removeWidget(self.view_page_interfaces)
        self.other_splitter = QSplitter()
        self.other_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.other_splitter.addWidget(self.listView_groups)
        self.other_splitter.addWidget(self.view_page_interfaces)
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

        # thumbnail size slider
        self.horizontalSlider_thumbnail_size.setMinimum(self.min_image_size)
        if parameters.PARAMETERS["doubling_image_thumbnail_max_size"]:
            self.horizontalSlider_thumbnail_size.setMaximum(self.image_load_size*2)
        else:
            self.horizontalSlider_thumbnail_size.setMaximum(self.image_load_size)
        self.horizontalSlider_thumbnail_size.setValue(self.image_load_size)
        self.horizontalSlider_thumbnail_size.valueChanged.connect(self.slider_thumbnail_size_changed)

        # group names
        self.comboBox_group_name.addItem("All")
        self.comboBox_group_name.addItems(sorted(self.db.get_group_names(), key=str.casefold))
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
        self.checkBox_remove_manual.stateChanged.connect(self.update_sorting)

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
        self.pushButton_deleted_group.clicked.connect(self.delete_group)

        # Single Image View
        self.pushButton_prev_image.clicked.connect(self.prev_single_image)
        self.single_image.leftClickedWithoutRectangle.connect(self.clicked_image_without_rectangle)
        self.pushButton_next_image.clicked.connect(self.next_single_image)
        self.current_edit_rect_name = ""
        self.single_image.rectangleCreated.connect(self.created_rectangle)
        self.checkBox_masking.stateChanged.connect(self.masking_checkbox_clicked)

        # create image objects and stores them, not yet visualized
        self.create_all_images_frames()

        self.pushButton_prev_button.clicked.connect(self.go_to_prev_page)
        self.pushButton_2_next_button.clicked.connect(self.go_to_next_page)
        self.pushButton_3_jump_page_button.clicked.connect(self.jump_to_page)
        
        self.pushButton_prev_button_other.clicked.connect(self.go_to_prev_page_other)
        self.pushButton_2_next_button_other.clicked.connect(self.go_to_next_page_other)
        self.pushButton_3_jump_page_button_other.clicked.connect(self.jump_to_page_other)
        
        parameters.PARAMETERS["view_page_count"]
        model = BaseImageView(self.images_widgets, items_per_page=parameters.PARAMETERS["view_page_count"])
        model_other = BaseImageView(self.images_widgets, items_per_page=parameters.PARAMETERS["view_page_count"])
        
        
        
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
        self.other_view_page_interfaces.hide()
        
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
        temp_search_tags = [] # list of [tag, include or remove from search , exact]
        for tag in search_tags:
            tag = tag.strip()
            if tag: # non empty
                to_add = ([tag], True, False) 
                if to_add[0][0][0] == "-":  # positive
                    to_add = ([to_add[0][0][1:]], False, to_add[2])
                if to_add[0][0][0] == '"' and to_add[0][0][-1] == '"':  # exact
                    to_add = ([to_add[0][0][1:-1]], to_add[1], True)
                if to_add[0][0][0] == "-":  # positive
                    to_add = ([to_add[0][0][1:]], False, to_add[2])
                if '*' in to_add[0][0]:
                    to_add = (to_add[0][0].split('*'), to_add[1], to_add[2])
                temp_search_tags.append(to_add)
        self.current_search_tags = temp_search_tags
        #parameters.log.info(f"search conditions: {self.current_search_tags}")
        self.update_sorting()

    @Slot()
    def update_sorting(self):
        """
        Update the sorting view, and the other view
        """
        current_list_sort = sorted([(x, self.current_sort.sort_function(self.db.images[x])) 
                                    for x in range(len(self.db.images)) 
                                    if self.show_image_in_main_view(x)], 
                                   key=lambda x: x[1], reverse=not self.checkBox_reverse.isChecked())
        
        self.listView_groups.model().apply_order(current_list_sort, self.current_sort.get_attribute())
        self.label_image_view_count.setText(f"{self.listView_groups.model().rowCount()} images")
        
        self.update_page_info()
        self.update_other_view()
        self.update_shown_page(0)
        self.update_shown_page_other(0)
        self.search_sorting_changed.emit(self.current_search_tags)
        
        #parameters.log.info(f"Usort, pix: {self.image_load_size}, and {self.listView_groups.sizeHintForRow(0)}")
        # test code to check scrollsize
        #scrollbar1 = self.listView_groups.verticalScrollBar()
        #parameters.log.info(f"{scrollbar1.maximum()}, {scrollbar1.minimum()}, {scrollbar1.singleStep()}, {scrollbar1.pageStep()}")
        

    @Slot()
    def update_other_view(self):
        """
        Update the other model view
        """
        if self.current_group == "All":
            self.listView_other.hide()
            self.other_view_page_interfaces.hide() 
            return

        # the sort function is an enum that has the basic or lambda functions that returns a numerical value used for the sorting
        current_list_sort = sorted([(x, self.current_sort.sort_function(self.db.images[x])) 
                                    for x in range(len(self.db.images)) 
                                    if self.show_image_in_other_view(x)], 
                                   key=lambda x: x[1], reverse=not self.checkBox_reverse.isChecked())
        
        if len(current_list_sort)==0:
            self.listView_other.hide()
            self.other_view_page_interfaces.hide()  
        else:
            self.listView_other.show()
            self.other_view_page_interfaces.show()
            self.update_page_info_other()
            self.listView_other.model().apply_order(current_list_sort, self.current_sort.get_attribute())
    
    @Slot()
    def go_to_prev_page_other(self):
        curr_page = self.listView_other.model().current_page
        self.update_shown_page_other(curr_page-1)
    @Slot()
    def go_to_next_page_other(self):
        curr_page = self.listView_other.model().current_page
        self.update_shown_page_other(curr_page+1)
         
    @Slot()
    def jump_to_page_other(self):
        # sanity check
        page_num = str(self.lineEdit_Entered_pageNum_other.text())
        if not page_num.isdigit():
            parameters.log.error("Page number is not a valid number")
            return
        page_num = int(page_num)-1
        if not (0 <= page_num <= self.listView_other.model().max_pages):
            parameters.log.error("Page number is out of bounds")
            return
        # jump to page
        self.update_shown_page_other(page_num)
    
    @Slot()
    def go_to_prev_page(self):
        curr_page = self.listView_groups.model().current_page
        self.update_shown_page(curr_page-1)
    @Slot()
    def go_to_next_page(self):
        curr_page = self.listView_groups.model().current_page
        self.update_shown_page(curr_page+1)
         
    @Slot()
    def jump_to_page(self):
        # sanity check
        page_num = str(self.lineEdit_Entered_pageNum.text())
        if not page_num.isdigit():
            parameters.log.error("Page number is not a valid number")
            return
        page_num = int(page_num)-1
        if not (0 <= page_num <= self.listView_groups.model().max_pages):
            parameters.log.error("Page number is out of bounds")
            return
        # jump to page
        self.update_shown_page(page_num)
    
    def update_page_info(self):
        
        # for the main view
        curr_page = self.listView_groups.model().current_page
        max_page = self.listView_groups.model().max_pages
        total_img = self.listView_groups.model().total_count
        start_img_idx, end_img_idx = self.listView_groups.model().get_first_and_last_indicies()
        if start_img_idx == end_img_idx:
            self.label_page_num.setText(f"Page:{curr_page+1}/{max_page+1}, Img:{start_img_idx}~{end_img_idx} out of {total_img}")
        else: 
            self.label_page_num.setText(f"Page:{curr_page+1}/{max_page+1}, Img:{start_img_idx+1}~{end_img_idx} out of {total_img}")
        self.label_image_view_count.setText(f"{end_img_idx-start_img_idx} images") 
        
        #disable buttons if on first or last page
        self.pushButton_prev_button.setEnabled(True)
        self.pushButton_2_next_button.setEnabled(True)
        if curr_page == 0:
            self.pushButton_prev_button.setEnabled(False) 
        if curr_page == self.listView_groups.model().max_pages:
            self.pushButton_2_next_button.setEnabled(False)
        
    def update_page_info_other(self):
        # for the main view
        curr_page = self.listView_other.model().current_page
        max_page = self.listView_other.model().max_pages
        total_img = self.listView_other.model().total_count
        start_img_idx, end_img_idx = self.listView_other.model().get_first_and_last_indicies()
        if start_img_idx == end_img_idx:
            self.label_page_num_other.setText(f"Page:{curr_page+1}/{max_page+1}, Img:{start_img_idx}~{end_img_idx} out of {total_img}")
        else: 
            self.label_page_num_other.setText(f"Page:{curr_page+1}/{max_page+1}, Img:{start_img_idx+1}~{end_img_idx} out of {total_img}")
        
        # disable buttons if on first or last page
        self.pushButton_prev_button_other.setEnabled(True)
        self.pushButton_2_next_button_other.setEnabled(True)
        if curr_page == 0:
            self.pushButton_prev_button_other.setEnabled(False) 
        if curr_page == self.listView_other.model().max_pages:
            self.pushButton_2_next_button_other.setEnabled(False)
            
    @Slot()
    def update_shown_page(self, page_num):
        if page_num < 0:
            parameters.log.info("Cannot go into negative pages")
        elif page_num > self.listView_groups.model().max_pages:
            parameters.log.info("Cannot go farther than this")
        else:
            #parameters.log.info(f"moving to page {page_num+1}")
            self.listView_groups.model().load_page(page_num)
            self.listView_groups.scrollToTop()
            
            self.update_page_info()
        
    @Slot()
    def update_shown_page_other(self, page_num):
        if page_num < 0:
            parameters.log.info("Cannot go into negative pages")
        elif page_num > self.listView_other.model().max_pages:
            parameters.log.info("Cannot go farther than this")
        else:
            #parameters.log.info(f"moving to page {page_num+1}")

            self.listView_other.model().load_page(page_num)
            self.listView_other.scrollToTop()
            self.update_page_info_other()
            
    
    def get_image_tags_and_sentences(self, image_index):
        # returns a list of tags and sentences to be searched
        tag_to_search_through = self.db.images[image_index].get_search_tags(self.checkBox_include_sentence.isChecked())
        if self.checkBox_remove_manual.isChecked():
            tag_to_search_through = tag_to_search_through.difference(self.db.images[image_index].manual_tags)
        if self.checkBox_include_sentence.isChecked():
            tag_to_search_through = tag_to_search_through.union([self.db.images[image_index].sentence_description.sentence])
        return tag_to_search_through
    
    def tag_match_bool(self, tag_to_search_through):
        if self.current_search_tags: # if search tag is not empty, check for match
            if files.loose_tags_check(self.current_search_tags, tag_to_search_through):
                return True
            return False
        return True
    
    def image_is_in_current_group(self, image_index):
        return self.db.images[image_index].md5 in self.db.groups[self.current_group]
    
    def show_image_in_main_view(self, image_index: int):
        # returns the filtred img indicies that needs to be visualized
        if self.current_group == "All" or self.image_is_in_current_group(image_index):
            if self.tag_match_bool(self.get_image_tags_and_sentences(image_index)):
                return True
        return False

    def show_image_in_other_view(self, image_index: int):
        tag_to_search_through = self.get_image_tags_and_sentences(image_index)
        
        if self.image_is_in_current_group(image_index):
            return False
        
        if self.checkBox_toggle_ungrouped_images.isChecked():
            if self.tag_match_bool(tag_to_search_through):
                return True
        else:
            if len(self.db.images[image_index].group_names)==0:
                if self.tag_match_bool(tag_to_search_through):
                    return True
        return False

    @Slot()
    def clicked_images_changed(self):
        view_indices, db_indices = self.get_selected_index_list()
        #parameters.log.info(f"view: {view_indices}, db_index: {db_indices}")
        self.apply_selection_gradient(view_indices)
        self.update_selected_images_changed(db_indices)

    def apply_selection_gradient(self, selected_model_indexes):
        gradient = QtGui.QRadialGradient(0, 20, 100)
        gradient.setColorAt(0, QtCore.Qt.GlobalColor.red)
        gradient.setColorAt(0.2, QtCore.Qt.GlobalColor.yellow)
        gradient.setColorAt(0.4, QtCore.Qt.GlobalColor.green)
        gradient.setColorAt(0.6, QtCore.Qt.GlobalColor.cyan)
        gradient.setColorAt(0.8, QtCore.Qt.GlobalColor.blue)
        gradient.setColorAt(1.0, QtCore.Qt.GlobalColor.magenta)
        brush = QBrush(gradient)
        blank_brush = QBrush(QtGui.QColor(214, 214, 214, 255))
        for base_index in range(self.listView_groups.model().rowCount()):
            index = self.listView_groups.model().index(base_index, 0)
            if index in selected_model_indexes:
                self.listView_groups.model().setData(index, brush, QtGui.Qt.ItemDataRole.BackgroundRole)
            else:
                self.listView_groups.model().setData(index, blank_brush, QtGui.Qt.ItemDataRole.BackgroundRole)

    def update_selected_images_changed(self, selected_indexes):
        """
        Args:
            selected_indexes: indices of the images inside the database images list
        """
        
        if len(selected_indexes) == 1 and self.checkBox_zoom_on_click.isChecked():
            # User selected a single image so we move tab and show the image on zoom mode
            self.stackedWidget.setCurrentIndex(1)
            image = self.db.images[selected_indexes[0]]
            if os.path.exists(image.path):
                self.single_image.update_image(image.path)
                # Do the label
                date_modified = datetime.datetime.fromtimestamp(os.path.getmtime(image.path))
                date_created = datetime.datetime.fromtimestamp(os.path.getctime(image.path))
                self.single_info_label.setText(
                    f'Width: {image.image_width}, Height: {image.image_height}, Date modified: {date_modified}, Date created: {date_created}')
                if image.misc_numerical_types:
                    kv_pair = [(k, v) for k, v in image.misc_numerical_types.items()]
                    parameters.log.info(f"file: {os.path.basename(image.path)}, {kv_pair}")
            
            else:
                self.single_image.update_image("")
                self.single_info_label.setText("Image path doesn't exist")
            self.label_image_md5.setText(f"MD5: {image.md5}, Original MD5: {image.original_md5}")

        else: # go back to multi-image mode
            self.stackedWidget.setCurrentIndex(0)
            
            

        self.single_image.activated_drawing = False # in case of not doing the edit
        self.selectedImagesChanges.emit(selected_indexes)

    def get_selected_index_list(self):
        # return a tuple with 2 lists containing the QmodelIndex obj: 
        # (which contains the indicies of selected images on the page, and the corresponding index in the database)
        selected_view_indicies = self.listView_groups.selectedIndexes()
    
        selected_db_indices = [int(self.listView_groups.model().itemData(index)[0]) for index in selected_view_indicies]
        
        return selected_view_indicies, selected_db_indices
    
    def single_img_move_direction(self, direction=1):
        #direction (int): -1 to move left (back) and 1 to move right (forwards)
        view_indices, db_indices = self.get_selected_index_list()
        curr_page = self.listView_groups.model().current_page
      
        
        if direction==-1 and view_indices[0].row() == 0:
            #handling edgecase for going backwards
            if curr_page == 0: # if we're on page 0, item 0
                parameters.log.info("First image, can't go back")
                return False
            else: # page n, item 0, need to move page and load the next item
                parameters.log.info(f"moving to new page: {curr_page+direction}")
                self.update_shown_page(curr_page+direction)
                self.listView_groups.scrollToBottom()
                row_count = self.listView_groups.model().rowCount()-1
                last_index = self.listView_groups.model().index(row_count, 0)
                self.listView_groups.setCurrentIndex(last_index)
                _, new_db_index = self.get_selected_index_list()
                self.update_selected_images_changed(new_db_index)
                
        elif direction==1 and view_indices[0].row() == self.listView_groups.model().rowCount()-1:
            #handling edgecase for going forwards
            if curr_page == self.listView_groups.model().max_pages: 
                parameters.log.info("Last image, can't go further")
                return False
            else: # page 0~n-1, last item, need to move page and load the next item
                parameters.log.info(f"moving to new page: {curr_page+direction}")
                self.update_shown_page(curr_page+direction)
                first_index = self.listView_groups.model().index(0, 0)
                self.listView_groups.setCurrentIndex(first_index)
                _, new_db_index = self.get_selected_index_list()
                self.update_selected_images_changed(new_db_index)
        else:
            # moving to new image within the same page 
            next_index = self.listView_groups.model().index(
                view_indices[0].row()+direction, 
                view_indices[0].column())
            self.listView_groups.setCurrentIndex(next_index)
            self.clicked_images_changed()
        
    @Slot()
    def prev_single_image(self):  
        self.single_img_move_direction(direction=-1)
        
    @Slot()
    def next_single_image(self):
        self.single_img_move_direction(direction=1)
       
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
        # transfer selected images from group to ungrouped
        if self.current_group == "All":
            parameters.log.info("No group selected.")
            return False
        if len(self.listView_groups.selectedIndexes())==0:
            parameters.log.info("No images selected.")
            return False
        for w_index in self.listView_groups.selectedIndexes():
            image_index = int(self.listView_groups.model().itemData(w_index)[0])
            self.db.remove_image_from_group(self.current_group, image_index)
        self.listView_groups.clearSelection()
        self.update_sorting()

    def update_selected_image_group(self, group_list=[]):
        view_indices, db_indices = self.get_selected_index_list()
        if db_indices:
            self.db.update_image_groups(group_list=group_list, image_indicies=db_indices)
        else:
            parameters.log.info("No image selected")
            

    @Slot()
    def add_selection_to_group(self):
        # transfer selected images from ungrouped to grouped
        if self.current_group == "All":
            parameters.log.info("No group selected.")
            return False
        if len(self.listView_other.selectedIndexes())==0:
            parameters.log.info("No images selected.")
            return False
        for w_index in self.listView_other.selectedIndexes():
            image_index = int(self.listView_other.model().itemData(w_index)[0])
            self.db.add_image_to_group(self.current_group, image_index)
        self.listView_other.clearSelection()
        self.update_sorting()

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
        self.comboBox_group_name.addItem(user_input)
        parameters.log.info(f"New group: {user_input}")
        self.group_count_changed.emit()
        
    @Slot()
    def delete_group(self):
        if self.current_group == "All":
            parameters.log.info("No group selected")
            return False
        if not confirmation_dialog(self):
            return False
        self.db.remove_group(self.current_group)
        current_comb_index = self.comboBox_group_name.currentIndex()
        self.comboBox_group_name.setCurrentIndex(0)
        self.comboBox_group_name.removeItem(current_comb_index)
        self.group_count_changed.emit()


    def create_all_images_frames(self):
        # create pyside's image object, chaches the thumbnailed version for retrieval
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
        # this is not called that often or once
        
        When an image has been changed, permits to recreate the images frames for these specific indexes, todo: currently update them all
        """
        t1=time.time()
        self.create_all_images_frames()
        model = BaseImageView(self.images_widgets, items_per_page=parameters.PARAMETERS["view_page_count"])
        model_other = BaseImageView(self.images_widgets, items_per_page=parameters.PARAMETERS["view_page_count"])
        self.listView_groups.setModel(model)
        self.listView_other.setModel(model_other)
        self.selected_sort_changed(self.comboBox_sort_type.currentText())
        self.listView_groups.verticalScrollBar().setSingleStep(self.listView_groups.sizeHintForRow(0))
        self.listView_other.verticalScrollBar().setSingleStep(self.listView_other.sizeHintForRow(0))
        t2=time.time()
        parameters.log.info(f"time taken to remake image frames: {t2-t1} sec")

    def visible_images_curr_page(self) -> list[int]:
        """
        Returns: list of indices of all images in the current visible page (doesn't include other pages)
        """
        return self.listView_groups.model().get_db_indices_of_curr_page()
    
    def all_visible_images(self) -> list[int]:
        """
        Returns: list of indices of all images that are view-able with the current filter (all pages)
        """
        return self.listView_groups.model().get_db_indices_of_view()


    def visualise_rectangles(self, rects: list[RectElement]):
        """
        Checks for image Zoom mode, then draws any boundary boxes on top of the displayed images 
        Visualise rectangles (if not in single image view emit it: notDisplayedRectangles)
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
    # signals emitted here goes to DatabaseViewBase and routed for database manipulation
    # TagsViewBase --> DatabaseViewBase --> image_view or tags_view
    askForRareTags = Signal()
    visualiseRectangles = Signal(list) # Send a list of all rectangles that should be visible (list of RectElements)
    editRectangleRequested = Signal(str)
    groupInfoChanged = Signal(list)
    RequestRelatedTags = Signal(list) # send a list of md5s and receive a list of manually edited tags
    UpdatedTags = Signal() # send a signal when tags are updated, matters if multiple images are updated at once
    
    
    def __init__(self):
        """
        This stores the tags and other info to be visualized, this shows the tags 
        for one or multiple selction, so the actual database manipulation happens
        in the ImageViewBase class
        """
        super().__init__()
        self.setupUi(self)
        self.image: ImageDatabase = None
        self.group_names = []
        # simple indicator as to if one or multiple images are selected, modified in databaseViewBase
        self.single_image_selected = True
        self.computed_token_dict = {}
        
        #self.pushButton_reload_view.setText("Reload")
        pixmapi = getattr(QStyle.StandardPixmap, "SP_BrowserReload")
        icon = self.style().standardIcon(pixmapi)
        self.pushButton_reload_view.setIcon(icon)
        self.pushButton_reload_view.clicked.connect(self.reload_image)
        
        
        self.tab.layout().removeWidget(self.listView_rejected)
        self.tab.layout().removeWidget(self.widget_sentenceSection)
        self.tab.layout().removeWidget(self.listView_tags)
        self.tab.layout().removeWidget(self.treeView_conflicts)
        self.tab.layout().removeWidget(self.listView_recommendations)

        right_splitter = QSplitter()
        right_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        right_splitter.addWidget(self.treeView_conflicts)
        right_splitter.addWidget(self.listView_recommendations)

        left_splitter = QSplitter()
        left_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        left_splitter.addWidget(self.listView_rejected)
        left_splitter.addWidget(self.listView_tags)
        
        tags_splitter = QSplitter()
        tags_splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        tags_splitter.addWidget(left_splitter)
        tags_splitter.addWidget(right_splitter)

        self.sentence_splitter = QSplitter()
        self.sentence_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.sentence_splitter.addWidget(self.widget_sentenceSection)
        self.sentence_splitter.addWidget(tags_splitter)

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
        rectangle_splitter.addWidget(self.sentence_splitter)

        self.tab.layout().insertWidget(4, rectangle_splitter)

        # remove placeholder and add custom class dropdown
        if self.comboBox_group_items:
            self.tab.layout().removeWidget(self.comboBox_group_items)
            self.comboBox_group_items.deleteLater()
            self.comboBox_group_items = None
            self.comboBox_groups = CheckComboBox([])
            size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.comboBox_groups.setSizePolicy(size_policy)
            self.horizontalLayout_7.insertWidget(0, self.comboBox_groups)
            self.comboBox_groups.dropdown_closed.connect(self.update_combobox_group)
        
        self.comboBox_score_tags.addItem("NONE")
        self.comboBox_score_tags.addItems(tag_categories.QUALITY_LABELS)
        self.comboBox_score_tags.currentTextChanged.connect(self.changed_aesthetic_score)

        # Configs
        self.highlight_tags_str = []
        self.highlight_tags = []
        self.lineEdit_tag_highlight.editingFinished.connect(self.changed_highlight)
        
        # Adding tags
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
        # this is to store and recommend missing manual tags to a similar images (via image similarity)
        self.related_tags = []
        # this is to highlight what was detected when we searched for a tag or partial tag
        self.searched_tags = [] 
        # is a tuple of tuples [condition, value used for filtering]
        self.highlight_criteria = tuple()

        self.listView_tags.keyPressEvent = lambda event: self.on_key_press(event, self.listView_tags)
        self.listView_rejected.keyPressEvent = lambda event: self.on_key_press(event, self.listView_rejected)
        self.listView_recommendations.keyPressEvent = lambda event: self.on_key_press(event, self.listView_recommendations)
        self.treeView_conflicts.keyPressEvent = lambda event: self.on_key_press(event, self.treeView_conflicts)
        self.treeView_conflicts.rightClicked.connect(self.right_clicked_conflicts)

        # Tree View Update
        self.pushButton_refresh_tree.clicked.connect(self.refresh_tree_clicked)
   
    def print_widget_info(self, widget):
        parent = widget.parentWidget()
        layout = parent.layout() if parent else None
        parent_name = parent.objectName() if parent else "N/A"
        layout_name = layout_name.objectName() if layout else "N/A"
        parameters.log.info(f"Widget {widget.objectName()} is at {widget.geometry()}")
        parameters.log.info(f"Widget's Parent {parent_name}, layout: {layout_name}")
        
    def update_combobox_group(self):
        groups = self.comboBox_groups.get_selected()
        parameters.log.info(f"update selected, {groups}")
        self.groupInfoChanged.emit(groups)
        if self.image:
            self.view_image(self.image)
        
    def refresh_combobox_group_content(self):
        img_groups = self.image.group_names if self.image else []
        #parameters.log.info(f"refresh, {self.group_names, img_groups}")
        self.comboBox_groups.update_list(self.group_names, img_groups)
            
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

        self.refresh_combobox_group_content()
        
        # Tags Label Updates, show img file info
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

        # setup Rejected tags
        self.image.rejected_tags.init_display_properties()
        self.image.rejected_tags.init_manual_display_properties(self.image.manual_tags+self.image.rejected_manual_tags)
        self.image.rejected_tags.init_rejected_display_properties(True)

        # setup Full Tags
        self.image.full_tags.init_display_properties()
        self.image.full_tags.init_manual_display_properties(self.image.manual_tags+self.image.rejected_manual_tags)
        self.image.full_tags.init_rejected_display_properties(self.image.rejected_tags)
       
        # setup Highlight Tags
        curr_highlight_tags = set(self.highlight_tags)
        
        # display search condition
        if self.searched_tags:
            for search in self.searched_tags:
                if search[2]: # exact match only
                    curr_highlight_tags.add(search[0][0])
                else: # fuzzy search
                    condition_met_tags = [t for t in self.image.full_tags.simple_tags() if search[0][0] in t]
                    curr_highlight_tags.update(condition_met_tags)
        
        # Check for rare tags
        if self.checkBox_highligh_rare_tags.isChecked():
            curr_highlight_tags = curr_highlight_tags.union(self.rare_tags)
        # check for optional coloring requests:
        if self.highlight_criteria:
            results = self.check_highlight_criteria()
            curr_highlight_tags = curr_highlight_tags.union(results)
        # check for any depreciated tags:
        curr_highlight_tags = curr_highlight_tags.union(tag_categories.DEPRECIATED)
            
        if self.highlight_tags_str:
            curr_highlight_tags = curr_highlight_tags.union(self.image.full_tags.loose_match(self.highlight_tags_str))
        
        if parameters.PARAMETERS["highlight_missing_implied_tags"]:
            curr_highlight_tags = curr_highlight_tags.union(self.image.check_missing_implied_tags())
          
        # set highlight property
        self.image.full_tags.init_highlight_display_properties(curr_highlight_tags)
        self.image.rejected_tags.init_highlight_display_properties(curr_highlight_tags)
        
        # Display Rejected and full tags
        rejected_tags_model = UniqueTagsView(self.image.rejected_tags, self.image)
        self.listView_rejected.setModel(rejected_tags_model)
        full_tags_model = UniqueTagsView(self.image.full_tags, self.image)
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


        # Display Sentence and expand or hide section if empty or hide_sentence_in_view is true
        sentence = str(self.image.sentence_description)
        self.plainTextEdit_sentence.setPlainText(sentence)
        #self.sentence_splitter # this contains the widget_sentenceSection
        sizes = self.sentence_splitter.sizes()
        total_height = sum(sizes)
        if sentence or not parameters.PARAMETERS["hide_sentence_in_view"]:
            if sizes[0] == 0:  # If the sentence section is collapsed (size[0] is 0), expand it
                perfered_height = min(200, total_height//2)
                self.sentence_splitter.setSizes([perfered_height, total_height - perfered_height])
        else:
            # Collapse the sentence section by setting its size to 0
            self.sentence_splitter.setSizes([0, total_height])
        
        
        
        
        
        
        # Display Recommendations
        recommendations = image.get_recommendations()
        self.related_tags = []
        if self.image.related_md5s:
            # get all manual tags in related images as it may be relevant
            self.RequestRelatedTags.emit(self.image.related_md5s)
            # self.requested_tags is being updated in the emited slot
            
            new_tags = [t for t in self.related_tags if t not in self.image.full_tags and t not in self.image.rejected_tags]
            recommendations+=new_tags
        
        
        
        
        
        recommendations.init_display_properties()
        recommendation_tags_model = UniqueTagsView(recommendations, self.image)
        if not recommendations:
            self.listView_recommendations.hide()
        else:
            self.listView_recommendations.show()
        
        self.listView_recommendations.setModel(recommendation_tags_model)

        
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
            


    def reload_image(self):
        if self.image:
            self.view_image(self.image)
    
    def check_highlight_criteria(self):
        if self.highlight_criteria:
            res = set()
            for i, (condition, value) in enumerate(self.highlight_criteria):
                
                match i:
                    case 0: # highlight tags with this source
                        if condition:
                            
                            res.update(self.image.auto_tags.get_tags_unique_in(value))
                    case 1: # highlight tags under this confidence
                        if condition:
                            under = self.image.auto_tags.tags_under_confidence(value)
                            over = self.image.auto_tags.tags_over_confidence(value)
                            res.update([t for t in under if t not in over])
                        
                    case 2: # highlight tags with token count above this value
                        if condition:
                            tags = self.image.auto_tags.simple_tags()
                            
                            uncomputed = [t for t in tags if t not in self.computed_token_dict]
                            if uncomputed:
                                tokenized_text = tokenize(uncomputed, context_length=500)
                                for tag, tokens in zip(uncomputed, tokenized_text):
                                    self.computed_token_dict[tag] = len(tokens[tokens.nonzero()[1:-1]])
                             
                            res.update([t for t in tags if self.computed_token_dict[t] >= value])
            return res    
        return []

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
        # we store the string version for loose tag matching later
        self.highlight_tags_str = [t.strip() for t in self.lineEdit_tag_highlight.text().split(",")]
        self.highlight_tags_str = [t for t in self.highlight_tags_str if t]
        self.highlight_tags = TagsList(tags=self.highlight_tags_str, name="highlight_tags")
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
        
        self.image.remove_manual_tags(tag)
        self.image.append_rejected_manual_tags(tag)
        self.UpdatedTags.emit()
        self.view_image(self.image)

    @Slot()
    def rejected_tags_clicked(self, index):
        if not index.isValid():
            return False
        tag = self.listView_rejected.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)

        self.image.remove_rejected_manual_tags(tag)
        self.image.append_manual_tags(tag)
        
        self.UpdatedTags.emit()
        self.view_image(self.image)
    @Slot()
    def recommendations_tags_clicked(self, index):
        if not index.isValid():
            return False
        tag = self.listView_recommendations.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)
        self.image.add_from_recommendation(tag)
        self.UpdatedTags.emit()
        self.view_image(self.image)

    @Slot()
    def right_clicked_conflicts(self):
        index = self.treeView_conflicts.currentIndex()
        if not index.isValid():
            return False
        if not index.parent().isValid():
            self.image.append_resolved_conflict(index.internalPointer()["name"])
            self.UpdatedTags.emit()
            self.view_image(self.image)
            return True
        tag = index.internalPointer()["name"]
        self.image.append_rejected_manual_tags(tag)
        self.UpdatedTags.emit()
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
        self.UpdatedTags.emit()
        self.view_image(self.image)

    @Slot()
    def changed_aesthetic_score(self):
        if isinstance(self.image, ImageDatabase):
            text = self.comboBox_score_tags.currentText()
            if text != "NONE":
                self.image.score_label = TagElement(text)

    @Slot()
    def add_tags(self):
        text = self.lineEdit_add_tags.text()
        tags = [tag.strip() for tag in text.split(",")]
        
        if isinstance(self.image, ImageDatabase) and tags:
            # removal is done automatically
            self.image.append_manual_tags(tags)
            self.UpdatedTags.emit()
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
            
            self.UpdatedTags.emit()
            self.view_image(self.image)

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

class DatabaseViewBase(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        load_wiki_info() #update wiki
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
        self.image_view.search_sorting_changed.connect(self.update_search_sort_condition)
        self.selected_images = []

        self.database_tools.clickedBatchFunction.connect(self.execute_batch_func)

        # Popup Window
        self.database_tools.clickedPopupWindow.connect(self.open_popup_window)
        self.popup_window = None

        # Favourites
        self.database_tools.clickedFavourites.connect(self.clicked_favourites)

        # Ask for rare tags
        self.tags_view.askForRareTags.connect(self.get_rare_tags)

        self.tags_view.RequestRelatedTags.connect(self.get_related_tags)
        
        self.tags_view.UpdatedTags.connect(self.apply_filter_to_selected)
        
        
        self.tags_view.group_names = self.db.get_group_names()
        self.tags_view.groupInfoChanged.connect(self.image_view.update_selected_image_group)
        self.image_view.group_count_changed.connect(self.group_count_changed)
        
        # Replace Button
        self.database_tools.clickedReplace.connect(self.clicked_replace)

        # Frequency
        self.database_tools.frequencyTagSelected.connect(self.frequency_tag_clicked)
        self.database_tools.removeTagsFrequencySelected.connect(self.tags_to_remove_frequency_selected)
        self.database_tools.get_curr_group.connect(self.update_curr_group)

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
        
        # Enable additional options:
        self.database_tools.checkedHighlightFunction.connect(self.highlight_tags)
        
        self.database_tools.clicked_manual_info.connect(self.db.print_db_info)
        self.database_tools.clicked_recommendation_info.connect(self.db.print_unknown_recommendations)
        self.database_tools.clickedPrintImageInfo.connect(self.print_image_info)
        self.database_tools.clicked_copy_to_clipboard.connect(self.copy_tags_to_clipboard)
        
        # new features: reports and discarding tags by group
        self.database_tools.clickedGenerateReport.connect(self.generate_and_fill_report)
        self.database_tools.clicked_discard_tag_group.connect(self.discard_tag_group)
        
    @Slot()
    def save_database(self):
        self.save_image()
        current_changes = self.db.get_changes(self.db_on_load)
        if self.db_last_saved_changes == current_changes:
            parameters.log.info("No changes detected in the database")
            return False
        self.db.save_database()
        self.db_last_saved_changes = current_changes

    def group_count_changed(self):
        self.tags_view.group_names = self.db.get_group_names()
        self.tags_view.refresh_combobox_group_content()

    def database_changed(self, changed_indexes):
        """
        All functions that do any changes to a specific index should report it to this function
        If it applies only to the selected image it's not necessary though
        
        this function also gets any changes from the tags_view -> main view
        if any changes need to happen in the opposite direction, do it before this function
        
        """
        if any(changed_index in self.selected_images for changed_index in changed_indexes):
            self.selected_images_changed(self.selected_images)

    @Slot(list)
    def update_search_sort_condition(self, search_condition:list):
        # search condition is a list of [tag, include or remove from search , exact]
        # we only need to highlight the tags that's in the matching category and not the remove category
        positive_match = []
        for s in search_condition:
            if s[1]:
                positive_match.append(s)
        parameters.log.info("sent new search condition to tags view")
        self.tags_view.searched_tags = positive_match
    
    @Slot(list)
    def selected_images_changed(self, image_indexes, history=False):
        """_summary_

        Args:
            image_indexes (list): list of database indices and updates shown tags based on single or multi-image selection
            history (bool, optional): _description_. Defaults to False.
        """
        if not history:
            self.save_image()
        self.change_popup_window(image_indexes)
        #parameters.log.info(f"selected {image_indexes}")
        if len(image_indexes) == 1:
            self.selected_images = image_indexes
            self.tags_view.view_image(self.db.images[self.selected_images[0]])
            self.tags_view.single_image_selected = True
            self.tags_view.group_names = self.db.get_group_names()
        elif len(image_indexes) > 1: # multi-img selection mode
            self.selected_images = image_indexes
            common_image = self.db.get_common_image(self.selected_images)
            self.tags_view.view_image(common_image)
            self.tags_view.single_image_selected = False
            self.tags_view.group_names = self.db.get_group_names()

    @Slot()
    def apply_filter_to_selected(self):
        # we don't need to do anything if selected imgs is < 2
        if len(self.selected_images) > 1:
            parameters.log.info(f"Multiple Imgs changed, applying filter to {len(self.selected_images)} images")
            for index in self.selected_images:
                self.db.images[index].filter(update_review=True)
                simple = self.db.images[index].get_full_tags().simple_tags()
                
            self.add_db_to_history("Filter applied to "+str(len(self.selected_images)))
            self.database_changed(self.selected_images)
            

    def save_image(self):
        """
        Save any tag modifications made in the tags view back to the database.
        
        This method is called when the user switches between images or performs
        actions that require persisting the current tag changes. It handles both
        single image and multi-image selection scenarios.
        
        For multi-image selections, changes are applied intelligently:
        - Tags added to the common view are added to all selected images
        - Tags removed from the common view are removed from all selected images
        """
        if self.selected_images:# proceed if user has image(s) selected
            current_image = self.tags_view.return_image()
            
            self.db.changed_common_image(current_image, self.selected_images)
            

    @Slot(tuple)
    def execute_batch_func(self, inherent):
        """
        This slot is called to execute the batch functions
        the tuple (len 2) stores a reference to the function that takes the db and image indexes as arguments
        the second element is the text in the combobox, which signify the selection (single image, curr view, all images)

        Args:
            inherent: [0]: function that executes the batch operation, [1]: the text that is in the Apply to

        Returns:

        """
        selected_indexes = self.get_selected_indexes(inherent[1])
        if not selected_indexes:
            parameters.log.info("No valid images selected for batch button")
            return False
        
        result = inherent[0](None, self.db, selected_indexes)

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
            case "Visible Images (All Pages)":
                return self.image_view.all_visible_images()
            case "Visible Images (Current Page)":
                return self.image_view.visible_images_curr_page()
            case "Database":
                return [i for i in range(len(self.db.images))]
        parameters.log.error("Incorrect Combobox selected text")

    @Slot()
    def get_rare_tags(self):
        self.tags_view.rare_tags = self.db.get_rare_tags()

    @Slot()
    def get_related_tags(self, md5s):
        self.tags_view.related_tags = self.db.get_related_tags(md5s)
    
    @Slot()
    def highlight_tags(self, highlight_tuple):
        # we only need to know via the tag groups
        self.tags_view.highlight_criteria = highlight_tuple
        self.tags_view.reload_image()

    @Slot()
    def print_image_info(self):
        print("function called")
        if self.selected_images:
            if len(self.selected_images) > 1:
                parameters.log.info("Multiple images selected, only printing info for the first one")
            self.db.images[self.selected_images[0]].print_image_info()
    
    @Slot()
    def copy_tags_to_clipboard(self, output_widget_checkboxes):
        
        if self.selected_images:
            if len(self.selected_images) > 1:
                parameters.log.info("Multiple images selected, copying tags is only available for a single image")
            elif len(self.selected_images) == 1:
                
                selection = self.selected_images[0]
                
                tags_text = self.db.create_output_text(selection,
                            add_backslash_before_parenthesis= False,
                            token_separator= output_widget_checkboxes[1],
                            keep_tokens_separator= parameters.PARAMETERS["keep_token_tags_separator"],
                            use_trigger_tags= output_widget_checkboxes[0],
                            use_aesthetic_score = output_widget_checkboxes[2],
                            use_sentence = output_widget_checkboxes[3],
                            sentence_in_trigger = False,
                            remove_tags_in_sentence = True,
                            score_trigger = output_widget_checkboxes[4],
                            shuffle_tags=output_widget_checkboxes[5]
                            )
                clipboard = QApplication.clipboard()
                clipboard.setText(tags_text)
                
                parameters.log.info("Copied tags to clipboard")
                """remove_tags_in_sentence, sentence_in_trigger are not used anywhere, idk why
                """
            else:
                parameters.log.info("No images selected")
        else:
            parameters.log.info("No images selected")
    
    @Slot()
    def generate_and_fill_report(self):
        report, _ = self.db.generate_report()
        self.database_tools.plainTextEdit_reports.setPlainText(report)
    
    @Slot(tuple)
    def discard_tag_group(self, discarded_info):
        selection, selected_indexes = discarded_info
        selected_indexes = self.get_selected_indexes(selected_indexes)
        if not selected_indexes:
            parameters.log.info("No valid images selected for batch button")
            return False
        parameters.log.info(f"Discarding {selection} from {len(selected_indexes)} images")
        tag_counter = Counter()
        for image_index in selected_indexes:
            for (discard, keep) in selection:
                # first check if category is a tuple or a string, 
                # for the discard category, soft-reject tags all tags in both rejected and full category 
                # to the secondary_rejected section
                # No action needed for the keep category
                
                # first get all the tags we need for analysis
                manual_tags = self.db.images[image_index].manual_tags
                rejected_manual_tags = self.db.images[image_index].rejected_manual_tags
                full_tags = self.db.images[image_index].get_full_tags().simple_tags()
                rejected_tags = self.db.images[image_index].get_rejected_tags().simple_tags()
                

                # if discard is a tuple, any tag with partial match is discarded
                if "," in discard:
                    discard = tuple(discard.split(","))
                
                if isinstance(discard, tuple):
                    discard_full = [t for t in full_tags if any([d in t.split(" ") for d in discard])]
                    discard_rejected = [t for t in rejected_tags if any([d in t.split(" ") for d in discard])]
                    print(f"discarding {discard_full}")
                else: # str, simple check
                    discard_full = [t for t in full_tags if discard in t.split(" ")]
                    discard_rejected = [t for t in rejected_tags if discard in t.split(" ")]
                
                # here we have tags that were already manually processed, and we don't touch those
                # tags added or added back manually stays
                # tags rejected manually stays rejected
                discard_full = [t for t in discard_full if t not in manual_tags]
                discard_rejected = [t for t in discard_rejected if t not in rejected_manual_tags]
                
                combined_discard = discard_full + discard_rejected
                print(f"rejecting {combined_discard}")
                self.db.images[image_index].append_secondary_rejected(combined_discard)
                tag_counter.update(combined_discard)
            self.db.images[image_index].filter(update_review=True)
        if tag_counter:
            parameters.log.info(f"Discarded The following:")
            for tag, count in tag_counter.most_common():
                parameters.log.info(f"{tag}, {count}")
        self.add_db_to_history("Discard tag group "+str(selection)+"on "+discarded_info[1])
        self.database_changed(selected_indexes)

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
    def clicked_replace(self, replace_info):
        replace_counters = [0,0,0] # [tags added, tags removed, tags replaced]
        selected_indexes = self.get_selected_indexes(replace_info[1])
        if not selected_indexes:
            parameters.log.info("No valid images selected for batch button")
            return False
        parameters.log.info(f"Replacing tags on {len(selected_indexes)} images, Ex ID: {selected_indexes[:max(10, len(selected_indexes))]}")
        
  
        
        for i, image_index in enumerate(selected_indexes):  
            image_changes = False
            for replace_tags in replace_info[0].values():
                from_tags: list[str] = replace_tags["from_tags"]
                to_tags: list[str] = replace_tags["to_tags"]
                
                if not from_tags: # add all to tags
                    self.db.images[image_index].append_manual_tags(to_tags)
                    self.db.images[image_index].remove_rejected_manual_tags(to_tags)
                    replace_counters[0] += 1
                    image_changes = True
                    
                elif not to_tags: # remove all from tags
                    self.db.images[image_index].remove_manual_tags(from_tags)
                    self.db.images[image_index].remove_secondary_tags(from_tags)
                    self.db.images[image_index].append_rejected_manual_tags(from_tags)
                    replace_counters[1] += 1
                    image_changes = True
                    
                elif all(tag in self.db.images[image_index].full_tags for tag in from_tags): # remove from tags and add to tags
                    
                    # we may have scenarios like: "cow, bull" --> "cow" or "autofellatio, fellatio" --> "autofellatio"
                    from_tags_removal = [t for t in from_tags if t not in to_tags]
                    self.db.images[image_index].append_manual_tags(to_tags)
                    self.db.images[image_index].remove_manual_tags(from_tags_removal)
                    # we upgrade secondary_rejected to rejected
                    self.db.images[image_index].secondary_rejected_tags -= from_tags_removal
                    self.db.images[image_index].append_rejected_manual_tags(from_tags_removal)
                    replace_counters[2] += 1
                    image_changes = True
                    
                else:
                    #parameters.log.info(f"Skipping replace on {os.path.basename(self.db.images[image_index].path)}")
                    continue
            
            if image_changes:
                self.db.images[image_index].filter(update_review=True)
        
        
        # update selected images
        self.selected_images = selected_indexes
        if len(selected_indexes) == 1:
            self.tags_view.view_image(self.db.images[self.selected_images[0]])
            self.tags_view.single_image_selected = True
        elif len(selected_indexes) > 1: # multi-img selection mode
            common_image = self.db.get_common_image(self.selected_images)
            self.tags_view.view_image(common_image)
            self.tags_view.single_image_selected = False
        self.tags_view.group_names = self.db.get_group_names()
        
        self.add_db_to_history("Replacing tags")
        # changes in tags view flow back to the database view, so updating tags_view happened before this line
        self.database_changed(selected_indexes)
        self.selected_images_changed(self.selected_images, history=True)
        self.tags_view.reload_image()
     

    @Slot()
    def frequency_tag_clicked(self, tag):
        parameters.log.info(f"Selecting all images with tag {tag}")
        all_corresponding_images = [] # list of a tuple corresponding to (db_image_index, model_index)
        for base_index in range(self.image_view.listView_groups.model().rowCount()):
            index = self.image_view.listView_groups.model().index(base_index, 0)
            db_index = int(self.image_view.listView_groups.model().itemData(index)[0])
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
        
        shown_examples = info_tuple[0][:min(5, len(info_tuple[0]))]
        confirmation = CustomWidgets.confirmation_dialog(self, f"Reject {len(info_tuple[0])} tags from the view with {len(images_index)} images?\n{shown_examples}")
        if not confirmation:
            parameters.log.info("Cancelled operation")
            return False

        # moved confirmation to the databasetool section for better message
        parameters.log.info(f"Removing {len(info_tuple[0])} tags from {len(images_index)} images")
        for index in images_index:
            for tag in info_tuple[0]:
                if tag in self.db.images[index].get_full_tags():
                    self.db.images[index].remove_manual_tags(tag)
                    self.db.images[index].append_rejected_manual_tags(tag)
                elif tag in self.db.images[index].get_rejected_tags(): 
                    # we also want hard reject tags already removed as we might be removing a parent tag and all childs
                    # ex : removing w -> v -> hand gestures
                    self.db.images[index].append_rejected_manual_tags(tag)

        self.add_db_to_history("Frequency remove "+str(info_tuple[0])+"on "+info_tuple[1])
        self.database_changed(images_index)

    def update_curr_group(self):
        self.database_tools.tag_freq_group = self.image_view.current_group
        
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
        return True

    def add_history_view(self, history_index):
        parameters.log.info(f"history_index: {history_index}")
        #parameters.log.info(f"history_buttons_len: {len(self.history_buttons.buttons())}")
        self.history_buttons.addButton(QRadioButton(f"{history_index}: {self.db_history[history_index-1][1]}"), id=history_index)
        self.database_tools.scrollAreaWidgetContents_history.layout().insertWidget(history_index,self.history_buttons.button(history_index))
        #parameters.log.info(f"history_buttons_len: {len(self.history_buttons.buttons())}")

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
            self.selected_images_changed(self.selected_images, history=True)
            return
        self.db = copy.deepcopy(self.db_on_load)
        self.image_view.db = self.db
        self.database_tools.db = self.db
        self.db.apply_changes(self.db_history[history_index-1][0])
        self.currently_selected_database = history_index
        self.selected_images_changed(self.selected_images, history=True)

    def keyReleaseEvent(self, event):
        lineedit_widgets = [self.tags_view.lineEdit_add_tags, self.tags_view.lineEdit_tag_highlight, 
                            self.image_view.lineEdit_tag_search, self.tags_view.plainTextEdit_sentence]
        lineedit_focus = any([widget.hasFocus() for widget in lineedit_widgets])
        
        if event.key() == QtCore.Qt.Key.Key_S and QtCore.Qt.KeyboardModifier.ControlModifier in event.modifiers():
            # CTRL+S: Save Database
            self.save_database()
        elif event.key() in(QtCore.Qt.Key.Key_Right,QtCore.Qt.Key.Key_Left) and lineedit_focus:
            
            super().keyReleaseEvent(event)
        elif event.key() == QtCore.Qt.Key.Key_Right and self.image_view.stackedWidget.currentIndex()==1:
            # right arrow: Next: Next image in single view
            self.image_view.next_single_image()
        elif event.key() == QtCore.Qt.Key.Key_Left and self.image_view.stackedWidget.currentIndex()==1:
            # left arrow: Prev: Prev image in single view
            self.image_view.prev_single_image()
        else:
            super().keyReleaseEvent(event)
