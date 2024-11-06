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

# people detection
# https://deepghs.github.io/imgutils/main/_modules/imgutils/detect/person.html#detect_person
#https://deepghs.github.io/imgutils/main/_modules/imgutils/detect/head.html#detect_heads


# code from yolov8, some parts, I'm unsure of and there doesn't seem to be an easy way to speed the bbox extraction
def _yolo_nms(boxes, scores, thresh: float = 0.7) -> list[int]:
    """
    dets: ndarray, (num_boxes, 5)
    """
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)

    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)

        inter = w * h
        iou = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(iou <= thresh)[0]
        order = order[inds + 1]

    return keep

def _yolo_xywh2xyxy(x: np.ndarray) -> np.ndarray:
    """
    Copied from yolov8.

    Convert bounding box coordinates from (x, y, width, height) format to (x1, y1, x2, y2) format where (x1, y1) is the
    top-left corner and (x2, y2) is the bottom-right corner.

    Args:
        x (np.ndarray) or (torch.Tensor): The input bounding box coordinates in (x, y, width, height) format.
    Returns:
        y (np.ndarray) or (torch.Tensor): The bounding box coordinates in (x1, y1, x2, y2) format.
    """
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    y[..., 2] = x[..., 0] + x[..., 2] / 2  # bottom right x
    y[..., 3] = x[..., 1] + x[..., 3] / 2  # bottom right y
    return y

def _xy_postprocess(x, y, old_size, new_size):
    # returns the height and weight associated to the original size of the image
    
    old_width, old_height = old_size
    new_width, new_height = new_size
    x, y = x / new_width * old_width, y / new_height * old_height
    x = int(np.clip(x, a_min=0, a_max=old_width).round())
    y = int(np.clip(y, a_min=0, a_max=old_height).round())
    return x, y


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

    def get_bbox(self, pred, old_dim, new_dim, labels=["person"]):
        # this gets the bbox based on the result per sample (not including batch dim)
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
    
    def bucketed_infer_batch(self, paths, batch_size=4):
        # this is a psudo batch yolo method, takes in the paths of the images, 
        # then bucket them using a resize policy of 640px.  Then run the infer_batch function on each bucket size
        resize_transform = ResizeWithAspectRatio(max_size=self.image_size, multiples=32)
        img_sizes = [resize_transform.get_resized_size(*imagesize.get(fpath)) for fpath in paths]
        main_dict = {}
        
        c = Counter()
        c.update(img_sizes)
        
        img_sizes_set = sorted(list(set(img_sizes)), reverse=True)
        parameters.log.info(f"working on the following batch sizes:")
        
        misc_sizes = {size for size in img_sizes_set if c[size] < batch_size}
        non_misc_size = [size for size in img_sizes_set if size not in misc_sizes]
        misc_path_subset = [p for p, s in zip(paths, img_sizes) if s in misc_sizes]
        
        for size in non_misc_size:
            parameters.log.info(f"{size} : {c[size]}")
        parameters.log.info(f"sum of misc size (running batch 1) : {len(misc_path_subset)}")
        
        for size in non_misc_size:    
            path_subset = [p for p, s in zip(paths, img_sizes) if s == size]
            main_dict.update(self.infer_batch(path_subset, batch_size)) # update main dict with results
        
        if misc_path_subset:
            main_dict.update(self.infer_batch(misc_path_subset, 1))
            
        return main_dict
             
    @torch.no_grad()  
    def infer_batch(self, paths, batch_size=1): 
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
