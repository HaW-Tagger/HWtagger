import os
os.environ["XFORMERS_FORCE_DISABLE_TRITON"] = "1"
import warnings
warnings.filterwarnings("ignore")
# onnx is built into pytorch

import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional as F
from torch.utils.data.dataloader import default_collate
import onnxruntime as ort

from tqdm.auto import tqdm
import numpy as np

from tools import files
from src_files.data.path_dataset import PathDataset_test
from resources import parameters, tag_categories

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# onnx verion opset:
# https://github.com/onnx/onnx/blob/main/docs/Versioning.md#released-versions

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
    
    return default_collate(batch)

class FictionnalArgs:
    def __init__(self, data, dir_path, ckpt, batch_size=4):
        self.model_name = 'SwinV2-v3'
        self.data = data
        self.model_dir = dir_path
        self.model_path = ckpt
        self.batch_size = batch_size
        self.image_size = IMAGE_SIZE
        self.keep_ratio = False # this is not helpful for this model
        self.base_tagger = False
        
    def add_args_for_tagger(self, thresh, char_thresh, char_tag=False, character_only=False):
        self.thresh = thresh
        self.char_thresh = char_thresh
        self.num_classes = 10861 # from v2-v3 config
        self.char_tag = char_tag
        self.keep_ratio = True
        self.character_only = character_only
        self.base_tagger = True
        
