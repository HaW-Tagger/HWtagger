import copy
import os
import webbrowser
import subprocess
import enum
import datetime
import concurrent.futures
from collections import Counter

import PySide6.QtGui as QtGui
from PySide6.QtWidgets import QWidget, QCompleter, QTreeWidgetItem, \
	QListWidgetItem, QTabBar, QSizePolicy, QSplitter, QLayout, QHBoxLayout, QFrame, QCheckBox, QLabel, QGridLayout, \
	QFormLayout, QVBoxLayout, QDialog, QPushButton, QLineEdit, QStackedWidget, QButtonGroup, QRadioButton
from PySide6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QBrush
import PySide6.QtCore as QtCore
from PySide6.QtCore import Slot, QStringListModel, QSize

import CustomWidgets
from classes.class_database import Database
from classes.class_image import ImageDatabase

from interfaces import databaseToolsBase, imageViewBase, tagsViewBase
from resources import parameters, tag_categories
from tools import files
from CustomWidgets import confirmation_dialog, InputDialog

class UniqueTagsView(QtCore.QAbstractListModel):
	def __init__(self, display_tags: list[str] | set[str], image: ImageDatabase, highlight_tags: list[str]=[], uncommon_tags: list[tuple[str, float]]=[]):

		super().__init__()
		self.display_tags = []
		for category in tag_categories.COLOR_DICT_ORDER:
			self.display_tags.extend([t for t in tag_categories.CATEGORY_TAG_DICT[category] if t in display_tags and t not in self.display_tags])
		self.display_tags.extend(tag for tag in display_tags if tag not in self.display_tags)
		self.image = image # never change anything in this object, it's only to gather information on the tags
		self.highlight_tags = highlight_tags

		# uncommon tags are tags not present in all the images when using a common image
		self.uncommon_tags: dict[str: float] = {}
		if uncommon_tags:
			for tag_tuple in uncommon_tags:
				if tag_tuple[0] not in self.display_tags:
					self.display_tags.append(tag_tuple[0])
					self.uncommon_tags[tag_tuple[0]] = int(255*tag_tuple[1])
		self.uncommon_tags_keys = self.uncommon_tags.keys()

	def rowCount(self, parent=None):
		return len(self.display_tags)

	def sort_display_tags(self, func):
		self.display_tags.sort(key=lambda x: func(x))

	def data(self, index, role):
		tag = self.display_tags[index.row()]
		if role == QtGui.Qt.ItemDataRole.DisplayRole:
			return tag

		if role == QtGui.Qt.ItemDataRole.FontRole:
			font = QtGui.QFont()
			if tag in self.image.manual_tags or tag in self.image.rejected_manual_tags:
				font.setBold(True)
			if (tag in self.image.filtered_rejected_tags or tag in self.image.rejected_tags) and (tag not in self.image.secondary_new_tags and tag not in self.image.manual_tags):
				font.setStrikeOut(True)
			if tag in self.uncommon_tags_keys:
				font.setItalic(True)
				font.setPointSize(parameters.PARAMETERS["font_size"]-2)
			return font

		if role == QtGui.Qt.ItemDataRole.ForegroundRole and type(tag) == str and tag in tag_categories.COLOR_DICT.keys():
			red, green, blue, alpha = tag_categories.COLOR_DICT[tag]
			brush = QtGui.QBrush()
			brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
			return brush

		if role == QtGui.Qt.ItemDataRole.BackgroundRole:
			if self.highlight_tags and any([t in tag for t in self.highlight_tags]):
				brush = QtGui.QBrush(QtGui.QColor.fromRgb(199,255,255, 80)) # color: Azure (darker shade)
			elif self.image.full_tags_token_length and self.image.full_tags_token_length > 223:# and (tag in tag_categories.HIGH_TOKEN_COUNT or len(tag) > 15):
				if tag in tag_categories.HIGH_TOKEN_COUNT:
					brush = QtGui.QBrush(QtGui.QColor.fromRgb(255,240,245, 50)) #Lavender Blush
				elif len(tag) > 15:
					brush = QtGui.QBrush(QtGui.QColor.fromRgb(255,240,245, 20)) #Lavender Blush
				else:
					return # just return nothing for background color
			else:
				return # just return nothing for background color
			brush.setStyle(QtCore.Qt.BrushStyle.Dense2Pattern)
			return brush


		if role == QtGui.Qt.ItemDataRole.ToolTipRole:
			tooltip_text = f"Tag: {tag}"
			if tag in self.uncommon_tags_keys:
				tooltip_text += f"\nOccurrence: {int((self.uncommon_tags[tag]/255)*100)} % of the selected images"
			if tag in tag_categories.TAG_DEFINITION.keys():
				tooltip_text += f"\nDefinition:  {tag_categories.TAG_DEFINITION[tag]}"

			if tag in self.image.external_tags_list:
				tooltip_text += f"\nOrigin: {', '.join(self.image.get_external_tag_origin(tag))} - external tags"
			if tag in self.image.simple_auto_tags_list:
				tooltip_text += f"\nOrigin: {', '.join(self.image.get_auto_tag_origin(tag))} - auto tags"
			if tag in self.image.secondary_new_tags or tag in self.image.filtered_new_tags:
				tooltip_text += f"\nOrigin: filter"

			return tooltip_text

class ConflictTagsView(QtCore.QAbstractItemModel):
	def __init__(self, conflicts, image: ImageDatabase, highlight_tags: list[str]=[]):
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
		self.highlight_tags = highlight_tags

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
			return node["name"]

		if index.parent().isValid():
			if role == QtGui.Qt.ItemDataRole.FontRole:
				font = QtGui.QFont()
				if node["name"] in self.image.manual_tags or node["name"] in self.image.rejected_manual_tags:
					font.setBold(True)
				if (node["name"] in self.image.filtered_rejected_tags or node["name"] in self.image.rejected_tags) and (
						node["name"] not in self.image.secondary_new_tags and node["name"] not in self.image.manual_tags):
					font.setStrikeOut(True)
				if (
						node["name"] in self.image.secondary_rejected_tags and node["name"] not in self.image.filtered_rejected_tags) or node["name"] in self.image.secondary_new_tags:
					font.setItalic(True)
				return font

			if role == QtGui.Qt.ItemDataRole.ForegroundRole and type(
					node["name"]) == str and node["name"] in tag_categories.COLOR_DICT.keys():
				red, green, blue, alpha = tag_categories.COLOR_DICT[node["name"]]
				brush = QtGui.QBrush()
				brush.setColor(QtGui.QColor.fromRgb(red, green, blue, alpha))
				return brush

			if role == QtGui.Qt.ItemDataRole.BackgroundRole:
				if self.highlight_tags and any([t in node["name"] for t in self.highlight_tags]):
					brush = QtGui.QBrush(QtGui.QColor.fromRgb(199,255,255, 80)) # color: Azure (darker shade)
       
				elif self.image.full_tags_token_length and self.image.full_tags_token_length > 223:
					if node["name"] in tag_categories.HIGH_TOKEN_COUNT:
						brush = QtGui.QBrush(QtGui.QColor.fromRgb(255, 255, 255, 50))
					elif len(node["name"]) > 15:
						brush = QtGui.QBrush(QtGui.QColor.fromRgb(255, 255, 255, 20))
					else:
						return  # just return nothing for background color
				else:
					return  # just return nothing for background color
				brush.setStyle(QtCore.Qt.BrushStyle.Dense2Pattern)
				return brush

			if role == QtGui.Qt.ItemDataRole.ToolTipRole:
				tooltip_text = f""
				if node["name"] in tag_categories.TAG_DEFINITION.keys():
					tooltip_text += f"Definition:  {tag_categories.TAG_DEFINITION[node['name']]}"

				if node["name"] in self.image.external_tags_list:
					tooltip_text += f"\nOrigin: {', '.join(self.image.get_external_tag_origin(node['name']))} - external tags"
				if node["name"] in self.image.simple_auto_tags_list:
					tooltip_text += f"\nOrigin: {', '.join(self.image.get_auto_tag_origin(node['name']))} - auto tags"
				if node["name"] in self.image.secondary_new_tags or node['name'] in self.image.filtered_new_tags:
					tooltip_text += f"\nOrigin: filter"

				return tooltip_text

		return None

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

		if role == QtGui.Qt.ItemDataRole.ToolTipRole:
			tooltip_text = f"Tag: {tag}"
			if tag in tag_categories.TAG_DEFINITION.keys():
				tooltip_text += f"\nDefinition:  {tag_categories.TAG_DEFINITION[tag]}"
			return tooltip_text



