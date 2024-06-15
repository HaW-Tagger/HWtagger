
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

from tqdm.auto import tqdm
import numpy as np
import pandas as pd
from resources import parameters



# from wd14 tagger
IMAGE_SIZE = 448
_LABELS = [
        "3d",
        "anime coloring",
        "comic",
        "illustration",
        "not painting"
    ]

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
    def __init__(self, data, dir_path, ckpt, bs=4):
        self.model_name = 'SwinV2-v3'
        self.data = data
        self.model_dir = dir_path
        self.model_path = ckpt
        self.bs = bs
        self.image_size = IMAGE_SIZE
        self.keep_ratio = True


     

class Demo: # https://github.com/kohya-ss/sd-scripts/blob/main/finetune/tag_images_by_wd14_tagger.py
    def __init__(self, args):
        parameters.log.info('Creating model {}...'.format(args.model_name))
        self.ort_session = ort.InferenceSession(
                    args.model_path,
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.input_name = self.ort_session.get_inputs()[0].name  # should be "input_1:0" 
        self.output_name = self.ort_session.get_outputs()[0].name
        parameters.log.debug(self.ort_session.get_inputs()[0])
        if args.keep_ratio:
            self.trans = transforms.Compose([
                #SquarePad(),
                transforms.Resize((args.image_size, args.image_size), interpolation=transforms.functional.InterpolationMode.BICUBIC),
                transforms.ToTensor(),
            ])
        else:
            self.trans = transforms.Compose([
                                    transforms.Resize((args.image_size, args.image_size)),
                                    transforms.ToTensor(),
                                    #transforms.ToPILImage()
                                ])
    
     
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
            parameters.log.debug(imgs.shape)
            predictions = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            classification = np.array(predictions)
            parameters.log.debug(classification)
            
            for pth, img_cls in zip(path_list, classification):
                idx = np.argmax(img_cls)
                label_idx =_LABELS[idx]
                label_prob=img_cls[idx]
                #if "2cb0" in pth or "c7d5" in pth or "0c0d" in pth:
                #    parameters.log.debug(pth, label_idx, label_prob)
                path_dict[pth]=(label_idx, label_prob)
        return path_dict
            
def main(data, model_pth):
    bs = 2
    if len(data) > 100:
        bs = 4
    bs_max = parameters.PARAMETERS["max_batch_size"]
    if bs_max > bs:
        bs = bs_max
    
    # model is the base model used in imguitls
    # https://huggingface.co/deepghs/anime_classification/tree/main/mobilenetv3_v1.3_dist
    ckpt = os.path.join(model_pth, "model.onnx") 

    parameters.log.info(f"Loading Image source classifer, Batch:{bs}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, bs)
    demo = Demo(args)
    
    if args.bs>1:
        tag_dict = demo.infer_batch(args.data, args.bs)
    else:
        parameters.log.error("Use a batch size > 2, the multi-item dataloader has a bad img exception")
        tag_dict = {}
    return tag_dict
    
    