import os, sys
import warnings

from resources import parameters
import tools
from tools import files, wd14_based_taggers, caformer_tagger, detection_taggers
 

def multi_model_caller(image_paths, tagging_models, extra_args=None):
    # extra args is a dictionary that sends optional arguments to the models.
    path_set = set(image_paths)
    untagged_images_paths = {}
    results = {}
    
    # here, we list the name of the key that stores the folder location and the model invoked
    # the list of hf_names are used to identify what to download and are used as keys for the results
    param_tagger_download_folders = ["caformer_folder", "swinv2v3_folder", "aesthetic_folder", "classifier_folder", 
                                     "completeness_folder", "person_detect_folder", "head_detect_folder", "hand_detect_folder",
                                     "eva02_large_v3_folder"]
    tagger_huggingface_name = ["Caformer", "Swinv2v3", "anime_aesthetic", "anime_classifier", 
                               "anime_completeness", "detect_people", "detect_head", "detect_hand",
                               "Eva02_largev3"]
    
    # basic checks
    if len(path_set) < 1: # check if we have data to tag
        parameters.log.error("No images are going to get tagged")
        return results

    for t in tagging_models: # check if the models used for tagging are valid
        if t not in tagger_huggingface_name:
            parameters.log.error(f"{t} is not a currently supported tagger, please check")
            return results
    
    
    for model_hf_name, download_loc in zip(tagger_huggingface_name, param_tagger_download_folders):
        if model_hf_name in tagging_models: # if the model is the one we want to use
            model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS[download_loc])
            
            # check if the model directory contains the tagger/detection models
            #use cocurrent threads to download model if it doesn't exist
            if not os.path.exists(model_folder):
                parameters.log.info(f"downloading model: {model_hf_name}")
                files.download_model(model_hf_name)
            
            # tag models based on the settings
            match model_hf_name:
                case "anime_aesthetic":
                    results[model_hf_name] = wd14_based_taggers.image_scoring(image_paths, model_folder)
                case "anime_classifier":
                    results[model_hf_name] = wd14_based_taggers.image_classify(image_paths, model_folder)
                case "Swinv2v3":
                    # check for optional args
                    characters_only = False
                    if extra_args and "Swinv2v3" in extra_args:
                        characters_only = extra_args["Swinv2v3"].get("characters_only", False)
                    results[model_hf_name] = wd14_based_taggers.swinv2v3_tagging(image_paths, model_folder, character_only=characters_only)
                case "Caformer":
                    #with warnings.catch_warnings():
                    #    warnings.simplefilter("ignore")
                    results[model_hf_name] = caformer_tagger.caformer_tagging(image_paths, model_folder)
                case "anime_completeness":
                    results[model_hf_name] = wd14_based_taggers.image_completeness(image_paths, model_folder)
                case "detect_people":
                    results[model_hf_name] = detection_taggers.detect_people(image_paths, model_folder)
                case "detect_head":
                    results[model_hf_name] = detection_taggers.detect_head(image_paths, model_folder)
                case "detect_hand":
                    results[model_hf_name] = detection_taggers.detect_hand(image_paths, model_folder)
                case "Eva02_largev3":
                    results[model_hf_name] = wd14_based_taggers.eva02_large_v3_tagging(image_paths, model_folder)
                case "florence_caption":
                    pass
                case _:
                    parameters.log.error(f"Unknown model name, doing nothing")

            # save file path info for what was tagged
            unused_paths = path_set - set(results[model_hf_name].keys())
            if unused_paths:
                untagged_images_paths[model_hf_name] = tuple(unused_paths) # 5his is a tuple so we can use a set later
    
    # print any unused imgae paths
    
    if untagged_images_paths:
        if len({paths for paths in untagged_images_paths.values()}) == 1: # print simplified view if untagged images are all the same paths
            key_list = list(untagged_images_paths.keys())
            parameters.log.error(f"For {key_list}, these files were not added to the database: {untagged_images_paths[key_list[0]]}")
        else: # untagged images are slightly different between tagger, so print per each model
            for k, v in untagged_images_paths.items():
                parameters.log.error(f"For {k}, these files were not added to the database: {v}")
    
    return results
    