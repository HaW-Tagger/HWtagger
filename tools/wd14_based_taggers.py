import os

from PIL import Image

os.environ["XFORMERS_FORCE_DISABLE_TRITON"] = "1"
import warnings
warnings.filterwarnings("ignore")
# onnx is built into pytorch

import torch
import math
import torchvision.transforms.v2 as transforms
import torchvision.transforms.functional as F
from torch.utils.data.dataloader import default_collate
import onnxruntime as ort

from tqdm.auto import tqdm
import numpy as np

from tools import files
from src_files.data.path_dataset import PathDataset_test
from resources import parameters, tag_categories

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PIN_MEMORY = True if torch.cuda.is_available() else False
# onnx verion opset:
# https://github.com/onnx/onnx/blob/main/docs/Versioning.md#released-versions

"""
Notes on this page:
imgClassification and ImageCompleteness works the same, img scoring is similar with additional methods
Thw swin and eva02 are models by smilingwolf so they run the same (use bgr for input)
"""


# for wd14 tagger(s)
IMAGE_SIZE = 448
_LABELS = [
        "3d",
        "anime coloring",
        "comic",
        "illustration",
        "not painting"
    ]
_COMPLETE_LABELS = [
        "polished art",
        "rough art", 
        "monochrome"
    ]

CHARACTERS_COUNT_THRESHOLD = parameters.PARAMETERS["swinv2_character_count_threshold"]

def parse_interpolation(interpolation_str):
    interpolation = interpolation_str.lower()
    if interpolation == 'lanczos':
        return transforms.functional.InterpolationMode.LANCZOS
    elif interpolation == 'area':
        return transforms.functional.InterpolationMode.NEAREST
    elif interpolation == 'bicubic':
        return transforms.functional.InterpolationMode.BICUBIC
    parameters.log.info("Typo or unrecognized interpolation method, defaulting to Bicubic interpolation")
    return transforms.functional.InterpolationMode.BICUBIC
        
def build_dataset(img_transformation, paths=[], bs=4, num_workers=4, use_bgr=False, reused_dataloader=None):
    # imgClassification, Image Completeness
    if reused_dataloader:
        return reused_dataloader
    # swin and other smilingwolf tagger uses bgr: https://huggingface.co/spaces/SmilingWolf/wd-tagger/blob/main/app.py
    dataset = PathDataset_test(paths, img_transformation, convert_bhwc=False, convert_bgr=use_bgr, 
                            to_np=True, fill_transaprent=True)
    loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=num_workers, 
                                        shuffle=False, collate_fn=custom_collate, pin_memory=PIN_MEMORY)
    return loader
class SquarePad:
    def __call__(self, image: Image.Image):
        #https://discuss.pytorch.org/t/how-to-resize-and-pad-in-a-torchvision-transforms-compose/71850/10
        img_shape = image.size
        max_wh = max(img_shape)
        #p_left, p_top = [(max_wh - s) // 2 for s in image.size]
        #p_right, p_bottom = [max_wh - (s+pad) for s, pad in zip(image.size, [p_left, p_top])]
        #padding = (p_left, p_top, p_right, p_bottom)
        pad_left = (max_wh - img_shape[0]) // 2
        pad_top = (max_wh - img_shape[1]) // 2
        padding = (pad_left, pad_top)
        # fill in with white
        
        # resize happens later
        return F.pad(image, padding, (255,255,255), 'constant')


def custom_collate(batch):
    #len_batch = len(batch)
    return default_collate(batch)

