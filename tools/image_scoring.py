
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
from resources import parameters, tag_categories


# from wd14 tagger
IMAGE_SIZE = 448
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
            parameters.log.debug(imgs.shape)
            scores = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            scores = np.array(scores)
            score = np.sum(np.multiply(scores, np.arange(len(tag_categories.QUALITY_LABELS))[::-1]), axis=1)
            
            
            percentile = [score_to_percentile(s) for s in score]
            labels = [percentile_to_label(p) for p in percentile]
            confidence = scores
            for pth, l, s_perct in zip(path_list, labels, percentile):
                path_dict[pth]=(l, s_perct)
        return path_dict
            
def main(data, model_pth):
    bs = 2
    if len(data) > 100:
        bs = 4
    bs_max = parameters.PARAMETERS["max_batch_size"]    
    if bs_max > bs:
        bs = bs_max
    
    ckpt = os.path.join(model_pth, "model.onnx") 

    parameters.log.info(f"Loading SwinV2_aesthetic, Batch:{bs}, using ONNX and torch")
    args = FictionnalArgs(data, model_pth, ckpt, bs)
    demo = Demo(args)
    
    if args.bs>=1:
        tag_dict = demo.infer_batch(args.data, args.bs, args.model_dir)
    else:
        parameters.log.error("Use a batch size > 2, the multi-item dataloader has a bad img exception")
        tag_dict = {}
    return tag_dict


if __name__ == '__main__':
    model_path = ""
    img_path = ""
    from tools.files import get_all_images_in_folder
    
    images = get_all_images_in_folder(img_path)
    x = main(images, model_path)
    parameters.log.info(x)
    import matplotlib.pyplot as plt
    plt.hist([v[1] for v in x.values()], bins=np.arange(0, 60)/10)
    plt.show()
    #parameters.log.info(x.shape())
    #score = []
    #from tools.dbaesthetic import anime_dbaesthetic
    

    #import time
    #for p in tqdm(): 
    #    score.append(anime_dbaesthetic(p))
    #img_dict = {}
    #start_time = time.time()

    #https://huggingface.co/deepghs/anime_aesthetic/tree/main/swinv2pv3_v0_448_ls0.2_x
    
    

    
    