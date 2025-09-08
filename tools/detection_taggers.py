import os
from resources import parameters

from tqdm import tqdm
from collections import Counter
import math
import torch
import onnxruntime as ort
from src_files.data.path_dataset import PathDataset_test
import torchvision.transforms as transforms

from torch.utils.data import DataLoader, Dataset
from PIL import Image

from tools.wd14_based_taggers import custom_collate
import imagesize
import numpy as np

from tools.yolo_postprocessing import _yolo_xywh2xyxy, _yolo_nms, _xy_postprocess, _bboxes_from_bitmap

# people detection
# https://deepghs.github.io/imgutils/main/_modules/imgutils/detect/person.html#detect_person
#https://deepghs.github.io/imgutils/main/_modules/imgutils/detect/head.html#detect_heads

class BaseArgs:
    # this is a class that stores the args used by the detection model
    def __init__(self, data, model_name, model_dir, ckpt, batch_size=1, model_type: str = 'm', model_version:str = 'v1.1',
                  image_size=640, conf_thresh: float = 0.3, iou_thresh: float = 0.5, labels=["person"]):
        self.model_name = model_name
        self.data = data
        self.batch_size = batch_size
        self.model_dir = model_dir
        self.model_path = ckpt
        self.model_type = model_type
        self.model_version = model_version
        self.image_size = image_size
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.keep_ratio = True # ?
        self.labels = labels

class ResizeWithAspectRatio:
    # a class with a __call__ feature which acts as the transformation applied to a torch custom dataset
    # calculates resized image, usually downsize to maxsize keeping aspect ratio
    def __init__(self, max_size=640, multiples=32):
        self.max_size = max_size
        self.multiples = multiples

    def get_resized_size(self, old_width, old_height):
        new_width, new_height = old_width, old_height
        r = self.max_size / max(new_width, new_height)
        if r < 1:
                new_width, new_height = new_width * r, new_height * r
                
         # ensure both sides are a multiple of 32 (required bc it's the stride it takes at the largest layers)
        new_width = int(math.ceil(new_width / self.multiples) * self.multiples)
        new_height = int(math.ceil(new_height / self.multiples) * self.multiples)
        return (new_width, new_height)
    
    def __call__(self, img):
        # Calculate new size maintaining aspect ratio that fit into the 640x640 box
        old_width, old_height = img.width, img.height
        new_size = self.get_resized_size(old_width, old_height)
        img = img.resize(new_size) # default is bicubic interpolation
        return img, np.array((old_width, old_height)), np.array(new_size)
    
class CustomDataset(Dataset):
    # custom pytorch dataset class, applies the transformation to loaded data
    def __init__(self, img_paths, transform=None, convert_bhwc=False):
        self.img_paths = img_paths
        self.transform = transform
        self.convert_bhwc = convert_bhwc

    def __len__(self):
        return len(self.img_paths)

    def __getitem__(self, idx):
        img_path = self.img_paths[idx]
        image = Image.open(img_path).convert("RGB")

        image, old_dim, new_dim = self.transform(image)
        image = transforms.ToTensor()(image)
        if self.convert_bhwc:
            # https://discuss.pytorch.org/t/torchvision-totensor-dont-change-channel-order/82038/3
            image = image.permute((1, 2, 0)).contiguous()
        return image, img_path, old_dim, new_dim
    