class FictionnalArgs:
    def __init__(self, data, dir_path, ckpt, batch_size:int=4, num_workers:int=4, interpolation:str="bicubic", model_name:str="model"):
        self.model_name = model_name
        self.data = data
        self.model_dir = dir_path
        self.model_path = ckpt
        self.batch_size = batch_size
        self.image_size = IMAGE_SIZE
        self.keep_ratio = False # this is not helpful for this model
        self.base_tagger = False
        self.num_workers = min(int(math.ceil(len(data)/batch_size)), num_workers if len(data)>200 else 2)
        # pin_memory is used for the dataloader
        self.use_bgr = False
        
        ####### Note on inerpolation methods ########
        # The best interpolation algorithm to use is usually split between bicubic and lanczos
        # tldr: bicubic for illustrations and digital images (cg, game sc), lanczos for real photos
        
        # koyha_ss uses Inter Area as default, commandline option for lanczos and inter_cubic (aka bicubic)
        # source: check sd-scripts/tools/resize__images_to_resolutions.py
        # wd-14 code (Smilingwolf) uses bicubic, 
        # source: https://huggingface.co/spaces/SmilingWolf/wd-tagger/blob/main/app.py
        
        # I will also list some of the few good notes/info I found on the different interpolation methods
        # Inter area : https://medium.com/@wenrudong/what-is-opencvs-inter-area-actually-doing-282a626a09b3
        self.interpolation_method = parse_interpolation(interpolation)
        self.trans = self.get_transformation_method()
        
    def add_args_for_tagger(self, thresh, char_thresh, char_tag:bool=False, character_only:bool=False, interpolation:str="bicubic", use_bgr:bool=True):
        """_summary_

        Args:
            thresh (_type_): _description_
            char_thresh (_type_): _description_
            char_tag (bool, optional): _description_. Defaults to False.
            character_only (bool, optional): _description_. Defaults to False.
            interpolation (str, optional): supports, "lanczos",  Defaults to "Bicubic".
            use_bgr (bool): enable for smilingwolf made taggers
        """
        self.use_bgr = use_bgr
        self.thresh = thresh
        self.char_thresh = char_thresh
        self.num_classes = 10861 # from v2-v3 config
        self.char_tag = char_tag
        self.keep_ratio = True
        self.character_only = character_only
        self.base_tagger = True
        self.interpolation_method = parse_interpolation(interpolation)
        self.trans = self.get_transformation_method()
             
    def get_transformation_method(self):
        if self.base_tagger: # this is for the basic tagger, swinv2v3
            trans = transforms.Compose([
                # ignore keep ratio bc it has a tendency to add letterboxed and other tags related to borders to tags
                SquarePad(), 
                transforms.Resize((self.image_size, self.image_size), 
                                  interpolation=self.interpolation_method),
            ])
        else:# this is for aesthetic and classifying
            trans = transforms.Compose([
                #square_pad()
                transforms.Resize((self.image_size, self.image_size),
                                interpolation=self.interpolation_method),
                transforms.ToTensor(),
                #transforms.ToPILImage()
            ])
        return trans

