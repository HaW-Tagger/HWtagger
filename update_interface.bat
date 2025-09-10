
call venv\Scripts\activate

pyside6-uic interfaces/interface.ui -o interfaces/interface.py
pyside6-uic interfaces/databaseToolsBase.ui -o interfaces/databaseToolsBase.py
pyside6-uic interfaces/imageViewBase.ui -o interfaces/imageViewBase.py
pyside6-uic interfaces/tagsViewBase.ui -o interfaces/tagsViewBase.py
pyside6-uic interfaces/dataset_cleaning.ui -o interfaces/dataset_cleaning.py
pyside6-uic interfaces/global_database_view.ui -o interfaces/global_database_view.py
pyside6-uic interfaces/image_tools.ui -o interfaces/image_tools.py
pyside6-uic interfaces/statistics.ui -o interfaces/statistics.py
pyside6-uic interfaces/popupscaledlabel.ui -o interfaces/popupscaledlabel.py
pyside6-uic interfaces/global_database_item.ui -o interfaces/global_database_item.py
pyside6-uic interfaces/databaseCreationTab.ui -o interfaces/databaseCreationTab.py
pyside6-uic interfaces/outputBase.ui -o interfaces/outputBase.py
pyside6-uic interfaces/rectangleTagsBase.ui -o interfaces/rectangleTagsBase.py

