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
    param_tagger_download_folders = ["caformer_folder", "swinv2v3_folder", "aesthetic_folder", 
                                     "classifier_folder", "completeness_folder", "person_detect_folder", 
                                     "head_detect_folder", "hand_detect_folder", "text_detect_folder", 
                                     "eva02_large_v3_folder"]
    tagger_huggingface_name = ["Caformer", "Swinv2v3", "anime_aesthetic", 
                               "anime_classifier", "anime_completeness", "detect_people", 
                               "detect_head", "detect_hand", "detect_text",
                               "Eva02_largev3"]
    
    # these are subsets of the hfnames above used to know which dataloader can be shared across models
    swinbased_models = ["Eva02_largev3", "Swinv2v3"]
    anime_classifier_models = ["anime_aesthetic", "anime_classifier", "anime_completeness"]
    
    # basic checks
    if len(path_set) < 1: # check if we have data to tag
        parameters.log.error("No images are going to get tagged")
        return results

    for t in tagging_models: # check if the models used for tagging are valid
        if t == "jpeg_artifacts":
            continue # this is an algorithm ran by another section, ignore it
        if t not in tagger_huggingface_name:
            parameters.log.error(f"{t} is not a currently supported tagger, please check")
            return results
    
    # we build a shared dataloader if applicable, saves some time when running multiple models of similar types
    SW_tagger_datset = None
    classifier_dataset = None
    
    def count_overlaps(inventory_list, item_list):
        return [m in inventory_list for m in item_list].count(True)
    
    if 1 < count_overlaps(tagging_models, swinbased_models):
        parameters.log.info("creating reusable dataloader for SW model types")
        f_args = wd14_based_taggers.FictionnalArgs(image_paths, "", "", interpolation="bicubic")
        f_args.add_args_for_tagger(0, 0)
        SW_tagger_datset = wd14_based_taggers.build_dataset(f_args.trans, f_args.data, f_args.batch_size, f_args.num_workers, use_bgr=True)
    if 1 < count_overlaps(tagging_models, anime_classifier_models):
        parameters.log.info("creating reusable dataloader for anime-classifier model types")
        f_args = wd14_based_taggers.FictionnalArgs(image_paths, "", "")
        classifier_dataset = wd14_based_taggers.build_dataset(f_args.trans, f_args.data, f_args.batch_size, f_args.num_workers)
    
    for model_hf_name, download_loc in zip(tagger_huggingface_name, param_tagger_download_folders):
        if model_hf_name in tagging_models: # if the model is the one we want to use
            model_folder = os.path.join(parameters.MAIN_FOLDER, parameters.PARAMETERS[download_loc])
            
            # check if the model directory contains the tagger/detection models
            #use cocurrent threads to download model if it doesn't exist
            
            if not os.path.exists(model_folder):
                parameters.log.info(f"downloading model: {model_hf_name}, to {model_folder}")
                files.download_model(model_hf_name)
            
            # tag models based on the settings
            match model_hf_name:
                case "anime_aesthetic":
                    results[model_hf_name] = wd14_based_taggers.image_scoring(image_paths, model_folder, 
                                                                              reused_dataloader=classifier_dataset, model_name=model_hf_name)
                case "anime_classifier":
                    results[model_hf_name] = wd14_based_taggers.image_classify(image_paths, model_folder, 
                                                                               reused_dataloader=classifier_dataset, model_name=model_hf_name)
                case "anime_completeness":
                    results[model_hf_name] = wd14_based_taggers.image_completeness(image_paths, model_folder, 
                                                                                   reused_dataloader=classifier_dataset, model_name=model_hf_name)
                case "Swinv2v3":
                    # check for optional args
                    characters_only = False
                    
                    if extra_args and "Swinv2v3" in extra_args:
                        characters_only = extra_args["Swinv2v3"].get("characters_only", False)
                    
                    results[model_hf_name] = wd14_based_taggers.swinv2v3_tagging(
                        image_paths, model_folder, character_only=characters_only, 
                        interpolation=parameters.PARAMETERS["downsample_interpolation_method"], 
                        reused_dataloader=SW_tagger_datset, model_name=model_hf_name)
                case "Caformer":
                    #with warnings.catch_warnings():
                    #    warnings.simplefilter("ignore")
                    results[model_hf_name] = caformer_tagger.caformer_tagging(image_paths, model_folder)
                case "detect_people":
                    results[model_hf_name] = detection_taggers.detect_people(image_paths, model_folder)
                case "detect_head":
                    results[model_hf_name] = detection_taggers.detect_head(image_paths, model_folder)
                case "detect_hand":
                    results[model_hf_name] = detection_taggers.detect_hand(image_paths, model_folder)
                case "detect_text":
                    results[model_hf_name] = detection_taggers.detect_text(image_paths, model_folder)
                case "Eva02_largev3":
                    results[model_hf_name] = wd14_based_taggers.eva02_large_v3_tagging(image_paths, model_folder, 
                                                                                       reused_dataloader=SW_tagger_datset, model_name=model_hf_name)
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
    