class BaseDetectionDemo:
    # this is the base container to call all detection models (yolov8), only the labels and thresholds changes
    def __init__(self, args):
        parameters.log.info(f'Creating model {args.model_name}...')
        self.ort_session = ort.InferenceSession(
                    args.model_path,
                    providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.input_name = self.ort_session.get_inputs()[0].name  # should be "input_1:0" 
        self.output_name = self.ort_session.get_outputs()[0].name
        parameters.log.debug(self.ort_session.get_inputs()[0])
        self.trans = ResizeWithAspectRatio()
        self.args = args
        self.labels = args.labels
        self.image_size = args.image_size
        self.yolo_text_detection = args.labels == ["text"]

    def get_bbox(self, pred, old_dim, new_dim, labels=["person"]):
        # this gets the bbox based on the result per sample (not including batch dim)
        #print(pred.shape)
        max_scores = pred[4:, :].max(axis=0) #[5, 8400]
        pred = pred[:, max_scores > self.args.conf_thresh].transpose(1, 0)
        boxes = pred[:, :4]
        scores = pred[:, 4:]
        filtered_max_scores = scores.max(axis=1)
        
        if not boxes.size:
            return []
        
        boxes = _yolo_xywh2xyxy(boxes)
        idx = _yolo_nms(boxes, filtered_max_scores, thresh=self.args.iou_thresh)
        boxes, scores = boxes[idx], scores[idx]

        detections = []
        detection_count = [0 for _ in labels] # counter for the number of times we seen the class
        for box, score in zip(boxes, scores):
            x0, y0 = _xy_postprocess(box[0], box[1], old_dim, new_dim)
            x1, y1 = _xy_postprocess(box[2], box[3], old_dim, new_dim)
            max_score_id = score.argmax()
            
            detections.append(((x0, y0, x1, y1), labels[max_score_id] +"_"+ str(detection_count[max_score_id]), float(score[max_score_id])))
            detection_count[max_score_id]+=1
        return detections
    
    def get_bbox_text(self, pred, old_dim, new_dim, labels=["texts"]):
        # old dim and new dim are pairs due to the dataloader
        heatmap = pred[0]
        (origin_width, origin_height) = np.array(old_dim)
        max_candidates = 1000
        unclip_ratio = 2
        # gets headmap
        retval = []
        det_count = 0
        for points, score in zip(*_bboxes_from_bitmap(
                heatmap, heatmap >= self.args.conf_thresh, origin_width, origin_height,
                self.args.iou_thresh, max_candidates, unclip_ratio,
        )):
            #retval.append((points, score))
            x0, y0 = points[:, 0].min(), points[:, 1].min()
            x1, y1 = points[:, 0].max(), points[:, 1].max()
            retval.append(((x0.item(), y0.item(), x1.item(), y1.item()), 'text'+"_"+ str(det_count), float(score)))
            det_count+=1
        return retval
    
    def bucketed_infer_batch(self, paths, batch_size=4):
        # this is a psudo batch yolo method, takes in the paths of the images, 
        # then bucket them using a resize policy of 640px.  Then run the infer_batch function on each bucket size
        resize_transform = ResizeWithAspectRatio(max_size=self.image_size, multiples=32)
        img_sizes = [resize_transform.get_resized_size(*imagesize.get(fpath)) for fpath in paths]
        main_dict = {}
        
        c = Counter()
        c.update(img_sizes)
        
        def get_batch(img_count):
            # dynamically assign proper batch size based on img count per bucket
            return 1 if img_count < 50 else batch_size
        
        img_sizes_set = sorted(list(set(img_sizes)), reverse=True)
        parameters.log.info(f"working with the following ((bucket sizes), img count, batch):")
        
        misc_sizes = {size for size in img_sizes_set if c[size] < batch_size}
        non_misc_size = [size for size in img_sizes_set if size not in misc_sizes]
        misc_path_subset = [p for p, s in zip(paths, img_sizes) if s in misc_sizes]
        
        for size in non_misc_size:
            parameters.log.info(f"{size} : {c[size]} , {get_batch(c[size])}")
        parameters.log.info(f"misc size (running batch 1) : {len(misc_path_subset)}, 1")
        
        for size in non_misc_size:    
            path_subset = [p for p, s in zip(paths, img_sizes) if s == size]
            img_count = len(path_subset)
            main_dict.update(self.infer_batch(path_subset, get_batch(img_count))) # update main dict with results
        
        if misc_path_subset:
            main_dict.update(self.infer_batch(misc_path_subset, 1))
            
        return main_dict
             
    @torch.no_grad()  
    def infer_batch(self, paths, batch_size=1):
        """
        this uses batches: 
        for batch > 1, only send images that are the same size after bucketing (check resize_transform)
        for batch = 1, you can send images of different size
        returns dict : path --> ((x0.item(), y0.item(), x1.item(), y1.item()), 'text', score)
        """
        path_dict = {}
        #dataset = PathDataset_test(self.args.data, self.trans, convert_bhwc=True, convert_bgr=False, to_np=True, fill_transaprent=True)
        resize_transform = ResizeWithAspectRatio(max_size=self.image_size, multiples=32)
        dataset = CustomDataset(paths, transform=resize_transform, convert_bhwc=False)
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, num_workers=4, shuffle=False, collate_fn=custom_collate)#
        
        #np.set_printoptions(suppress=True)
        for imgs, path_list, old_dim, new_dim in tqdm(loader):
            #print(path_list, old_dim, new_dim)
            imgs = np.array(imgs)
            #parameters.log.info(f"img_dim: {imgs.shape}")
            batch_output = self.ort_session.run([self.output_name], {self.input_name:imgs})[0] # onnx output numpy
            #parameters.log.info(f"output_shape: {batch_output.shape}")
            for i, path in enumerate(path_list):
                if self.yolo_text_detection:
                    path_dict[path] = self.get_bbox_text(batch_output[i], old_dim[i], new_dim[i], self.labels)
                else:
                    path_dict[path] = self.get_bbox(batch_output[i], old_dim[i], new_dim[i], self.labels)
        return path_dict