class BaseDemo: 
    # https://github.com/kohya-ss/sd-scripts/blob/main/finetune/tag_images_by_wd14_tagger.py
    def __init__(self, args):
        parameters.log.info(f'Creating model {args.model_name}...')
        self.ort_session = ort.InferenceSession(
                    args.model_path,
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.input_name = self.ort_session.get_inputs()[0].name  # should be "input_1:0" 
        self.output_name = self.ort_session.get_outputs()[0].name
        parameters.log.debug(self.ort_session.get_inputs()[0])
        if args.base_tagger: # this is for the basic tagger, swinv2v3
            self.trans = transforms.Compose([
                #SquarePad(), # ignore keep ratio bc it has a tentancy to add letterboxed and other tags related to borders to tags
                transforms.Resize((args.image_size, args.image_size), 
                                  interpolation=transforms.functional.InterpolationMode.BICUBIC),
            ])
        else:# this is for aesthetic and classifying
            self.trans = transforms.Compose([
                #square_pad()
                transforms.Resize((args.image_size, args.image_size),
                                interpolation=transforms.functional.InterpolationMode.BICUBIC),
                transforms.ToTensor(),
                #transforms.ToPILImage()
            ])
    
    # infer_batch is different per model, so inheritance takes care of that below
            
class ImageClassificationDemo(BaseDemo):
    def __init__(self, args):
        super().__init__(args)
        
    @torch.no_grad()  
    def infer_batch(self, paths, bs):
        path_dict = {}
        # original library
        #from imgutils.validate.classify import anime_classify 
        dataset = PathDataset_test(paths, self.trans, convert_bhwc=False, convert_bgr=False, to_np=True, fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False, collate_fn=custom_collate)
        
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
    def infer_batch(self, paths, bs):
        path_dict = {}
        # original library
        #from imgutils.validate.classify import anime_classify 
        dataset = PathDataset_test(paths, self.trans, convert_bhwc=False, convert_bgr=False, to_np=True, fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False, collate_fn=custom_collate)
        
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

     
class ImageScoringDemo(BaseDemo):
    def __init__(self, args):
        super().__init__(args)
        
    @torch.no_grad()  
    def infer_batch(self, paths, bs, model_dir):
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
        
        def percentile_to_label(percentile):
            mapping = tag_categories.QUALITY_LABELS_MAPPING
            for label, threshold in sorted(mapping.items(), key=lambda x: (-x[1], x[0])):
                if percentile >= threshold:
                    return label
            return "WORST"
                
        sorted_values = np.array([v for v in sorted(tag_categories.QUALITY_LABELS_MAPPING.values())])
        sorted_keys = [v[0] for v in sorted(tag_categories.QUALITY_LABELS_MAPPING.items(), key=lambda item: item[1])]
        
        
        dataset = PathDataset_test(paths, self.trans, convert_bhwc=False, convert_bgr=False, to_np=True, fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False, collate_fn=custom_collate)
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
    def __init__(self, args):
        super().__init__(args)
        
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

        self.whitelist_characters = [chara for chara, freq in tag_categories.CHARACTERS_TAG_FREQUENCY.items() if int(freq) > CHARACTERS_COUNT_THRESHOLD]
    
    @torch.no_grad()  
    def infer_batch(self, paths, bs, thresh, char_thresh, num_classes=10861, char_tag=False, character_only=False):
        tag_dict = {}
        dataset = PathDataset_test(paths, self.trans, convert_bhwc=False, convert_bgr=True, to_np=True, fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False, collate_fn=custom_collate)
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
                    tags.extend( [(char_name, round(float(prob), 3)) for char_name, prob in zip(self.character_tags, char_prob) if prob > char_thresh and char_name in self.whitelist_characters])
                elif char_tag and character_only:
                    char_prob = prob_vec[self.character_indexes]
                    tags = [(char_name, round(float(prob), 3)) for char_name, prob in zip(self.character_tags, char_prob) if prob > char_thresh and char_name in self.whitelist_characters]
                    
                tag_dict[f_path] = tags

        return tag_dict


class Eva02LargeV3TaggingDemo(BaseDemo):
    def __init__(self, args):
        super().__init__(args)

        tags_df = files.get_pd_eva02_large_tag_frequency()
        # https://huggingface.co/spaces/SmilingWolf/wd-tagger/tree/main
        name_series = tags_df["name"]
        name_series = name_series.map(lambda x: x.replace("_", " ") if x not in tag_categories.KAOMOJI else x)
        self.tag_names = name_series.tolist()
        self.rating_indexes = list(np.where(tags_df["category"] == 9)[0])
        self.general_indexes = list(np.where(tags_df["category"] == 0)[0])
        self.character_indexes = list(np.where(tags_df["category"] == 4)[0])
        self.general_tag = [self.tag_names[i] for i in self.general_indexes]
        self.character_tags = [self.tag_names[i] for i in self.character_indexes]

        self.whitelist_characters = [chara for chara, freq in tag_categories.CHARACTERS_TAG_FREQUENCY.items() if
                                     int(freq) > CHARACTERS_COUNT_THRESHOLD]

    @torch.no_grad()
    def infer_batch(self, paths, bs, thresh, char_thresh, num_classes=10861, char_tag=False, character_only=False):
        tag_dict = {}
        dataset = PathDataset_test(paths, self.trans, convert_bhwc=False, convert_bgr=True, to_np=True,
                                   fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False,
                                             collate_fn=custom_collate)
        # np.set_printoptions(suppress=True)
        for imgs, path_list in tqdm(loader):
            imgs = np.array(imgs)
            probs = self.ort_session.run([self.output_name], {self.input_name: imgs})[0]  # onnx output numpy
            for f_path, prob_vec in zip(path_list, probs):
                general_prob = prob_vec[self.general_indexes]
                tags = [(tag_name, round(float(prob), 3)) for tag_name, prob in zip(self.general_tag, general_prob) if
                        prob > thresh]
                tags.sort(reverse=True, key=lambda x: x[1])

                if char_tag and not character_only:
                    char_prob = prob_vec[self.character_indexes]
                    tags.extend(
                        [(char_name, round(float(prob), 3)) for char_name, prob in zip(self.character_tags, char_prob)
                         if prob > char_thresh and char_name in self.whitelist_characters])
                elif char_tag and character_only:
                    char_prob = prob_vec[self.character_indexes]
                    tags = [(char_name, round(float(prob), 3)) for char_name, prob in
                            zip(self.character_tags, char_prob) if
                            prob > char_thresh and char_name in self.whitelist_characters]

                tag_dict[f_path] = tags

        return tag_dict
        
def image_scoring(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"]):
    #https://huggingface.co/deepghs/anime_aesthetic/tree/main/swinv2pv3_v0_448_ls0.2_x
    
    ckpt = os.path.join(model_pth, "model.onnx")
    parameters.log.info(f"Loading SwinV2_aesthetic, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size)
    demo = ImageScoringDemo(args)
    tag_dict = demo.infer_batch(args.data, args.batch_size, args.model_dir)
    return tag_dict

def image_classify(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"]):
    # model is the base model used in imguitls
    # https://huggingface.co/deepghs/anime_classification/tree/main/mobilenetv3_v1.3_dist
    ckpt = os.path.join(model_pth, "model.onnx") 
    parameters.log.info(f"Loading Image source classifer, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size)
    demo = ImageClassificationDemo(args)
    tag_dict = demo.infer_batch(args.data, args.batch_size)
    return tag_dict

def image_completeness(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"]):
    # model is one used by imgutils
    # https://huggingface.co/deepghs/anime_completeness/tree/main/caformer_s36_v2.2
    ckpt = os.path.join(model_pth, "model.onnx") 
    parameters.log.info(f"Loading Image completeness identifier, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, batch_size)
    demo = ImageCompletenessDemo(args)
    tag_dict = demo.infer_batch(args.data, args.batch_size)
    return tag_dict

def swinv2v3_tagging(data, model_pth, character_only=False, batch_size=parameters.PARAMETERS["max_batch_size"]):
    threshold=parameters.PARAMETERS["swinv2_threshold"], 
    character_threshold=parameters.PARAMETERS["swinv2_character_threshold"],
    ckpt = os.path.join(model_pth, "model.onnx") 
    CHARACTERS = parameters.PARAMETERS["swinv2_enable_character"]
    parameters.log.info(f"Loading SwinV2, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt,  batch_size)
    args.add_args_for_tagger(threshold, character_threshold, CHARACTERS, character_only)
    demo = Swinv2v3TaggingDemo(args)
    tag_dict = demo.infer_batch(args.data, args.batch_size, args.thresh ,args.char_thresh, args.num_classes, args.char_tag, args.character_only)
    return tag_dict

def eva02_large_v3_tagging(data, model_pth, character_only=False, batch_size=parameters.PARAMETERS["max_batch_size"]):
    threshold=parameters.PARAMETERS["wdeva02_large_threshold"],
    character_threshold=parameters.PARAMETERS["swinv2_character_threshold"],
    ckpt = os.path.join(model_pth, "wd-eva02-large-tagger-v3.onnx")
    CHARACTERS = parameters.PARAMETERS["swinv2_enable_character"]
    parameters.log.info(f"Loading wd-eva02-large-tagger-v3, Batch:{batch_size}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt,  batch_size)
    args.add_args_for_tagger(threshold, character_threshold, CHARACTERS, character_only)
    demo = Eva02LargeV3TaggingDemo(args)
    tag_dict = demo.infer_batch(args.data, args.batch_size, args.thresh ,args.char_thresh, args.num_classes, args.char_tag, args.character_only)
    return tag_dict

# note to self:
# classifier and scorer has same dataloader

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