class BaseDemo: 
    # https://github.com/kohya-ss/sd-scripts/blob/main/finetune/tag_images_by_wd14_tagger.py
    # infer_batch is different per model, so inheritance takes care of that below
    def __init__(self, args: FictionnalArgs):
        parameters.log.info(f'Creating model {args.model_name}...')
        self.ort_session = ort.InferenceSession(
                    args.model_path,
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.input_name = self.ort_session.get_inputs()[0].name  # should be "input_1:0" 
        self.output_name = self.ort_session.get_outputs()[0].name
        #parameters.log.debug(self.ort_session.get_inputs()[0])

class ImageClassificationDemo(BaseDemo):
    def __init__(self, args):
        super().__init__(args)
        
    @torch.no_grad()  
    def infer_batch(self, loader):
        path_dict = {}
        # original library
        #from imgutils.validate.classify import anime_classify 
        np.set_printoptions(suppress=True)
        for imgs, path_list in tqdm(loader):
            imgs = np.array(imgs)
            #parameters.log.debug(imgs.shape)
            predictions = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            classification = np.array(predictions)
            #parameters.log.debug(classification)
            
            for pth, img_cls in zip(path_list, classification):
                idx = np.argmax(img_cls)
                label_idx =_LABELS[idx]
                label_prob=img_cls[idx]
                
                path_dict[pth]=(label_idx, label_prob)
        return path_dict
     
class ImageCompletenessDemo(BaseDemo):
    def __init__(self, args):
        super().__init__(args)
    
    @torch.no_grad()  
    def infer_batch(self, loader):
        path_dict = {}
        # original library
        #from imgutils.validate.classify import anime_classify 
        np.set_printoptions(suppress=True)
        for imgs, path_list in tqdm(loader):
            imgs = np.array(imgs)
            #parameters.log.debug(imgs.shape)
            predictions = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            classification = np.array(predictions)
            #parameters.log.debug(classification)
            
            for pth, img_cls in zip(path_list, classification):
                idx = np.argmax(img_cls)
                label_idx =_COMPLETE_LABELS[idx]
                label_prob=img_cls[idx]
                #if "2cb0" in pth or "c7d5" in pth or "0c0d" in pth:
                #    parameters.log.debug(pth, label_idx, label_prob)
                path_dict[pth]=(label_idx, label_prob)
        return path_dict

def percentile_to_label(percentile):
    mapping = tag_categories.QUALITY_LABELS_MAPPING
    return_label = "worst"
    for label, threshold in sorted(mapping.items(), key=lambda x: (-x[1], x[0])):
        if percentile >= threshold:
            return_label = label
            break
    return return_label

class ImageScoringDemo(BaseDemo):
    def __init__(self, args):
        super().__init__(args)
        
    @torch.no_grad()  
    def infer_batch(self, loader, model_dir):
        # returns a dict [path] --> label, percentile
        path_dict = {}
        x_file = os.path.join(model_dir, "samples_x.npy")
        y_file = os.path.join(model_dir, "samples_y.npy")
        
        if not os.path.exists(x_file):
            from huggingface_hub import hf_hub_download
            repo_id = 'deepghs/anime_aesthetic'
            model_name = 'swinv2pv3_v0_448_ls0.2_x'
            stacked = np.load(hf_hub_download(
                    repo_id=repo_id,
                    repo_type='model',
                    filename=f'{model_name}/samples.npz',
                ))['arr_0']
            
            x, y = stacked[0], stacked[1]
            #x, y = x[0::4], y[0::4] # slicing using a step of 4, basically reducing the sample size by 4
            np.save(x_file, x[3000::100]) # sliced up to 100 skipping the first 300
            np.save(y_file, y[3000::100])
        x = np.load(x_file)
        y = np.load(y_file)
        #parameters.log.debug(len(x))
        #import matplotlib.pyplot as plt
        #plt.hist(x, bins=100)
        #plt.show()
        
        (x, x_min, x_max), (y, y_min, y_max) = (x, x.min(), x.max()), (y, y.min(), y.max())
        
        def score_to_percentile(score):
            idx = np.searchsorted(x, np.clip(score, a_min=x_min, a_max=x_max))
            if idx < x.shape[0] - 1:
                x0, y0 = x[idx], y[idx]
                x1, y1 = x[idx + 1], y[idx + 1]
                if np.isclose(x1, x0):
                    return y[idx]
                else:
                    return np.clip((score - x0) / (x1 - x0) * (y1 - y0) + y0, a_min=y_min, a_max=y_max)
            else:
                return y[idx]
                
        sorted_values = np.array([v for v in sorted(tag_categories.QUALITY_LABELS_MAPPING.values())])
        sorted_keys = [v[0] for v in sorted(tag_categories.QUALITY_LABELS_MAPPING.items(), key=lambda item: item[1])]
        
        np.set_printoptions(suppress=True)
        for imgs, path_list in tqdm(loader):
            imgs = np.array(imgs)
            #parameters.log.debug(imgs.shape)
            scores = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            
            scores = np.array(scores)
            score = np.sum(np.multiply(scores, np.arange(len(tag_categories.QUALITY_LABELS))[::-1]), axis=1)
            
            
            percentile = [score_to_percentile(s) for s in score]
            labels = [percentile_to_label(p) for p in percentile]
            confidence = scores
            for pth, l, s_perct in zip(path_list, labels, percentile):
                path_dict[pth]=(l, s_perct)
        return path_dict
        
class Swinv2v3TaggingDemo(BaseDemo):
    def __init__(self, args, update_to_eva02=False):
        super().__init__(args)
        # the eva02_large code and Swinv2v3 code is basically the same, so it was refactored
        
        if update_to_eva02:
            tags_df = files.get_pd_eva02_large_tag_frequency()
        else:
            tags_df = files.get_pd_swinbooru_tag_frequency()
       # https://huggingface.co/spaces/SmilingWolf/wd-tagger/tree/main
        name_series = tags_df["name"]
        name_series = name_series.map(lambda x: x.replace("_", " ") if x not in tag_categories.KAOMOJI else x)
        self.tag_names = name_series.tolist()
        self.rating_indexes = list(np.where(tags_df["category"] == 9)[0])
        self.general_indexes = list(np.where(tags_df["category"] == 0)[0])
        self.character_indexes = list(np.where(tags_df["category"] == 4)[0])
        self.general_tag = [self.tag_names[i] for i in self.general_indexes]
        self.character_tags = [self.tag_names[i] for i in self.character_indexes]

        self.whitelist_characters = tag_categories.CHARACTERS_TAG
      
    @torch.no_grad()  
    def infer_batch(self, loader, thresh, char_thresh, num_classes=10861, char_tag=False, character_only=False):
        tag_dict = {}
        #np.set_printoptions(suppress=True)
        for imgs, path_list in tqdm(loader):
            imgs = np.array(imgs)
            probs = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            for f_path, prob_vec in zip(path_list, probs):
                general_prob = prob_vec[self.general_indexes]
                tags = [(tag_name, round(float(prob), 3)) for tag_name, prob in zip(self.general_tag, general_prob) if prob > thresh]
                tags.sort(reverse=True, key=lambda x: x[1])
                
                if char_tag and not character_only:
                    
                    char_prob = prob_vec[self.character_indexes]
                    chars = [(char_name, round(float(prob), 3)) for char_name, prob in zip(self.character_tags, char_prob) 
                                  if prob > char_thresh and char_name in self.whitelist_characters]
                    
                    tags.extend(chars)
                elif char_tag and character_only:
                    char_prob = prob_vec[self.character_indexes]
                    tags = [(char_name, round(float(prob), 3)) for char_name, prob in zip(self.character_tags, char_prob) 
                            if prob > char_thresh and char_name in self.whitelist_characters]
                    
                tag_dict[f_path] = tags

        return tag_dict

""" # attempt to move the caformer code, we couldn't fine the correct corresponding onnx version, + some bugs, so ignore this
class CaformerTaggingDemo(BaseDemo):
    def __init__(self, args):
        super().__init__(args)
        self.class_map_name = args.class_map
        self.ema = False
        self.class_map = None
        self.image_size = 448
        self.load_class_map()
        self.general_tag
        
    def load_class_map(self):
        import json
        with open(self.class_map_name, 'r') as f:
            self.class_map = json.load(f)
            
    @torch.no_grad()
    def infer_batch(self, paths, bs, thresh, char_thresh, num_classes=10861, char_tag=False, character_only=False):
        tag_dict = {}
        
        # check bgr
        
        dataset = PathDataset_test(paths, self.trans, convert_bhwc=False, convert_bgr=False, to_np=True, fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset,batch_size=bs, num_workers=min(int(len(paths)/bs), 4 if len(paths)>200 else 2), shuffle=False, collate_fn=custom_collate, pin_memory=True if torch.cuda.is_available() else False)

        #np.set_printoptions(suppress=True)
        for imgs, path_list in tqdm(loader):
            imgs = np.array(imgs)
            probs = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            for f_path, prob_vec in zip(path_list, probs):
                general_prob = prob_vec
                tags = [(tag_name, round(float(prob), 3)) for tag_name, prob in zip(self.general_tag, general_prob) if prob > thresh]
                
                tag_dict[f_path] = tags

        return tag_dict

def caformer_tagger(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"]):
    ckpt = os.path.join(model_pth, "model.onnx")
    parameters.log.info(f"Loading Caformer, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size)
    demo = CaformerTaggingDemo(args)
    tag_dict = demo.infer_batch(args.data, args.batch_size, args.model_dir)
    return tag_dict
"""

def image_scoring(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"], reused_dataloader=None, model_name="image_scoring"):
    #https://huggingface.co/deepghs/anime_aesthetic/tree/main/swinv2pv3_v0_448_ls0.2_x
    
    ckpt = os.path.join(model_pth, "model.onnx")
    parameters.log.info(f"Loading SwinV2_aesthetic, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size, model_name=model_name)
    demo = ImageScoringDemo(args)
    dataloader = build_dataset(args.trans, args.data, args.batch_size, args.num_workers, args.use_bgr, reused_dataloader)
    tag_dict = demo.infer_batch(dataloader, args.model_dir)
    
    return tag_dict

def image_classify(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"], reused_dataloader=None, model_name="image_classfier"):
    # model is the base model used in imguitls
    # https://huggingface.co/deepghs/anime_classification/tree/main/mobilenetv3_v1.3_dist
    ckpt = os.path.join(model_pth, "model.onnx") 
    parameters.log.info(f"Loading Image source classifer, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size, model_name=model_name)
    demo = ImageClassificationDemo(args)
    dataloader = build_dataset(args.trans, args.data, args.batch_size, args.num_workers, args.use_bgr, reused_dataloader)
    tag_dict = demo.infer_batch(dataloader)
    return tag_dict

def image_completeness(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"], reused_dataloader=None, model_name="image_completeness"):
    # model is one used by imgutils
    # https://huggingface.co/deepghs/anime_completeness/tree/main/caformer_s36_v2.2
    ckpt = os.path.join(model_pth, "model.onnx") 
    parameters.log.info(f"Loading Image completeness identifier, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size, model_name=model_name)
    demo = ImageCompletenessDemo(args)
    dataloader = build_dataset(args.trans, args.data, args.batch_size, args.num_workers, args.use_bgr, reused_dataloader)
    tag_dict = demo.infer_batch(dataloader)
    return tag_dict

def swinv2v3_tagging(data, model_pth, character_only=False, batch_size=parameters.PARAMETERS["max_batch_size"], 
                     interpolation="bicubic", reused_dataloader=None, model_name="Swinv2 tagging"):
    threshold=parameters.PARAMETERS["swinv2_threshold"], 
    character_threshold=parameters.PARAMETERS["swinv2_character_threshold"],
    ckpt = os.path.join(model_pth, "model.onnx") 
    CHARACTERS = parameters.PARAMETERS["swinv2_enable_character"]
    parameters.log.info(f"Loading SwinV2, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size, model_name=model_name)
    args.add_args_for_tagger(threshold, character_threshold, CHARACTERS, character_only, interpolation)
    demo = Swinv2v3TaggingDemo(args)
    dataloader = build_dataset(args.trans, args.data, args.batch_size, args.num_workers, args.use_bgr, reused_dataloader)
    tag_dict = demo.infer_batch(dataloader, args.thresh ,args.char_thresh, args.num_classes, args.char_tag, args.character_only)
    return tag_dict

def eva02_large_v3_tagging(data, model_pth, character_only=False, batch_size=parameters.PARAMETERS["max_batch_size"], 
                           interpolation="bicubic", reused_dataloader=None, model_name="Eva02 tagging"):
    threshold=parameters.PARAMETERS["wdeva02_large_threshold"],
    character_threshold=parameters.PARAMETERS["swinv2_character_threshold"],
    ckpt = os.path.join(model_pth, "wd-eva02-large-tagger-v3.onnx")
    CHARACTERS = parameters.PARAMETERS["swinv2_enable_character"]
    parameters.log.info(f"Loading wd-eva02-large-tagger-v3, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt,  batch_size, model_name=model_name)
    args.add_args_for_tagger(threshold, character_threshold, CHARACTERS, character_only, interpolation)
    demo = Swinv2v3TaggingDemo(args, update_to_eva02=True)
    dataloader = build_dataset(args.trans, args.data, args.batch_size, args.num_workers, args.use_bgr, reused_dataloader)
    tag_dict = demo.infer_batch(dataloader, args.thresh ,args.char_thresh, args.num_classes, args.char_tag, args.character_only)
    return tag_dict

# note to self:
# classifier and scorer has same dataloader

class image_resize_demo(BaseDemo):
    pass
    


class CaptionArgs:
    def __init__(self, data, model_pth, ckpt, batch_size):
        self.data = data
        self.model_pth = model_pth
        self.ckpt = ckpt
        self.batch_size = batch_size

class Florence2Demo:
    def __init__(self, args):
        self.model = None # load florence here
        
    def infer(self, data):
        pass

def sentence_captioning(data, model_pth):
    pass
    ckpt = None
    parameters.log.info(f"Generating caption for {len(data)} images")
    batch_size = 1

    
    args = CaptionArgs(data, model_pth, ckpt, batch_size)
    demo = Florence2Demo(args)
    caption_dict = demo.infer(args.data)

if __name__ == '__main__':
    from tools.files import get_all_images_in_folder
    
    model_path = ""
    img_path = ""
    images = get_all_images_in_folder(img_path)
    
    x = image_scoring(images, model_path)
    
    # use the following for image_scoreing
    #import matplotlib.pyplot as plt
    #plt.hist([v[1] for v in x.values()], bins=np.arange(0, 60)/10)
    #plt.show()