class SortType(enum.Enum):
	# add sort name and the sort function here to add sort method to ui

	# Name, function, Tooltip description
	TAGS_LEN = "Tags length", lambda x: len(x.full_tags), "Tags Length"
	TOKEN_LEN = "Token length", lambda x: x.get_token_length(), "Other"
	SENTENCE_TOKEN_LEN = "Sentence token length", lambda x: x.get_sentence_token_length(), "Other"
	MANUAL_TAGS_LEN = "Manual tags length", lambda x: len(x.manual_tags), "Other"
	FILE_NAME = "Filename", lambda x: x.get_filename(), "Other"
	CONFLICTS_LEN = "Conflicts length", lambda x: len(x.filtered_review.keys()), "Other"
	SCORE_RATING = "Aesthetic score", lambda x: x.get_score_sort_tuple(), "Other" # double sort (label, score)
	IMAGE_RATIO = "Image ratio", lambda x: x.image_ratio, "Other"
	IMAGE_PIXEL_COUNT = "Image pixel count", lambda x: x.image_width*x.image_height, "Other"
	IMAGE_WIDTH = "Image width", lambda x: (x.image_width, x.image_height), "Other"
	IMAGE_HEIGHT = "Image height", lambda x: (x.image_height, x.image_width), "Other"
	SIMILARITY_GROUP = "Similarity", lambda x: x.similarity_group, "Other"
	BRIGHTNESS_VALUE = "Brightness", lambda x: x.get_brightness(), "Other"
	AVERAGE_PIXEL = "Average pixel", lambda x: x.get_average_pixel(), "Other"
	CONTRAST_COMPOSITION = "Contrast", lambda x: x.get_contrast_composition(), "Other"
	UNDERLIGHTING_COMPOSITION = "Underlighting", lambda x: x.get_underlighting(), "Other"
	GRADIENT_COMPOSITION = "Gradient", lambda x: x.get_gradient(), "Other"

 
	CHARACTER_COUNT = "Named characters count", lambda x: x.get_character_count(), "Other"
	RARE_TAGS_COUNT = "Rare tags count", lambda x: x.get_rare_tags_count(), "Other"
	UNKNOWN_TAGS = "Unknown tags", lambda x: x.get_unknown_tags_count(), "Other"

	def sort_function(self, image):
		return self.value[1](image)

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

	def rowCount(self, parent=None):
		return self.row_count

	def apply_order(self, list_sort):
		self.beginResetModel()
		self.clear()
		self.row_count = len(list_sort)
		for x in list_sort:
			item = self.create_item(x[0])
			self.appendRow(item)
		self.endResetModel()


	def create_item(self, image_index):
		item = QStandardItem(str(image_index))
		item.setIcon(self.images_dict[image_index][0])
		date_modified = datetime.datetime.fromtimestamp(os.path.getmtime(self.images_dict[image_index][1].path))
		date_created = datetime.datetime.fromtimestamp(os.path.getctime(self.images_dict[image_index][1].path))
		if parameters.PARAMETERS["database_view_tooltip"]:
			item.setToolTip(
				f'<b>path: {self.images_dict[image_index][1].path}, width: {self.images_dict[image_index][1].image_width}, height: {self.images_dict[image_index][1].image_height}, date modified: {date_modified}, date created: {date_created}, </b><br><img src="{self.images_dict[image_index][1].path}" width={768 * self.images_dict[image_index][1].image_ratio} height={768}>')
		return item

	def data(self, index, role):
		if role == QtGui.Qt.ItemDataRole.DecorationRole:
			return self.item(index.row()).data(QtGui.Qt.ItemDataRole.DecorationRole)
		if role == QtGui.Qt.ItemDataRole.ToolTipRole:
			return self.item(index.row()).data(QtGui.Qt.ItemDataRole.ToolTipRole)
		if role == QtGui.Qt.ItemDataRole.BackgroundRole:
			return self.item(index.row()).data(QtGui.Qt.ItemDataRole.BackgroundRole)

class DatabaseToolsBase(QWidget, databaseToolsBase.Ui_Form):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

class ImageViewBase(QWidget, imageViewBase.Ui_Form):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

		self.layout().removeWidget(self.listView_groups)
		self.layout().removeWidget(self.listView_other)
		self.other_splitter = QSplitter()
		self.other_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
		self.other_splitter.addWidget(self.listView_groups)
		self.other_splitter.addWidget(self.listView_other)
		self.layout().insertWidget(2, self.other_splitter)

class TagsViewBase(QWidget, tagsViewBase.Ui_Form):
	def __init__(self):
		super().__init__()
		self.setupUi(self)

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



		self.layout().insertWidget(4, splitter)

