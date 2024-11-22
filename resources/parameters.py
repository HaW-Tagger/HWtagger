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
    SWINV2V3 = "Swinv2v3"
    CAFORMER = "Caformer"
    CLASSIFY = "anime_classifier"
    AESTHETIC = "anime_aesthetic"
    WDEVA02LARGEV3 = "Eva02_largev3"

log = logging.getLogger("rich")

DATABASE_FILE_NAME = "database.json"
SETTINGS_FILE_NAME = "settings.json"

# NOT TO CHANGE
IMAGES_EXT = (".png", ".jpeg", ".jpg", ".PNG", ".JPEG", ".JPG")
MAIN_FOLDER = os.getcwd()



default_discard_folder = ["TO EDIT", "to edit", "DISCARDED", "discarded", "DUPLICATES", "duplicates", "ADJUST_RATIO", "adjust_ratio", "DISCARDED_ANIMATION"]

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
    'hide_sentence_in_view': True,
    'default_path': "",
    'view_load_images': True,
    'view_placeholder_default_path': "resources/images/default.jpg",
    'doubling_image_thumbnail_max_size': False,
    'danbooru_tag_wiki_lookup': True
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
    'caformer_folder': "models/ML-danbooru-caformer/",
    'caformer_threshold': 0.70,
    'max_batch_size': 8,
    'aesthetic_folder':"models/anime_aesthetic/",
    'classifier_folder':"models/anime_classifier/",
    "person_detect_folder": "models/person_detect/",
    "head_detect_folder": "models/head_detect/",
    "hand_detect_folder": "models/hand_detect/",
    "completeness_folder": "models/anime_completeness/",
    "detection_small_resolution": 512,
    "eva02_large_v3_folder": "models/wd-eva02-large-tagger-v3/",
    "wdeva02_large_threshold": 0.35
}


default_parameters['Database'] = {
    'main_database_folder': "database/",
    'keep_token_tags_separator': "|||",
    'remove_transparency_from_images': True,
    'discard_folder_name_from_search': default_discard_folder,
    'max_images_loader_thread' : 24,
    'max_4k_pixel_save_multiplier': 10,
    'max_databases_view_backup': 5,
    'frequency_rare_tag_threshold': 0.02
}
default_parameters['Filter'] = {
    'deactivate_filter': False,
    'filter_remove_series': True,
    'filter_remove_metadata': False,
    'filter_remove_characters': False
}
default_parameters['Exporting'] = {
    'custom_export_height': 1024,
    'custom_export_width': 1024,
    'custom_export_bucket_steps': 64,
    'toml_sample_max_count': 5,
    'export_negative_prompt': "monochrome, greyscale, furry, pony, blurry, simple background",
    'export_prepend_positive_prompt': "score_7_up, source_anime",
    'export_sample_steps': 24,
    'export_cfg_scale': 7,

    'custom_scores_6': "masterpiece",
    'custom_scores_5': "best",
    'custom_scores_4': "great",
    'custom_scores_3': "good",
    'custom_scores_2': "average",
    'custom_scores_1': "worse",
    'custom_scores_0': "worst"
}

def create_config():
    default_config = configparser.ConfigParser()

    for section in default_parameters.keys():
        default_config.add_section(section)
        for option in default_parameters[section].keys():
            if option == "discard_folder_name_from_search":
                default_config[section][option] = ",".join(default_parameters[section][option])
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
                    config_values[option] = [AvailableTaggers[tagger.strip()] for tagger in x.split(",")]
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
        log.warning("The keep_token_tags_separator option should always be something unique, if you don't use this, make it something long and unique because it could create problems in functions that does micro checks relating to it: We use |||")

    return config_values

PARAMETERS = read_config()