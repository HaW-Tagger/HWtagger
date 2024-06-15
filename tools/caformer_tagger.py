import os, sys
import argparse
import warnings
warnings.filterwarnings("ignore")

import torch
import torchvision.transforms as transforms
from torch.utils.data.dataloader import default_collate
from src_files.data.path_dataset import PathDataset_test
from src_files.helper_functions.helper_functions import crop_fix
from src_files.models import create_model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from tqdm.auto import tqdm
import json
from PIL import Image
from resources import parameters
from resources.tag_categories import KAOMOJI


IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]

class HiddenPrints: # this is used when loading the model to supress the triton message
    # https://stackoverflow.com/a/45669280
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def custom_collate(batch):
    len_batch = len(batch)
    batch = list(filter(lambda x : x[0] is not None, batch))
    if len_batch > len(batch): # if there are samples missing just use existing members, doesn't work if you reject every sample in a batch
        diff = len_batch - len(batch)
        batch = batch + batch[:diff] # assume diff < len(batch)
    return default_collate(batch)

class FictionnalArgs:
    def __init__(self, data, ckpt, class_map, bs):
        self.data = data
        self.ckpt = ckpt
        self.class_map = class_map
        self.model_name = 'caformer_m36'
        self.num_classes = 12547
        self.image_size = 448
        self.thr = parameters.PARAMETERS["caformer_threshold"]
        self.keep_ratio = False
        self.bs = bs
        self.use_ml_decoder = 0
        self.fp16 = False
        self.ema = False
        self.frelu = True
        self.xformers = False
        self.decoder_embedding = 384
        self.num_layers_decoder = 4
        self.num_head_decoder = 8
        self.num_queries = 80
        self.scale_skip = 1
        self.model_path = None


def make_args():
    parser = argparse.ArgumentParser(description='mldanbooru Demo')
    parser.add_argument('--data', type=str, default='')
    parser.add_argument('--ckpt', type=str, default='')
    parser.add_argument('--class_map', type=str, default='./class.json')
    parser.add_argument('--model_name', default='caformer_m36')
    parser.add_argument('--num_classes', default=12547)
    parser.add_argument('--image_size', default=448, type=int,
                        metavar='N', help='input image size')
    parser.add_argument('--thr', default=0.75, type=float,
                        metavar='N', help='threshold value')
    parser.add_argument('--keep_ratio', type=str2bool, default=False)
    parser.add_argument('--bs', type=int, default=1)

    # ML-Decoder
    parser.add_argument('--use_ml_decoder', default=0, type=int)
    parser.add_argument('--fp16', action="store_true", default=False)
    parser.add_argument('--ema', action="store_true", default=False)

    parser.add_argument('--frelu', type=str2bool, default=True)
    parser.add_argument('--xformers', type=str2bool, default=False)

    # CAFormer
    parser.add_argument('--decoder_embedding', default=384, type=int)
    parser.add_argument('--num_layers_decoder', default=4, type=int)
    parser.add_argument('--num_head_decoder', default=8, type=int)
    parser.add_argument('--num_queries', default=80, type=int)
    parser.add_argument('--scale_skip', default=1, type=int)

    parser.add_argument('--out_type', type=str, default='json')

    args = parser.parse_args()
    return args

class Demo:
    def __init__(self, args):
        self.args=args

        parameters.log.info('Creating model {}...'.format(args.model_name))
        args.model_path = None
        
        model = create_model(args, load_head=True).to(device)
        state = torch.load(args.ckpt, map_location='cpu')
        if args.ema:
            state = state['ema']
        elif 'model' in state:
            state=state['model']
        model.load_state_dict(state, strict=True)

        self.model = model.to(device).eval()
        #######################################################

        if args.keep_ratio:
            self.trans = transforms.Compose([
                transforms.Resize(args.image_size),
                crop_fix,
                transforms.ToTensor(),
            ])
        else:
            self.trans = transforms.Compose([
                                    transforms.Resize((args.image_size, args.image_size)),
                                    transforms.ToTensor(),
                                ])

        self.load_class_map()

    def load_class_map(self):
        with open(self.args.class_map, 'r') as f:
            self.class_map = json.load(f)

    def load_data(self, path):
        img = Image.open(path).convert('RGB')
        img = self.trans(img)
        return img

    def infer_one(self, img, one_image=False, path=None):
        with torch.cuda.amp.autocast(enabled=self.args.fp16):
            img = img.unsqueeze(0)
            output = torch.sigmoid(self.model(img)).cpu().view(-1)
        pred = torch.where(output > self.args.thr)[0].numpy()

        cls_list = [(self.class_map[str(i)], output[i]) for i in pred]
        if not one_image:
            return cls_list
        tag_dict = {path: []}
        for tag_name, prob in cls_list:
            if len(tag_name)>3 and tag_name not in KAOMOJI:
                tag_dict[path].append((tag_name.replace('_', ' '), round(float(prob), 3)))
            else:
                tag_dict[path].append((tag_name, round(float(prob), 3)))
        return tag_dict

    @torch.no_grad()
    def infer(self, paths):
        if len(paths) == 1:
            img = self.load_data(paths[0]).to(device)
            tag_dict = self.infer_one(img, one_image=True, path=paths[0])
            return tag_dict
        else:
            tag_dict = {}
            for item in tqdm(paths):
                img = self.load_data(item).to(device)
                cls_list = self.infer_one(img)
                cls_list.sort(reverse=True, key=lambda x: x[1])
                tag_dict[item] = []
                for tag_name, prob in cls_list:
                    if len(tag_name) > 3 and tag_name not in KAOMOJI:
                        tag_dict[item].append((tag_name.replace('_', ' '), round(float(prob), 3)))
                    else:
                        tag_dict[item].append((tag_name, round(float(prob), 3)))

            return tag_dict

    @torch.no_grad()
    def infer_batch(self, paths, bs=8):
        tag_dict = {}
        dataset = PathDataset_test(paths, self.trans, fill_transaprent=True)
        loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False, collate_fn=custom_collate)
        for imgs, path_list in tqdm(loader):
            imgs = imgs.to(device)

            with torch.cuda.amp.autocast(enabled=self.args.fp16):
                output_batch = torch.sigmoid(self.model(imgs)).cpu()

            for output, img_path in zip(output_batch, path_list):
                pred = torch.where(output>self.args.thr)[0].numpy()
                cls_list = [(self.class_map[str(i)], output[i]) for i in pred]
                cls_list.sort(reverse=True, key=lambda x:x[1])
                tag_dict[img_path] = []
                for tag_name, prob in cls_list:
                    if len(tag_name) > 3 and tag_name not in KAOMOJI:
                        tag_dict[img_path].append((tag_name.replace('_', ' '), round(float(prob), 3)))
                    else:
                        tag_dict[img_path].append((tag_name, round(float(prob), 3)))

        return tag_dict


#python caformer_tagger.py --data imgs/t1.jpg --model_name caformer_m36 --ckpt ckpt/ml_caformer_m36_dec-5-97527.ckpt --thr 0.7 --image_size 448
def main(data, ckpt, class_map, bs):
    
    args = FictionnalArgs(data, ckpt, class_map, bs)
    demo = Demo(args)
    if args.bs>1:
        tag_dict = demo.infer_batch(args.data, args.bs)
    else:
        tag_dict = demo.infer(args.data)
    return tag_dict


if __name__ == '__main__':
    args = make_args()
    demo = Demo(args)
    if args.bs>1:
        tag_dict = demo.infer_batch(args.data, args.bs)
    else:
        tag_dict = demo.infer(args.data)

    parameters.log.info(tag_dict)