class DatabaseViewBase(QWidget):
	def __init__(self, db: Database):
		super().__init__()

		self.db = db
		self.saved_recent_db = self.db

		# history, the most ancient one is the first one, the most recent one is on index -1
		self.db_history: list[tuple[Database, str]] = [(copy.deepcopy(self.db), "Database on Load")]
		self.db_history_last_saved_index = 0


		# create the big 3 layout
		splitter = QSplitter()
		simple_layout = QHBoxLayout()
		self.stacked_widget = QStackedWidget()
		self.image_view = ImageViewBase()
		self.tags_view = TagsViewBase()
		self.database_tools = DatabaseToolsBase()
		self.stacked_widget.addWidget(self.image_view)
		splitter.addWidget(self.stacked_widget)
		splitter.addWidget(self.tags_view)
		splitter.addWidget(self.database_tools)
		simple_layout.addWidget(splitter)
		self.setLayout(simple_layout)

		# single image view
		self.single_image_widget = QWidget()
		self.single_image_button = QPushButton()
		self.stacked_widget.addWidget(self.single_image_widget)
		self.review_single_image_on_change = False
		self.init_single_image_widget()

		# images
		self.image_load_size = max(parameters.PARAMETERS["image_load_size"], 96)
		self.images_widgets: dict[int: object] = {}
		self.min_image_size = 16

		#tracking image_view
		self.current_group: str = "All"
		self.current_sort: SortType = SortType.TAGS_LEN
		self.current_search_tags: list[tuple[list[str], bool, bool]] = [] #tag, positive, exact
		self.current_images: list[int] = []
		self.common_image: ImageDatabase = None
		self.uncommon_added_tags: list[tuple[str, float]] = []
		self.uncommon_rejected_tags: list[tuple[str, float]] = []

		# Tracking tags
		self.current_highlight_tag: list[str] = []
		self.tags_view.lineEdit_tag_highlight.editingFinished.connect(self.update_highlight_tags)

  
		# popup image
		self.popup_window = False


		self.init_image_view()
		self.init_tools_view()
		#self.init_tags_view()
		self.init_favourites()
		self.init_history_view()
		self.database_tools.lineEdit_edit_favourites.returnPressed.connect(self.edit_favourites)
		self.tags_view.comboBox_score_tags.addItem("NONE")
		self.tags_view.comboBox_score_tags.addItems(tag_categories.QUALITY_LABELS)
		self.tags_view.lineEdit_add_tags.returnPressed.connect(self.add_tags_to_selected_images)

		if parameters.PARAMETERS["double_click"]:
			self.tags_view.listView_tags.doubleClicked.connect(self.clicked_base_tags)
			self.tags_view.listView_recommendations.doubleClicked.connect(self.clicked_recommendations)
			self.tags_view.listView_rejected.doubleClicked.connect(self.clicked_rejected)
			self.tags_view.treeView_conflicts.doubleClicked.connect(self.clicked_conflicts) 
		else:
			self.tags_view.listView_tags.clicked.connect(self.clicked_base_tags)
			self.tags_view.listView_recommendations.clicked.connect(self.clicked_recommendations)
			self.tags_view.listView_rejected.clicked.connect(self.clicked_rejected)
			self.tags_view.treeView_conflicts.clicked.connect(self.clicked_conflicts)
			
		#self.tags_view.checkBox_hide_sentence.stateChanged.connect(self.show_or_hide_sentence)
  
		## Autocompletion
		# TODO: custom completer that priorities the view of tag_categories over danbooru tags
		self.wordlist = QStringListModel()
		tags = set([tag for tag, freq in tag_categories.DESCRIPTION_TAGS_FREQUENCY.items() if int(freq) > 50] + list(
				tag_categories.COLOR_DICT.keys()))
		self.wordlist.setStringList(tags)
		self.completer = QCompleter(self.wordlist)
		self.completer.setModelSorting(QCompleter.ModelSorting.CaseSensitivelySortedModel)
		self.completer.setMaxVisibleItems(5)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
		# self.completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
		self.completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
		self.tags_view.lineEdit_add_tags.setCompleter(self.completer)

	def init_favourites(self):
		favourites = files.get_favourites()
		blank_image = ImageDatabase()
		fav_dict = {}
		for tag_category, tag_set in tag_categories.TAG_CATEGORIES_EXCLUSIVE.items():
			if any([fav in tag_set for fav in favourites]):
				fav_dict[tag_category] = [fav for fav in favourites if fav in tag_set]
				favourites = [fav for fav in favourites if fav not in fav_dict[tag_category]]
		if favourites:
			fav_dict["Other"] = favourites
		fav_model = ConflictTagsView(fav_dict, blank_image)
		self.database_tools.treeView_favourites.setModel(fav_model)
		self.database_tools.treeView_favourites.expandAll()
		self.database_tools.treeView_favourites.clicked.connect(self.clicked_favourites)

	@Slot()
	def edit_favourites(self):
		edit = [tag.strip() for tag in self.database_tools.lineEdit_edit_favourites.text().split(",")]
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
		self.database_tools.lineEdit_edit_favourites.clear()


	def init_single_image_widget(self):
		# image button
		vert_layout = QVBoxLayout()
		self.single_image_button.clicked.connect(self.clicked_single_image_button)
		vert_layout.addWidget(self.single_image_button)
		bottom_layout = QHBoxLayout()
		go_left_button = QPushButton("<-")
		go_left_button.clicked.connect(self.clicked_go_left_button)

		single_reviewed_checkbox = QCheckBox("Review On Change")
		single_reviewed_checkbox.stateChanged.connect(self.single_reviewed_changed)

		go_right_button = QPushButton("->")
		go_right_button.clicked.connect(self.clicked_go_right_button)
		bottom_layout.addWidget(go_left_button)
		bottom_layout.addWidget(single_reviewed_checkbox)
		bottom_layout.addWidget(go_right_button)

		vert_layout.addLayout(bottom_layout)
		self.single_image_widget.setLayout(vert_layout)

	@Slot(QtCore.Qt.CheckState)
	def single_reviewed_changed(self, check_state):
		if check_state == QtCore.Qt.CheckState.Checked.value:
			self.review_single_image_on_change = True
		else:
			self.review_single_image_on_change = False

	@Slot()
	def clicked_single_image_button(self):
		self.stacked_widget.setCurrentIndex(0)

	@Slot()
	def clicked_go_left_button(self):
		if self.image_view.listView_groups.selectedIndexes()[0].row() == 0:
			parameters.log.info("First image, can't go back")
			return False
		if self.review_single_image_on_change:
			self.update_review(True)
		next_index = self.image_view.listView_groups.model().index(self.image_view.listView_groups.selectedIndexes()[0].row()-1, self.image_view.listView_groups.selectedIndexes()[0].column())
		self.image_view.listView_groups.setCurrentIndex(next_index)
		self.clicked_images_changed()

	@Slot()
	def clicked_go_right_button(self):
		if self.image_view.listView_groups.selectedIndexes()[0].row()+1 >= self.image_view.listView_groups.model().rowCount():
			parameters.log.info("Last image, can't go further")
			return False
		if self.review_single_image_on_change:
			self.update_review(True)
		next_index = self.image_view.listView_groups.model().index(self.image_view.listView_groups.selectedIndexes()[0].row()+1, self.image_view.listView_groups.selectedIndexes()[0].column())
		self.image_view.listView_groups.setCurrentIndex(next_index)
		self.clicked_images_changed()

	def update_single_image_view(self):
		image_object = QtGui.QImage(self.get_current_image().path)
		icon = QPixmap(image_object)
		self.single_image_button.setIcon(icon)
		self.single_image_button.setIconSize((QtCore.QSize(int(self.stacked_widget.width() * 0.9), int(self.stacked_widget.height() * 0.9))))
		self.single_image_button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)



	def init_image_view(self):
		self.db.create_images_objects(self.image_load_size)
		self.db.tokenize_all_images()


		# selection updated
		self.image_view.listView_groups.clicked.connect(self.clicked_images_changed)
		self.image_view.checkBox_single_selection_mode.stateChanged.connect(self.selection_mode_changed)

		# slider
		self.image_view.horizontalSlider_thumbnail_size.setMinimum(self.min_image_size)
		self.image_view.horizontalSlider_thumbnail_size.setMaximum(self.image_load_size)
		self.image_view.horizontalSlider_thumbnail_size.setValue(self.image_load_size)
		self.image_view.horizontalSlider_thumbnail_size.valueChanged.connect(self.slider_thumbnail_size_changed)

		# group names
		self.image_view.comboBox_group_name.addItem("All")
		self.image_view.comboBox_group_name.addItems([group_name for group_name in self.db.groups.keys()])
		#self.image_view.comboBox_group_name.currentTextChanged.connect(self.selected_group_changed)
		#self.image_view.comboBox_group_name.editTextChanged.connect(self.selected_group_changed)
		self.image_view.comboBox_group_name.currentIndexChanged.connect(self.selected_group_changed)

		# sort type
		k=0
		for x in SortType:
			self.image_view.comboBox_sort_type.addItem(x.value[0])
			self.image_view.comboBox_sort_type.setItemData(k, x.value[2], QtCore.Qt.ItemDataRole.ToolTipRole)
			k+=1
		self.image_view.comboBox_sort_type.currentTextChanged.connect(self.selected_sort_changed)

		# sentence search and reverse search
		self.image_view.checkBox_reverse.stateChanged.connect(self.update_sorting)
		self.image_view.checkBox_include_sentence.stateChanged.connect(self.update_sorting)

		# tag search
		self.image_view.lineEdit_tag_search.editingFinished.connect(self.search_tags_changed)

		# clear search button
		#self.image_view.pushButton_clear_search.clicked.connect(self.clear_sorting)

		# create image objects and show them
		self.create_all_images_frames()
		self.first_view()

		# show ungrouped images when selecting groups
		self.image_view.checkBox_toggle_ungrouped_images.clicked.connect(self.update_other_view)

		#add and remove selections to and from groups
		self.image_view.pushButton_remove_selection_from_group.clicked.connect(self.remove_selection_from_group)
		self.image_view.pushButton_add_selection_to_group.clicked.connect(self.add_selection_to_group)

		# create new group
		self.image_view.pushButton_add_group.clicked.connect(self.create_group)
		self.image_view.pushButton_deleted_group.clicked.connect(self.delete_group)

	@Slot()
	def clicked_base_tags(self, index):
		if not index.isValid():
			return False
		tag = self.tags_view.listView_tags.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)
		img = self.get_current_image()
		img.append_rejected_manual_tags([tag])
		img.remove_manual_tags([tag])
		self.update_tags_view()


	@Slot()
	def clicked_recommendations(self, index):
		if not index.isValid():
			return False
		tag = self.tags_view.listView_recommendations.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)
		img = self.get_current_image()
		img.append_manual_tags([tag])
		img.remove_rejected_manual_tags([tag])
		self.update_tags_view()

	@Slot()
	def clicked_rejected(self, index):
		if not index.isValid():
			return False
		tag = self.tags_view.listView_rejected.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole)
		img = self.get_current_image()
		img.remove_rejected_manual_tags([tag])
		img.append_manual_tags([tag])
		self.update_tags_view()

	@Slot()
	def clicked_conflicts(self, index):
		if not index.isValid():
			return False
		if not index.parent().isValid():
			img = self.get_current_image()
			img.append_resolved_conflict(index.internalPointer()["name"])
			self.update_tags_view()
			return True
		tag = index.internalPointer()["name"]
		sub_category =  index.parent().internalPointer()
		img = self.get_current_image()
		img.append_rejected_manual_tags([x["name"] for x in sub_category["children"] if x["name"] != tag])
		img.remove_manual_tags([x["name"] for x in sub_category["children"] if x["name"] != tag])
		self.update_tags_view()

	@Slot()
	def right_clicked_conflicts(self):
		index = self.tags_view.treeView_conflicts.currentIndex()
		if not index.isValid():
			return False
		if not index.parent().isValid():
			img = self.get_current_image()
			img.append_resolved_conflict(index.internalPointer()["name"])
			self.update_tags_view()
			return True
		tag = index.internalPointer()["name"]
		img = self.get_current_image()
		img.append_rejected_manual_tags([tag])
		self.update_tags_view()

	@Slot()
	def clicked_favourites(self, index):
		if not index.isValid():
			return False
		if not self.get_current_image():
			parameters.log.info("No images were selected")
			return False
		if not index.parent().isValid():
			parameters.log.info("Can't add tag favourites categories to tags")
			return False
		tag = index.internalPointer()["name"]
		img = self.get_current_image()
		img.append_manual_tags([tag])
		self.update_tags_view()


	@Slot()
	def add_tags_to_selected_images(self):
		if not self.current_images:
			parameters.log.info("No images selected.")
			return False
		text = self.tags_view.lineEdit_add_tags.text()
		if not text:
			parameters.log.info("No text entered.")
			return False
		tags = [x.strip() for x in text.split(",") if x.strip()]
		if all([not tag for tag in tags]):
			parameters.log.info("No valid text entered.")
			return False

		img = self.get_current_image()
		img.append_manual_tags(tags)
		img.remove_rejected_manual_tags(tags)
		self.update_tags_view()
		if self.tags_view.checkBox_clear_on_add.isChecked():
			self.tags_view.lineEdit_add_tags.clear()

	def get_current_image(self):
		if len(self.current_images) == 1:
			return self.db.images[self.current_images[0]]
		return self.common_image



	@Slot()
	def clicked_images_changed(self):
		selected_indexes = [int(self.image_view.listView_groups.model().itemData(index)[0]) for index in self.image_view.listView_groups.selectedIndexes()]
		self.apply_selection_gradient(self.image_view.listView_groups.selectedIndexes())
		self.update_selected_images_changed(selected_indexes)


	def update_selected_images_changed(self, selected_indexes):
		"""
		Args:
			selected_indexes: indexes of the images inside the database images list
		"""
		self.update_pop_up_image(selected_indexes)
		self.init_tags_view(selected_indexes)

		if len(selected_indexes) == 1 and self.image_view.checkBox_zoom_on_click.isChecked():
			self.stacked_widget.setCurrentIndex(1)
			self.update_single_image_view()

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
		for base_index in range(self.image_view.listView_groups.model().rowCount()):
			index = self.image_view.listView_groups.model().index(base_index, 0)
			if index in selected_model_indexes:
				self.image_view.listView_groups.model().setData(index, brush, QtGui.Qt.ItemDataRole.BackgroundRole)
			else:
				self.image_view.listView_groups.model().setData(index, blank_brush, QtGui.Qt.ItemDataRole.BackgroundRole)



	@Slot()
	def selection_mode_changed(self):
		if self.image_view.checkBox_single_selection_mode.isChecked():
			self.image_view.listView_groups.setSelectionMode(self.image_view.listView_groups.SelectionMode.SingleSelection)
		else:
			self.image_view.listView_groups.setSelectionMode(self.image_view.listView_groups.SelectionMode.ExtendedSelection)


	def update_tags_view(self):
		if not self.current_images:
			return False
		self.get_current_image().filter()
		self.show_or_hide_sentence(bool(self.get_current_image().sentence_description))
		self.update_single_image_tags(self.get_current_image())
		if len(self.current_images) == 1:
			self.tags_view.plainTextEdit_sentence.setPlainText(self.get_current_image().sentence_description)
		self.update_tags_labels()

	def show_or_hide_sentence(self, is_sentence):
		if is_sentence:
			self.tags_view.label_sentence_len.show()
			self.tags_view.plainTextEdit_sentence.show()
			self.tags_view.widget_2.show()
		elif parameters.PARAMETERS["hide_sentence_in_view"]:
			self.tags_view.label_sentence_len.hide()
			self.tags_view.plainTextEdit_sentence.hide()
			self.tags_view.widget_2.hide()
		else:
			self.tags_view.label_sentence_len.show()
			self.tags_view.plainTextEdit_sentence.show()
			self.tags_view.widget_2.show()

	def save_current_images(self):
		def save_quality_score(aesthetic_score, image_index):
			self.db.images[image_index].score_label = aesthetic_score
		def save_sentence(sentence, image_index):
			self.db.images[image_index].sentence_description = sentence
		def save_reviewed_state(review_state, image_index):
			self.db.images[image_index].manually_reviewed = review_state

		if self.common_image:
			artificial_image = self.create_artificial_common_image([self.db.images[x] for x in self.current_images])
			for index in self.current_images:
				self.db.images[index].manual_tags = [tag for tag in self.db.images[index].manual_tags if tag not in self.common_image.rejected_manual_tags]+[tag for tag in self.common_image.manual_tags if tag not in artificial_image.manual_tags]
				self.db.images[index].rejected_manual_tags = [tag for tag in self.db.images[index].rejected_manual_tags if tag not in self.common_image.manual_tags]+[tag for tag in self.common_image.rejected_manual_tags if tag not in artificial_image.rejected_manual_tags]
				if self.tags_view.comboBox_score_tags.currentIndex() != 0  and self.tags_view.comboBox_score_tags.currentText() != artificial_image.score_label:
					save_quality_score(self.tags_view.comboBox_score_tags.currentText(), index)
				if self.tags_view.checkBox_reviewed.isChecked():
					save_reviewed_state(self.tags_view.checkBox_reviewed.isChecked(), index)

		elif len(self.current_images) == 1:
			save_reviewed_state(self.tags_view.checkBox_reviewed.isChecked(), self.current_images[0])
			if self.tags_view.comboBox_score_tags.currentText() != self.db.images[self.current_images[0]].score_label:
				if self.tags_view.comboBox_score_tags.currentText() == "NONE":
					save_quality_score("", self.current_images[0])
				else:
					save_quality_score(self.tags_view.comboBox_score_tags.currentText(), self.current_images[0])

			if self.tags_view.plainTextEdit_sentence.toPlainText().strip() != self.db.images[self.current_images[0]].sentence_description:
				save_sentence(self.tags_view.plainTextEdit_sentence.toPlainText().strip(), self.current_images[0])


	def init_tags_view(self, image_index_list: list[int]):
		self.save_current_images()
		#self.add_db_to_history()

		self.uncommon_added_tags = []
		self.uncommon_rejected_tags = []

		if len(image_index_list) == 1:
			self.update_review(self.db.images[image_index_list[0]].manually_reviewed)
			self.current_images = image_index_list
			self.common_image = None
			self.update_tags_view()
		else:
			all_images = [self.db.images[i] for i in image_index_list]
			common_image = self.create_artificial_common_image(all_images)
			self.current_images = image_index_list
			self.common_image = common_image
			self.update_review(False)
			self.update_tags_view()


	def update_tags_labels(self):
		if len(self.current_images) == 1:
			self.update_labels(tags_len=len(self.db.images[self.current_images[0]].full_tags),
							   token_len=self.db.images[self.current_images[0]].get_token_length(),
							   image_path=self.db.images[self.current_images[0]].path,
							   sentence_len=self.db.images[self.current_images[0]].get_sentence_token_length())
		elif len(self.current_images) > 1:
			self.update_labels(tags_len=len(self.common_image.full_tags),
							   token_len=self.common_image.get_token_length(),
			                   image_path=f"{len(self.current_images)} images selected"
			                   )


	def create_artificial_common_image(self, all_images: list[ImageDatabase]):
		artificial_image = ImageDatabase()

		auto_tags = {}
		for auto_tagger in all_images[0].auto_tags.keys():
			auto_tags[auto_tagger] = [tag_tuple for tag_tuple in all_images[0].auto_tags[auto_tagger] if all([tag_tuple[0] in x.simple_auto_tags[auto_tagger] for x in all_images])]

		external_tags = {}
		for external_name in all_images[0].external_tags.keys():
			external_tags[external_name] = [tag for tag in all_images[0].external_tags[external_name] if all(external_name in x.external_tags.keys() for x in all_images) and all([tag in x.external_tags[external_name] for x in all_images])]

		common_manual = [tag for tag in all_images[0].manual_tags if all([tag in image.manual_tags for image in all_images])]
		common_rejected_manual = [tag for tag in all_images[0].rejected_manual_tags if all([tag in image.rejected_manual_tags for image in all_images])]

		common_score_label = ""
		if all([all_images[0].score_label == image.score_label for image in all_images]):
			common_score_label = all_images[0].score_label

		common_classify_label = ""
		if all([all_images[0].classify_label == image.classify_label for image in all_images]):
			common_classify_label = all_images[0].classify_label

		artificial_image.init_image_dict({
			"auto_tags": auto_tags,
			"external_tags": external_tags,

			"manual_tags": common_manual,
			"rejected_manual_tags": common_rejected_manual,

			"score_label": common_score_label,
			"classify_label": common_classify_label,
		})
		artificial_image.filter()
		artificial_image.get_full_tags()

		uncommon_added_tags = []
		uncommon_rejected_tags = []

		for image in all_images:
			uncommon_added_tags.extend([tag for tag in image.get_full_tags() if tag not in artificial_image.full_tags])
			uncommon_rejected_tags.extend([tag for tag in image.rejected_tags if tag not in artificial_image.rejected_tags])

		c = Counter()
		c.update(uncommon_added_tags)
		self.uncommon_added_tags = [(tag_tuple[0], tag_tuple[1]/len(all_images)) for tag_tuple in c.most_common()]

		c = Counter()
		c.update(uncommon_rejected_tags)
		self.uncommon_rejected_tags = [(tag_tuple[0], tag_tuple[1] / len(all_images)) for tag_tuple in c.most_common()]

		return artificial_image



	def update_aesthetic_score(self, image: ImageDatabase):
		current_score_label = image.score_label
		if current_score_label and current_score_label in tag_categories.QUALITY_LABELS:
			self.tags_view.comboBox_score_tags.setCurrentIndex(tag_categories.QUALITY_LABELS.index(current_score_label)+1)
		else:
			self.tags_view.comboBox_score_tags.setCurrentIndex(0)
		for index in range(self.tags_view.comboBox_score_tags.count()):
			self.tags_view.comboBox_score_tags.setItemData(index, QtGui.QColor(0, 0, 0, 255),role=QtCore.Qt.ItemDataRole.BackgroundRole)
			if index == self.tags_view.comboBox_score_tags.currentIndex():
				self.tags_view.comboBox_score_tags.setItemData(index, QtGui.QColor(0,206,209,255),role=QtCore.Qt.ItemDataRole.BackgroundRole)


	def update_single_image_tags(self, image: ImageDatabase):
		full_tags_model = UniqueTagsView(image.get_full_tags(), image, highlight_tags=self.current_highlight_tag, uncommon_tags=self.uncommon_added_tags)
		#full_tags_model.sort_display_tags(lambda x: x)
		rejected_tags_model = UniqueTagsView(image.rejected_tags, image, highlight_tags=self.current_highlight_tag, uncommon_tags=self.uncommon_rejected_tags)
		#rejected_tags_model.sort_display_tags(lambda x: x)
		recommendation_tags_model = UniqueTagsView(image.get_recommendations(), image, highlight_tags=self.current_highlight_tag)
		#recommendation_tags_model.sort_display_tags(lambda x: x)
		conflicts_tags_model = ConflictTagsView(image.get_unresolved_conflicts(), image, highlight_tags=self.current_highlight_tag)
		self.tags_view.listView_tags.setModel(full_tags_model)
		self.tags_view.listView_rejected.setModel(rejected_tags_model)
		self.tags_view.listView_recommendations.setModel(recommendation_tags_model)
		self.tags_view.treeView_conflicts.setModel(conflicts_tags_model)


		self.tags_view.listView_tags.keyPressEvent = lambda event: self.on_key_press(event, self.tags_view.listView_tags)
		self.tags_view.listView_rejected.keyPressEvent = lambda event: self.on_key_press(event, self.tags_view.listView_rejected)
		self.tags_view.listView_recommendations.keyPressEvent = lambda event: self.on_key_press(event, self.tags_view.listView_recommendations)
		self.tags_view.treeView_conflicts.keyPressEvent = lambda event: self.on_key_press(event, self.tags_view.treeView_conflicts)
		self.tags_view.treeView_conflicts.rightClicked.connect(self.right_clicked_conflicts)


		self.tags_view.treeView_conflicts.setHeaderHidden(True)
		self.tags_view.treeView_conflicts.expandAll()
		if self.tags_view.listView_recommendations.model().rowCount() == 0:
			self.tags_view.listView_recommendations.hide()
		else:
			self.tags_view.listView_recommendations.show()
		if self.tags_view.treeView_conflicts.model().rowCount() == 0:
			self.tags_view.treeView_conflicts.hide()
		else:
			self.tags_view.treeView_conflicts.show()
		self.update_aesthetic_score(image)

	def update_labels(self, *, tags_len=0, token_len=0, image_path="multiple_images", sentence_len=0):
		self.tags_view.label_image_path.setText(f"{image_path}")
		self.tags_view.label_tags_len.setText(f"{tags_len} tags")
		self.tags_view.label_token_len.setText(f"{token_len} tokens")
		if token_len > 225:
			style = "QLabel { color : red; }" + self.tags_view.label_image_path.styleSheet()
			self.tags_view.label_token_len.setStyleSheet(style)
		elif token_len > 223:
			style = "QLabel { color : orange; }" + self.tags_view.label_image_path.styleSheet()
			self.tags_view.label_token_len.setStyleSheet(style)
		else:
			style = self.tags_view.label_image_path.styleSheet()
			self.tags_view.label_token_len.setStyleSheet(style)
		self.tags_view.label_token_len.setText(f"{token_len} tokens")
		if os.path.exists(image_path):
			self.tags_view.label_image_ext.setText(f"{os.path.splitext(image_path)[1]}")
			self.tags_view.label_image_size.setText(f"{round(os.path.getsize(image_path)/(1024*1024), ndigits=4)} MB")
			self.tags_view.label_image_ext.show()
			self.tags_view.label_image_size.show()
		else:
			self.tags_view.label_image_ext.hide()
			self.tags_view.label_image_size.hide()
		self.tags_view.label_sentence_len.setText(f"{sentence_len} tokens")

	def update_review(self, reviewed: bool):
		self.tags_view.checkBox_reviewed.setChecked(reviewed)

	@Slot(int)
	def slider_thumbnail_size_changed(self, new_value):
		self.image_view.listView_groups.setIconSize(QSize(new_value, new_value))
		self.image_view.listView_other.setIconSize(QSize(new_value, new_value))

	@Slot(int)
	def selected_group_changed(self, index):
		self.current_group = self.image_view.comboBox_group_name.currentText()
		self.update_sorting()
		self.update_other_view()

	@Slot(str)
	def selected_sort_changed(self, text):
		self.current_sort = get_sort_member(text)
		if self.current_sort == SortType.SIMILARITY_GROUP:
			self.db.find_similar_images()
		# todo: highlight rare tags checkbox
		if self.current_sort == SortType.RARE_TAGS_COUNT:
			self.db.update_rare_tags()
		self.update_sorting()
		self.update_other_view()

	@Slot()
	def search_tags_changed(self):
		search_tags = self.image_view.lineEdit_tag_search.text().split(',')
		temp_search_tags = []
		for tag in search_tags:
			if tag.strip():
				to_add = ([tag.strip()], True, False)
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
		parameters.log.info(self.current_search_tags)
		self.update_sorting()
		self.update_other_view()


	@Slot()
	def update_sorting(self):
		"""
		Update the sorting view
		"""
		current_list_sort = sorted([(x, self.current_sort.sort_function(self.db.images[x])) for x in range(len(self.db.images)) if self.image_to_view(x)], key=lambda x: x[1], reverse=not self.image_view.checkBox_reverse.isChecked())
		self.image_view.listView_groups.model().apply_order(current_list_sort)
		self.image_view.label_image_view_count.setText(f"{self.image_view.listView_groups.model().rowCount()} images")

	@Slot()
	def update_other_view(self):
		"""
		Update the other model view
		"""
		if self.current_group == "All":
			self.image_view.listView_other.hide()
			return

		current_list_sort = sorted([(x, self.current_sort.sort_function(self.db.images[x])) for x in range(len(self.db.images)) if self.image_to_other_view(x)], key=lambda x: x[1], reverse=not self.image_view.checkBox_reverse.isChecked())
		if len(current_list_sort)==0:
			self.image_view.listView_other.hide()
		else:
			self.image_view.listView_other.show()
			self.image_view.listView_other.model().apply_order(current_list_sort)

	def image_to_view(self, image_index: int):
		tag_to_search_through = set(self.db.images[image_index].get_search_tags())
		if self.image_view.checkBox_include_sentence.isChecked():
			tag_to_search_through = tag_to_search_through.union([self.db.images[image_index].sentence_description])
		if self.current_group == "All":
			if self.current_search_tags:
				if not files.loose_tags_check(self.current_search_tags, tag_to_search_through):
					return False
				else:
					return True
			else:
				return True
		elif self.db.images[image_index].md5 in self.db.groups[self.current_group]["images"]:
			if self.current_search_tags:
				if not files.loose_tags_check(self.current_search_tags, tag_to_search_through):
					return False
				else:
					return True
			else:
				return True
		return False

	def image_to_other_view(self, image_index: int):
		if self.db.images[image_index].md5 in self.db.groups[self.current_group]["images"]:
			return False
		tag_to_search_through = set(self.db.images[image_index].get_search_tags())
		if self.image_view.checkBox_include_sentence.isChecked():
			tag_to_search_through = tag_to_search_through.union([self.db.images[image_index].sentence_description])
		if self.image_view.checkBox_toggle_ungrouped_images.isChecked():
			if self.current_search_tags:
				if files.loose_tags_check(self.current_search_tags, tag_to_search_through):
					return True
			else:
				return True
		else:
			if len(self.db.images[image_index].group_names)==0:
				if self.current_search_tags:
					if files.loose_tags_check(self.current_search_tags, tag_to_search_through):
						return True
				else:
					return True
		return False

	def create_all_images_frames(self):
		for k in range(len(self.db.images)):
			image_object = QPixmap(self.db.images[k].get_image_object())
			image_object = image_object.scaled(self.image_load_size, self.image_load_size,
											   QtCore.Qt.AspectRatioMode.KeepAspectRatio,
											   QtCore.Qt.TransformationMode.FastTransformation)
			self.images_widgets[k] = (image_object, self.db.images[k])

	def first_view(self):
		model = BaseImageView(self.images_widgets)
		model_other = BaseImageView(self.images_widgets)
		self.image_view.listView_groups.setModel(model)
		self.image_view.listView_groups.setViewMode(self.image_view.listView_groups.ViewMode.ListMode)
		self.image_view.listView_groups.setFlow(self.image_view.listView_groups.Flow.LeftToRight)
		self.image_view.listView_groups.setWrapping(True)
		self.image_view.listView_groups.setResizeMode(self.image_view.listView_groups.ResizeMode.Adjust)
		self.image_view.listView_groups.setSelectionMode(self.image_view.listView_groups.SelectionMode.ExtendedSelection)
		self.image_view.listView_groups.setIconSize(QSize(self.image_load_size, self.image_load_size))
		self.image_view.listView_other.setModel(model_other)
		self.image_view.listView_other.setViewMode(self.image_view.listView_groups.ViewMode.ListMode)
		self.image_view.listView_other.setFlow(self.image_view.listView_groups.Flow.LeftToRight)
		self.image_view.listView_other.setWrapping(True)
		self.image_view.listView_other.setResizeMode(self.image_view.listView_groups.ResizeMode.Adjust)
		self.image_view.listView_other.setSelectionMode(self.image_view.listView_groups.SelectionMode.ExtendedSelection)
		self.image_view.listView_other.setIconSize(QSize(self.image_load_size, self.image_load_size))
		self.image_view.listView_other.hide()
		self.selected_sort_changed(self.image_view.comboBox_sort_type.currentText())

	@Slot()
	def remove_selection_from_group(self):
		if self.current_group == "All":
			parameters.log.info("No group selected.")
			return False
		if len(self.image_view.listView_groups.selectedIndexes())==0:
			parameters.log.info("No images selected.")
			return False
		for w_index in self.image_view.listView_groups.selectedIndexes():
			image_index = int(self.image_view.listView_groups.model().itemData(w_index)[0])
			self.db.remove_image_from_group(self.current_group, image_index)
		self.image_view.listView_groups.clearSelection()
		self.update_sorting()
		self.update_other_view()
	@Slot()
	def add_selection_to_group(self):
		if self.current_group == "All":
			parameters.log.info("No group selected.")
			return False
		if len(self.image_view.listView_other.selectedIndexes())==0:
			parameters.log.info("No images selected.")
			return False
		for w_index in self.image_view.listView_other.selectedIndexes():
			image_index = int(self.image_view.listView_other.model().itemData(w_index)[0])
			self.db.add_image_to_group(self.current_group, image_index)
		self.image_view.listView_other.clearSelection()
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
		self.db.groups[user_input] = {}
		self.db.groups[user_input]["images"] = []
		self.image_view.comboBox_group_name.addItem(user_input)
		parameters.log.info(f"New group: {user_input}")

	@Slot()
	def delete_group(self):
		if self.current_group == "All":
			parameters.log.info("No group selected")
			return False
		if not confirmation_dialog(self):
			return False
		self.db.remove_group(self.current_group)
		current_comb_index = self.image_view.comboBox_group_name.currentIndex()
		self.image_view.comboBox_group_name.setCurrentIndex(0)
		self.image_view.comboBox_group_name.removeItem(current_comb_index)


	### Right Panel
	def init_tools_view(self):
		self.database_tools.pushButton_refresh_tags_frequency.clicked.connect(self.refresh_tags_frequency)
		for category in ["ALL"]+list(tag_categories.TAG_CATEGORIES.keys()):
			self.database_tools.comboBox_frequency_sort.addItem(category)
		self.database_tools.comboBox_frequency_sort.currentTextChanged.connect(self.refresh_tags_frequency)
		self.database_tools.pushButton_remove_tags_from_frequency_batch.clicked.connect(self.remove_tags_from_frequency)

		self.database_tools.pushButton_save_database.clicked.connect(self.save_database_button)
		self.database_tools.comboBox_selection.addItems(["Current Selection", "Visible Images", "Database"])
		self.database_tools.comboBox_selection.setCurrentIndex(0)
		self.database_tools.comboBox_batch_selection_frequency.addItems(["Current Selection", "Visible Images", "Database"])
		self.database_tools.comboBox_batch_selection_frequency.setCurrentIndex(0)
		self.database_tools.pushButton_replace.clicked.connect(self.replace_tags)

		# create the add button inside the view
		self.replace_lines: list[QWidget] = []
		self.base_replace_layout = QVBoxLayout()
		add_replace_line_button = QPushButton("Add replace line")
		remove_replace_line_button = QPushButton("Remove last replace lines")
		add_replace_line_button.clicked.connect(self.create_replace_line)
		remove_replace_line_button.clicked.connect(self.remove_last_replace_line)
		self.base_replace_layout.addWidget(add_replace_line_button)
		self.base_replace_layout.addWidget(remove_replace_line_button)
		self.database_tools.scrollAreaWidgetContents.setLayout(self.base_replace_layout)

  
		self.init_trigger_tags()
		self.database_tools.lineEdit_main_trigger_tag.editingFinished.connect(self.save_trigger_tags)
		self.database_tools.plainTextEdit_secondary_trigger_tags.textChanged.connect(self.save_trigger_tags)
		self.database_tools.pushButton_txt_file.clicked.connect(self.create_txt_files)
		self.database_tools.pushButton_json_tags_file.clicked.connect(self.create_json_file)
		self.database_tools.pushButton_make_sample_toml.clicked.connect(self.create_sample_toml)
		self.database_tools.pushButton_auto_tag.clicked.connect(self.batch_auto_tags)
		self.database_tools.pushButton_auto_score.clicked.connect(self.batch_auto_score)
		self.database_tools.pushButton_refresh_tags_from_gelbooru_and_rule34.clicked.connect(self.batch_refresh_online_tags)
		self.database_tools.pushButton_reset_manual_score.clicked.connect(self.batch_reset_manual_score)
		self.database_tools.pushButton_auto_classify.clicked.connect(self.batch_auto_classify)
		self.database_tools.pushButton_only_tag_characters.clicked.connect(self.batch_only_tag_characters)
		self.database_tools.pushButton_export_images.clicked.connect(self.batch_export_images)
		self.database_tools.pushButton_purge_manual.clicked.connect(self.batch_purge_manual)
		self.database_tools.pushButton_cleanup_rejected_manual_tags.clicked.connect(self.batch_cleanup_rejected_manual_tags)
		self.database_tools.pushButton_apply_filtering.clicked.connect(self.batch_apply_filtering)
		self.database_tools.pushButton_apply_replacement_to_sentence.clicked.connect(self.batch_apply_replacement_to_sentence)
		self.database_tools.pushButton_discard_image.clicked.connect(self.batch_discard_image)
		self.database_tools.pushButton_open_in_default_program.clicked.connect(self.open_default_program)
		self.database_tools.pushButton_popup_image.clicked.connect(self.pop_up_image)
  
	def update_highlight_tags(self):
		split_text = [t.strip() for t in self.tags_view.lineEdit_tag_highlight.text().split(",")]
		self.current_highlight_tag = [t for t in split_text if t] # make sure tags are not blank strings
		self.update_tags_view()

	@Slot()
	def refresh_tags_frequency(self):
		frequency = self.db.get_frequency_of_all_tags()
		category = self.database_tools.comboBox_frequency_sort.currentText()

		if category != "ALL":
			frequency = [tag_tuple for tag_tuple in frequency if any([tag_tuple[0] in tags["high"]+tags["low"]+tags["tags"] for sub_category, tags in tag_categories.TAG_CATEGORIES[category].items()])]

		refresh_model = FrequencyTagsView(frequency)
		self.database_tools.listView_tags_frequency.setModel(refresh_model)
		self.database_tools.listView_tags_frequency.doubleClicked.connect(self.tag_from_tags_frequency_selected)

	@Slot()
	def tag_from_tags_frequency_selected(self, index):
		if not index.isValid():
			return False
		tag = self.database_tools.listView_tags_frequency.model().data(index, QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
		all_corresponding_images = [] # list of a tuple corresponding to (db_image_index, model_index)
		for base_index in range(self.image_view.listView_groups.model().rowCount()):
			index = self.image_view.listView_groups.model().index(base_index, 0)
			db_index = int(self.image_view.listView_groups.model().itemData(index)[0])
			if tag in self.db.images[db_index].get_full_tags():
				all_corresponding_images.append((db_index, index))
		if not all_corresponding_images:
			parameters.log.info("No images in the groups view has this tag")
			return False

		self.apply_selection_gradient([x[1] for x in all_corresponding_images])
		self.update_selected_images_changed([x[0] for x in all_corresponding_images])



	@Slot()
	def save_database_button(self):
		self.save_current_images()
		if self.db.get_saving_dict() == self.db_history[self.db_history_last_saved_index][0].get_saving_dict():
			parameters.log.info("No changes detected in the database")
			return False
		self.db.save_database()
		self.db_history_last_saved_index = len(self.db_history)-1

	def get_selected_indexes_right_panel(self) -> list[int]:
		result = []
		match self.database_tools.comboBox_selection.currentText():
			case "Current Selection":
				return self.current_images
			case "Visible Images":
				for base_index in range(self.image_view.listView_groups.model().rowCount()):
					try:
						result.append(int(self.image_view.listView_groups.model().itemData(self.image_view.listView_groups.model().index(base_index, 0))[0]))
					except KeyError:
						return []
				return result
			case "Database":
				result = [i for i in range(len(self.db.images))]
				return result
		parameters.log.error("Incorrect Combobox selected text")

	def get_selected_indexes_frequency_tab(self) -> list[int]:
		result = []
		match self.database_tools.comboBox_batch_selection_frequency.currentText():
			case "Current Selection":
				return self.current_images
			case "Visible Images":
				for base_index in range(self.image_view.listView_groups.model().rowCount()):
					try:
						result.append(int(self.image_view.listView_groups.model().itemData(self.image_view.listView_groups.model().index(base_index, 0))[0]))
					except KeyError:
						return []
				return result
			case "Database":
				result = [i for i in range(len(self.db.images))]
				return result
		parameters.log.error("Incorrect Combobox selected text")

	# all replace buttons and related issues
	@Slot()
	def create_replace_line(self):
		one_widget = QWidget()
		h_layout = QHBoxLayout()
		first_line_edit = QLineEdit()
		first_line_edit.setCompleter(self.completer)
		h_layout.addWidget(first_line_edit)
		h_layout.addWidget(QLabel("->"))
		second_line_edit = QLineEdit()
		second_line_edit.setCompleter(self.completer)
		h_layout.addWidget(second_line_edit)
		one_widget.setLayout(h_layout)
		self.replace_lines.append(one_widget)
		self.base_replace_layout.insertWidget(0, one_widget)

	@Slot()
	def remove_last_replace_line(self):
		if len(self.replace_lines) < 1:
			parameters.log.info("No replace line to remove")
			return False
		x = self.replace_lines.pop(-1)
		self.base_replace_layout.removeWidget(x)
		x.hide()
		x.destroy()

	# replace button
	@Slot()
	def replace_tags(self):
		def apply_replace(image_index):
			for line in self.replace_lines:
				from_tags = [tag.strip() for tag in line.layout().itemAt(0).widget().text().split(',') if tag != ""]
				to_tags = [tag.strip() for tag in line.layout().itemAt(2).widget().text().split(',') if tag != ""]
				if len(from_tags) == 0:
					if len(to_tags) == 0:
						parameters.log.info("Blank replace line")
						continue

					# all to_tags need to be added to image
					self.db.images[image_index].append_manual_tags(to_tags)
					self.db.images[image_index].remove_rejected_manual_tags(to_tags)
					self.db.images[image_index].get_full_tags()

				elif len(to_tags) == 0:
					# all from_tags need to be removed from images
					self.db.images[image_index].remove_manual_tags(from_tags)
					self.db.images[image_index].append_rejected_manual_tags(from_tags)
					self.db.images[image_index].get_full_tags()

				elif all([tag in self.db.images[image_index].full_tags for tag in from_tags]):
						self.db.images[image_index].append_manual_tags(to_tags)
						self.db.images[image_index].remove_rejected_manual_tags(to_tags)

						self.db.images[image_index].remove_manual_tags(from_tags)
						self.db.images[image_index].append_rejected_manual_tags(from_tags)
						self.db.images[image_index].get_full_tags()



		if len(self.replace_lines) < 1:
			parameters.log.info("No replacement line created")
			return False
		images_index = self.get_selected_indexes_right_panel()
		if len(images_index) < 1:
			parameters.log.info("No images selected")
			return False

		pool = concurrent.futures.ThreadPoolExecutor()
		for image_index in images_index:
			pool.submit(apply_replace, image_index)
		pool.shutdown(wait=True)
		self.add_db_to_history(f"{len(images_index)} images had their tags replaced with {len(self.replace_lines)} lines")
		self.update_tags_view()




	# OUTPUT
	def init_trigger_tags(self):
		self.database_tools.lineEdit_main_trigger_tag.setText(', '.join([tag for tag in self.db.trigger_tags['main_tags']]))
		self.database_tools.plainTextEdit_secondary_trigger_tags.setPlainText(','.join([tag for tag in self.db.trigger_tags['secondary_tags']]))

	@Slot()
	def save_trigger_tags(self):
		self.db.trigger_tags['main_tags'] = [tag.strip() for tag in self.database_tools.lineEdit_main_trigger_tag.text().split(",")]
		self.db.trigger_tags['secondary_tags'] = [tag.strip() for tag in self.database_tools.plainTextEdit_secondary_trigger_tags.toPlainText().split(",")]

	@Slot()
	def create_txt_files(self):
		self.db.create_txt_files(
			use_trigger_tags=True,
			token_separator=self.database_tools.checkBox_use_separator.isChecked(),
			use_aesthetic_score=self.database_tools.checkBox_export_aesthetic_score.isChecked(),
			use_sentence=self.database_tools.checkBox_use_sentence.isChecked(),
			remove_tags_in_sentence=self.database_tools.checkBox_remove_tags_in_sentence.isChecked(),
			sentence_in_trigger=self.database_tools.checkBox_sentence_separator.isChecked(),
			score_trigger=self.database_tools.checkBox_aesthetic_score_in_token_separator.isChecked()
			)

	@Slot()
	def create_json_file(self):
		self.db.create_json_file(
			use_trigger_tags=True,
			token_separator=self.database_tools.checkBox_use_separator.isChecked(),
			use_aesthetic_score=self.database_tools.checkBox_export_aesthetic_score.isChecked(),
			use_sentence=self.database_tools.checkBox_use_sentence.isChecked(),
			remove_tags_in_sentence=self.database_tools.checkBox_remove_tags_in_sentence.isChecked(),
			sentence_in_trigger=self.database_tools.checkBox_sentence_separator.isChecked(),
			score_trigger=self.database_tools.checkBox_aesthetic_score_in_token_separator.isChecked()
		)

	@Slot()
	def create_sample_toml(self):
		selected_resolution = self.database_tools.comboBox_toml_resolution.currentText()
		resolution_dict = {
      		"SDXL":	(1024, 1024, 64), 
			"SD1.5":(768, 768, 64), 
			"SD1.0":(512,512, 64), 
			"Custom":(parameters.PARAMETERS['custom_export_width'], 
						parameters.PARAMETERS['custom_export_height'], 
						parameters.PARAMETERS['custom_export_bucket_steps'])
        }
		if selected_resolution in resolution_dict:
			res_info = resolution_dict[selected_resolution]
		else:
			parameters.log.error("Resolution string not found")
			res_info = resolution_dict["SDXL"]

		self.db.create_sample_toml(res_info[0], res_info[1], res_info[2])

	@Slot()
	def remove_tags_from_frequency(self):
		images_index = self.get_selected_indexes_frequency_tab()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return False
		if not CustomWidgets.confirmation_dialog(self):
			return False
		tags_to_remove = [self.database_tools.listView_tags_frequency.model().data(self.database_tools.listView_tags_frequency.model().index(model_index),
		                                                                           QtGui.Qt.ItemDataRole.DisplayRole).split(':', maxsplit=1)[1].strip()
		                  for model_index in range(self.database_tools.listView_tags_frequency.model().rowCount())]
		for index in images_index:
			self.db.images[index].remove_manual_tags(tags_to_remove)
			self.db.images[index].append_rejected_manual_tags(tags_to_remove)
		self.add_db_to_history(f"{len(images_index)} images had {len(tags_to_remove)} tags removed in the frequency tab: {self.database_tools.comboBox_frequency_sort.currentText()}")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_auto_tags(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return False
		if not CustomWidgets.confirmation_dialog(self):
			return False
		self.db.tag_images([self.db.images[i].path for i in images_index])
		self.add_db_to_history(f"{len(images_index)} images were auto-tagged")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_auto_score(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if not CustomWidgets.confirmation_dialog(self):
			return False
		self.db.score_images([self.db.images[i].path for i in images_index])
		self.add_db_to_history(f"{len(images_index)} images were auto-scored")
		if self.current_images:
			self.init_tags_view(self.current_images)
	@Slot()
	def batch_refresh_online_tags(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if not CustomWidgets.confirmation_dialog(self):
			return False
		self.db.refresh_unsafe_tags(images_index)
		self.add_db_to_history(f"{len(images_index)} images had their online tags refreshed")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_reset_manual_score(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if not CustomWidgets.confirmation_dialog(self):
			return False
		for i in images_index:
			self.db.images[i].reset_score()
		self.add_db_to_history(f"{len(images_index)} images had their manual score reset")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_auto_classify(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if not CustomWidgets.confirmation_dialog(self):
			return False
		self.db.classify_images([self.db.images[i].path for i in images_index])
		self.add_db_to_history(f"{len(images_index)} images were reclassified")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_only_tag_characters(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if not CustomWidgets.confirmation_dialog(self):
			return False
		self.db.character_only_tag_images([self.db.images[i].path for i in images_index])
		self.add_db_to_history(f"{len(images_index)} images were only characters auto-tagged")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_purge_manual(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if not CustomWidgets.confirmation_dialog(self):
			return False
		self.db.purge_manual_tags(images_index)
		self.add_db_to_history(f"{len(images_index)} images had their manual data purged")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_cleanup_rejected_manual_tags(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		self.db.cleanup_images_rejected_tags(images_index)
		self.add_db_to_history(f"{len(images_index)} images had their rejected manual tags cleaned-up")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_export_images(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return False

		export_path_dialog = InputDialog()
		export_path_dialog.setWindowTitle(f"Input path to export {len(images_index)} images")
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
		export_group_dialog.setToolTip("If no group is specified, it won't add images to the group and it will copy the images to the root folder of the database.")
		if export_group_dialog.exec() == QDialog.DialogCode.Accepted:
			group_input = export_group_dialog.input_field.text()
		else:
			parameters.log.warning("No specified group")
			return False
		self.db.export_database(images_index, path_input, group_input)

	@Slot()
	def batch_apply_filtering(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if len(images_index)/len(self.db.images) > 0.8:
			self.db.filter_all()
		else:
			[self.db.images[i].filter() for i in images_index]
		self.add_db_to_history(f"{len(images_index)} images had filtering applied")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_apply_replacement_to_sentence(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		parameters.log.warning("Filter sentences is not yet implemented")
		if len(images_index)/len(self.db.images) > 0.8:
			self.db.filter_sentence_all()
		else:
			[self.db.images[i].filter_sentence() for i in images_index]
		self.add_db_to_history(f"{len(images_index)} images had their sentence filtered")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def batch_discard_image(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid for batch modification")
			return
		if len(images_index)>1:
			if not CustomWidgets.confirmation_dialog(self, f"You selected {len(images_index)} images to discard.\nAre you sure you want to discard them ?\n\nTip: This button is affected by the 'apply to:' setting at the top right of the window."):
				return False
		files.export_images([self.db.images[i].path for i in images_index if os.path.exists(self.db.images[i].path)], self.db.folder, "TEMP_DISCARDED")
		if self.current_images:
			self.init_tags_view(self.current_images)

	@Slot()
	def open_default_program(self):
		images_index = self.get_selected_indexes_right_panel()
		if not images_index:
			parameters.log.warning("No images were valid to open in an external program")
			return
		if len(images_index)>1:
			if not CustomWidgets.confirmation_dialog(self, f"You selected {len(images_index)} images to open.\nAre you sure you want to open them ?\n\nTip: This button is affected by the 'apply to:' setting at the top right of the window."):
				return False
		for index in images_index:
			image_path = self.db.images[index].path
			if not os.path.exists(image_path):
				parameters.log.info(f"Image doesn't exist: {image_path}")
				continue
			if parameters.PARAMETERS["external_image_editor_path"]:
				subprocess.Popen([parameters.PARAMETERS["external_image_editor_path"], image_path])
			else:
				os.startfile(image_path)

	def on_key_press(self, event, list_view):
		if event.key() == QtCore.Qt.Key.Key_W:
			parameters.log.info("Pressed Key")
			selected_index = list_view.currentIndex()
			if selected_index.isValid():
				webbrowser.open(f"https://danbooru.donmai.us/wiki_pages/{selected_index.data(QtGui.Qt.ItemDataRole.DisplayRole).replace(' ', '_')}")
		else:
			super().keyPressEvent(event)

	def keyPressEvent(self, event):
		# CTRL+S: save database, maybe use '&' for the keyboard modifier
		if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier and event.key() == QtCore.Qt.Key.Key_S:
			self.save_database_button()
		# LEFT: go previous image
		elif event.key() == QtCore.Qt.Key.Key_Left and self.stacked_widget.currentIndex() == 1:
			self.clicked_go_left_button()
		# RIGHT: go previous image
		elif event.key() == QtCore.Qt.Key.Key_Right and self.stacked_widget.currentIndex() == 1:
			self.clicked_go_right_button()
		else:
			super().keyPressEvent(event)

	def add_db_to_history(self, short_description="default name"):
		"""if self.history_buttons.checkedId() != 0:
			current_id = self.history_buttons.checkedId()
			parameters.log.info("before remove history from")
			self.remove_history_starting_from(current_id)
			parameters.log.info("after remove history from")
			self.history_buttons.button(0).setChecked(True)
			self.database_tools.scrollAreaWidgetContents_history.update()
			parameters.log.info("after update")
		self.db_history.append((copy.deepcopy(self.db), short_description))
		self.add_history_view(len(self.db_history))"""

	def init_history_view(self):
		self.history_buttons = QButtonGroup()
		self.history_buttons.addButton(QRadioButton(f"Most Recent"), id=0)
		self.history_buttons.button(0).setChecked(True)
		self.history_buttons.idClicked.connect(self.change_to_history)
		self.database_tools.scrollAreaWidgetContents_history.layout().addWidget(self.history_buttons.button(0))
		self.add_history_view(1)
		self.database_tools.tabWidget.setTabEnabled(4, False)

	def add_history_view(self, history_index):
		#parameters.log.info(f"history_index: {history_index}")
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
		parameters.log.info("Len of the db_history: "+str(len(self.db_history)))
		parameters.log.info("Len of the button_group: "+str(len(self.history_buttons.buttons())))

	@Slot()
	def change_to_history(self, history_index):
		parameters.log.info(history_index)
		if history_index <= 0: #
			self.db = self.saved_recent_db
			self.clear_all()
			return
		self.clear_all()
		self.saved_recent_db = self.db
		self.db = self.db_history[history_index-1][0]


	def clear_all(self):
		self.clear_left_panel()
		self.clear_tags_panel()

	def clear_left_panel(self):
		self.image_view.comboBox_group_name.setCurrentIndex(0)
		self.stacked_widget.setCurrentIndex(0)
		self.image_view.checkBox_single_selection_mode.setChecked(False)

	def clear_tags_panel(self):
		self.current_images: list[int] = []
		self.common_image: ImageDatabase = None
		self.uncommon_added_tags: list[tuple[str, float]] = []
		self.uncommon_rejected_tags: list[tuple[str, float]] = []

		self.update_review(False)
		self.update_labels(tags_len= 0,
                  token_len = 0,
                  image_path= "",
                  sentence_len= 0)
		self.update_single_image_tags(ImageDatabase())



	@Slot()
	def pop_up_image(self):
		if not self.current_images:
			parameters.log.info("No images are selected.")
			return False
		if not isinstance(self.popup_window, bool):
			if self.popup_window.isVisible():
				self.popup_window.hide()
				self.popup_window = False
				return False
			if self.popup_window.isHidden():
				self.popup_window.show()
				self.popup_window.update_image(self.db.images[self.current_images[0]].path)
				return True
		self.popup_window = CustomWidgets.ImageWindow(self.db.images[self.current_images[0]].path)
		self.popup_window.show()

	def update_pop_up_image(self, selected_indexes):
		if isinstance(self.popup_window, bool):
			return False
		if self.popup_window.isHidden():
			return False
		if not selected_indexes:
			return False

		if len(selected_indexes) == 1:
			self.popup_window.update_image(self.db.images[selected_indexes[0]].path)
		elif any([x not in self.current_images for x in selected_indexes]):
			new_indexes = [x for x in selected_indexes if x not in self.current_images]
			self.popup_window.update_image(self.db.images[new_indexes[-1]].path)
		elif any([x not in selected_indexes for x in self.current_images]):
			self.popup_window.update_image(self.db.images[selected_indexes[0]].path)


