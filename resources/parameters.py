import enum
import logging
import os
import configparser
from rich.logging import RichHandler
FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

class AvailableTaggers(enum.Enum):
	# Currently full and characters is not used but maybe in the future
	SWINV2V2 = "Swinv2v2", "Full"
	SWINV2V2_CHARACTERS = "Swinv2v2", "Characters"
	SWINV2V3 = "Swinv2v3", "Full"
	SWINV2V3_CHARACTERS = "Swinv2v3", "Characters"
	CAFORMER = "Caformer", "Full"


log = logging.getLogger("rich")

DATABASE_FILE_NAME = "database.json"

# NOT TO CHANGE
IMAGES_EXT = (".png", ".jpeg", ".jpg", ".PNG", ".JPEG", ".JPG")
MAIN_FOLDER = os.getcwd()

default_discard_folder = str(",".join(["TO EDIT", "to edit", "DISCARDED", "discarded", "DUPLICATES", "duplicates", "ADJUST_RATIO", "adjust_ratio", "DISCARDED_ANIMATION"]))

default_parameters = dict()
default_parameters['General'] = {
	'similarity_threshold': 0.7,
	'external_image_editor_path': ""
}
default_parameters['Interface'] = {
	'font_name': "Segoe Ui",
	'font_size': 12,
	'image_load_size': 128,
	'database_view_tooltip': True,
	'double_click': True,
}
default_parameters['Taggers'] = {
	'automatic_tagger': [AvailableTaggers.SWINV2V3, AvailableTaggers.CAFORMER],
    'swinv2_folder': "models/SwinV2/",
    'swinv2v3_folder': "models/SwinV2v3/",
    'swinv2_preference': "v2v3", # v2v2 or v2v3
    'swinv2_threshold': 0.35,
    'swinv2_enable_character': True,
    'swinv2_character_threshold': 0.5,
    'swinv2_character_count_threshold': 250,
    'caformer_folder': "models/ML-danbooru-caformer",
    'caformer_threshold': 0.70,
    'max_batch_size': 8,
    'aesthetic_folder':"models/anime_aesthetic/",
    'classifier_folder':"models/anime_classifier/"
}
default_parameters['Database'] = {
	'main_database_folder': "database/",
	'keep_token_tags_separator': "|||",
	'remove_transparency_from_images': True,
	'discard_folder_name_from_search': default_discard_folder,
	'max_images_loader_thread' : 24,
	'max_4k_pixel_save_multiplier': 10
}
default_parameters['Filter'] = {
	'filter_remove_series': True,
	'filter_remove_metadata': False,
	'filter_remove_characters': False
}


def create_config():
	default_config = configparser.ConfigParser()
	for section in default_parameters.keys():
		default_config.add_section(section)
		for option in default_parameters[section].keys():
			if option == "discard_folder_name_from_search":
				default_config[section][option] = default_parameters[section][option]
			elif option == "automatic_tagger":
				default_config[section][option] = ",".join([x.name for x in default_parameters[section][option]])
			else:
				default_config[section][option] = str(default_parameters[section][option])
	# Write the configuration to a file
	with open('config.ini', 'w') as configfile:
		default_config.write(configfile)

def save_config():
	config = configparser.ConfigParser()
	# Add sections and key-value pairs
	for section in default_parameters.keys():
		config.add_section(section)
		for option in default_parameters[section].keys():
			if option == "discard_folder_name_from_search":
				config[section][option] = ",".join(PARAMETERS[option])
			elif option == "automatic_tagger":
				config[section][option] = ",".join([x.name for x in PARAMETERS[option]])
			else:
				config[section][option] = str(PARAMETERS[option])

	# Write the configuration to a file
	with open('config.ini', 'w') as configfile:
		config.write(configfile)

	log.info("Saved Config")

def read_config():
	if not os.path.exists('config.ini'):
		create_config()

	# Create a ConfigParser object
	config = configparser.ConfigParser()

	# Read the configuration file
	config.read('config.ini')

	# DICT
	config_values=dict()
	for section in default_parameters.keys():
		for option in default_parameters[section].keys():
			if option == "discard_folder_name_from_search":
				config_values[option] = [t.strip() for t in config.get(section, option, fallback=default_parameters[section][option]).split(",")]
			elif option == "automatic_tagger":
				x = config.get(section, option, fallback=default_parameters[section][option])
				if isinstance(x, str):
					config_values[option] = [AvailableTaggers[t.strip()] for t in x.split(",")]
				else:
					config_values[option] = x
			elif isinstance(default_parameters[section][option], float):
				config_values[option] = config.getfloat(section, option, fallback=default_parameters[section][option])
			elif isinstance(default_parameters[section][option], bool):
				config_values[option] = config.getboolean(section, option, fallback=default_parameters[section][option])
			elif isinstance(default_parameters[section][option], int):
				config_values[option] = config.getint(section, option, fallback=default_parameters[section][option])
			else:
				config_values[option] = config.get(section, option, fallback=default_parameters[section][option])

	if len(config_values['keep_token_tags_separator']) < 2:
		log.warning("The keep_token_tags_separator option should always be something unique, if you don't use this, make it something long and unique because it could create problems in functions that does micro checks realting to it: We use |||")

	return config_values

PARAMETERS = read_config()