import os
import warnings
warnings.filterwarnings("ignore")
# onnx is built into pytorch

    
import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional as F
from torch.utils.data.dataloader import default_collate
import onnxruntime as ort
from src_files.data.path_dataset import PathDataset_test
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from tools import files

from tqdm.auto import tqdm
import numpy as np
from resources import parameters, tag_categories
from resources.tag_categories import KAOMOJI

# from wd14 tagger
IMAGE_SIZE = 448
CHARACTERS_COUNT_THRESHOLD = parameters.PARAMETERS["swinv2_character_count_threshold"]

# onnx verion opset:
# https://github.com/onnx/onnx/blob/main/docs/Versioning.md#released-versions

class SquarePad:
    #https://discuss.pytorch.org/t/how-to-resize-and-pad-in-a-torchvision-transforms-compose/71850/10
    def __call__(self, image):
        max_wh = max(image.size)
        p_left, p_top = [(max_wh - s) // 2 for s in image.size]
        p_right, p_bottom = [max_wh - (s+pad) for s, pad in zip(image.size, [p_left, p_top])]
        padding = (p_left, p_top, p_right, p_bottom)
        return F.pad(image, padding, 0, 'constant')

def custom_collate(batch):
    len_batch = len(batch)
    batch = list(filter(lambda x : x[0] is not None, batch))
    if len_batch > len(batch): # if there are samples missing just use existing members, doesn't work if you reject every sample in a batch
        diff = len_batch - len(batch)
        batch = batch + batch[:diff] # assume diff < len(batch)
    return default_collate(batch)

class FictionnalArgs:
    def __init__(self, data, dir_path, ckpt, thresh, char_thresh, bs=4, char_tag=False, character_only=False):
        self.model_name = 'SwinV2-v3'
        self.data = data
        self.model_dir = dir_path
        self.model_path = ckpt
        self.thresh = thresh
        self.char_thresh = char_thresh
        self.bs = bs
        self.image_size = IMAGE_SIZE
        self.keep_ratio = True
        self.num_classes = 10861 # from v2-v3 config
        self.char_tag = char_tag
        self.character_only = character_only
     

class Demo: # https://github.com/kohya-ss/sd-scripts/blob/main/finetune/tag_images_by_wd14_tagger.py
    def __init__(self, args):
        parameters.log.info('Creating model {}...'.format(args.model_name))
        self.ort_session = ort.InferenceSession(
                    args.model_path,
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.input_name = self.ort_session.get_inputs()[0].name  # should be "input_1:0" 
        self.output_name = self.ort_session.get_outputs()[0].name
        
        if args.keep_ratio:
            self.trans = transforms.Compose([
                #SquarePad(),
                transforms.Resize((args.image_size, args.image_size), interpolation=transforms.functional.InterpolationMode.BICUBIC),
                #transforms.ToTensor(),
            ])
        else:
            self.trans = transforms.Compose([
                                    transforms.Resize((args.image_size, args.image_size)),
                                    transforms.ToTensor(),
                                    #transforms.ToPILImage()
                                ])
        
        tags_df = files.get_pd_swinbooru_tag_frequency()
        
       # https://huggingface.co/spaces/SmilingWolf/wd-tagger/tree/main
        name_series = tags_df["name"]
        name_series = name_series.map(lambda x: x.replace("_", " ") if x not in KAOMOJI else x)
        self.tag_names = name_series.tolist()
        self.rating_indexes = list(np.where(tags_df["category"] == 9)[0])
        self.general_indexes = list(np.where(tags_df["category"] == 0)[0])
        self.character_indexes = list(np.where(tags_df["category"] == 4)[0])
        self.general_tag = [self.tag_names[i] for i in self.general_indexes]
        self.character_tags = [self.tag_names[i] for i in self.character_indexes]

        self.whitelist_characters = [chara for chara, freq in tag_categories.CHARACTERS_TAG_FREQUENCY.items() if int(freq) > CHARACTERS_COUNT_THRESHOLD]


    @torch.no_grad()  
    def infer_batch(self, paths, bs, thresh, char_thresh, num_classes=10861, char_tag=False, character_only=False):
        tag_dict = {}
        dataset = PathDataset_test(paths, self.trans, convert_bhwc=False, convert_bgr=True, to_np=True, fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False, collate_fn=custom_collate)
        np.set_printoptions(suppress=True)
        for imgs, path_list in tqdm(loader):
            imgs = np.array(imgs)
            probs = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            for f_path, prob_vec in zip(path_list, probs):
                general_prob = prob_vec[self.general_indexes]
                tags = [(tag_name, round(float(prob), 3)) for tag_name, prob in zip(self.general_tag, general_prob) if prob > thresh]
                tags.sort(reverse=True, key=lambda x: x[1])
                
                if char_tag and not character_only:
                    char_prob = prob_vec[self.character_indexes]
                    tags.extend( [(char_name, round(float(prob), 3)) for char_name, prob in zip(self.character_tags, char_prob) if prob > char_thresh and char_name in self.whitelist_characters])
                elif char_tag and character_only:
                    char_prob = prob_vec[self.character_indexes]
                    tags = [(char_name, round(float(prob), 3)) for char_name, prob in zip(self.character_tags, char_prob) if prob > char_thresh and char_name in self.whitelist_characters]
                    
                tag_dict[f_path] = tags

        return tag_dict
            

def main(data, model_pth, character_only=False):
    bs = 2
    if len(data) > 100:
        bs = 4
    bs_max = parameters.PARAMETERS["max_batch_size"]    
    if bs_max > bs:
        bs = bs_max
        
    threshold=parameters.PARAMETERS["swinv2_threshold"], 
    character_threshold=parameters.PARAMETERS["swinv2_character_threshold"],
    ckpt = os.path.join(model_pth, "model.onnx") 
    CHARACTERS = parameters.PARAMETERS["swinv2_enable_character"]
    parameters.log.info(f"Loading SwinV2, Batch:{bs}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, threshold, character_threshold, bs, CHARACTERS, character_only)
    demo = Demo(args)
    
    if args.bs>=1:
        tag_dict = demo.infer_batch(args.data, args.bs, args.thresh ,args.char_thresh, args.num_classes, args.char_tag, args.character_only)
    else:
        parameters.log.error("Use a batch size >= 1, the multi-item dataloader has a bad img exception")
        tag_dict = {}
    return tag_dict