def detect_people(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"]): # no batch size for now
    model_name = "person_detect_plus_v1.1_best_m.onnx"
    ckpt = os.path.join(model_pth, model_name)
    parameters.log.info(f"Loading people (anime) detection")
    
    args = BaseArgs(data, "people detection", model_pth, ckpt, batch_size=batch_size, model_type="m", 
                    model_version="v1.1", conf_thresh=0.3, iou_thresh=0.5, labels=["person"], 
                    image_size=parameters.PARAMETERS["detection_small_resolution"])
    demo = BaseDetectionDemo(args)
    
    if len(data) < 50: # do batch 1
        batch_size = 1
        args.batch_size = batch_size
        tag_dict = demo.infer_batch(args.data, batch_size)
    else: # bucket the images into similar size and so detection that ways
        tag_dict = demo.bucketed_infer_batch(args.data, batch_size)
    return tag_dict

def detect_head(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"]):
    model_name = "head_detect_best_s.onnx"
    ckpt = os.path.join(model_pth, model_name)
    parameters.log.info(f"Loading head (anime) detection")
    
    args = BaseArgs(data, "head detection", model_pth, ckpt, batch_size=batch_size, model_type="s", 
                    model_version="Best", conf_thresh=0.3, iou_thresh=0.7, labels=["head"], 
                    image_size=parameters.PARAMETERS["detection_small_resolution"])
    demo = BaseDetectionDemo(args)
    
    if len(data) < 50: # do batch 1
        batch_size = 1
        args.batch_size = batch_size
        tag_dict = demo.infer_batch(args.data, batch_size)
    else: # bucket the images into similar size and so detection that ways
        tag_dict = demo.bucketed_infer_batch(args.data, batch_size)
    return tag_dict
    
def detect_hand(data, model_pth, batch_size=parameters.PARAMETERS["max_batch_size"]):
    # from https://huggingface.co/deepghs/anime_hand_detection/tree/main/hand_detect_v1.0_s
    ckpt = os.path.join(model_pth, "model.onnx")
    parameters.log.info(f"Loading hand (anime) detection")
    args = BaseArgs(data, "hand detection", model_pth, ckpt, batch_size=batch_size, model_type="s", 
                    model_version="v1.0", conf_thresh=0.35, iou_thresh=0.7, labels=["hand"], 
                    image_size=parameters.PARAMETERS["detection_small_resolution"])
    demo = BaseDetectionDemo(args)
    if len(data) < 50: # do batch 1
        batch_size = 1
        args.batch_size = batch_size
        tag_dict = demo.infer_batch(args.data, batch_size)
    else: # bucket the images into similar size and so detection that ways
        tag_dict = demo.bucketed_infer_batch(args.data, batch_size)
    return tag_dict


def detect_text(data:list[str], model_pth:str, batch_size:int=4):
    """This is intended to call ocr models hosted by imgutils but using batches based on bucketed images
    imgutils: https://dghs-imgutils.deepghs.org/main/api_doc/ocr/index.html
    ocr models: https://huggingface.co/deepghs/paddleocr/tree/main

    resize max dim of img to 768 (keep aspect ratio), then bucket them based on the resized resolution,
    then perform batch inference with yolo (which returns a heatmap), 
    then we process the heatmap to get the location data for the detected text
    
    Args:
        data (list[str]): list of image paths
        model_pth (str): location where the model.onnx file is location (include filename)
        batch_size (int, optional): _description_. Defaults to 4.

    Returns:
        dict[str:list[tuple((int, int, int, int), str, float)]] : returns a dict with the image_path as key, values is a list of tuple
            len 3: tuple stores the top left and bottom right corner of the detection area, the detection type, and confidence (0~1)
            Ex: img_path --> ((x0.item(), y0.item(), x1.item(), y1.item()), 'text', score)
    """
    ckpt = os.path.join(model_pth, "model.onnx")
    args = BaseArgs(data, "text detection", model_pth, ckpt, batch_size=batch_size, model_type="det", 
                    model_version="v4", conf_thresh=0.3, iou_thresh=0.6, labels=["text"], 
                    image_size=parameters.PARAMETERS["detection_text_resolution"])
    demo = BaseDetectionDemo(args)
    if len(data) < 50: # do batch 1
        batch_size = 1
        args.batch_size = batch_size
        tag_dict = demo.infer_batch(args.data, batch_size)
    else: # bucket the images into similar size and so detection that ways
        tag_dict = demo.bucketed_infer_batch(args.data, batch_size)
    return tag_dict
