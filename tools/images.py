import os.path
import pathlib
from PIL import Image
from PIL.ExifTags import TAGS

import numpy as np
import concurrent.futures

import math
# cv2 is a backup library for high bitrate images (32 bit, 4 channel imgs) that pillow doesn't support
import cv2

from src_files.data.path_dataset import PathDataset_test
from imgutils.ocr import detect_text_with_ocr

from timeit import default_timer as timer
from functools import wraps

from resources import parameters
from tools import files

import torch
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.dataloader import default_collate
from tqdm.auto import tqdm
from collections import Counter, defaultdict

import imagesize

# the 89478485 is the default value (0.5gb), so we're basically raising the limit to 1gb
Image.MAX_IMAGE_PIXELS = 89478485 * 2
COMPATIBLE_IMG_TYPES = ('RGB', 'RGBA', '1', 'L', 'P')

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = timer()
        result = f(*args, **kw)
        te = timer()
        parameters.log.info('func:%r took: %2.4f sec' % \
          (f.__name__, te-ts))
        return result
    return wrap

def custom_collate(batch):
    len_batch = len(batch)
    batch = list(filter(lambda x : x[0] is not None, batch))
    if len_batch > len(batch): # if there are samples missing just use existing members, doesn't work if you reject every sample in a batch
        diff = len_batch - len(batch)
        batch = batch + batch[:diff] # assume diff < len(batch)
    return default_collate(batch)

@torch.no_grad()
def infer_batch(path, trans, bs=8, remove_exif=False):
    # this is copy of the inference loop for CAformer, without the actual model
    # this is repurposed to iterate through the dataset and catch bad images
    # some images are converted and some are printed
    dupe_paths = []
    used_paths = []
    dataset = PathDataset_test(path, trans, remove_exif=remove_exif, break_on_monocolor=True)
    loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=4, shuffle=False, collate_fn=custom_collate)
    for _, path_list in tqdm(loader):
        used_paths.extend(path_list)
        dupe_path = list(set([x for x in path_list if path_list.count(x) > 1]))
        if dupe_path:
            dupe_paths.append(dupe_path)
    diff = set(path) - set(used_paths)
    return dupe_paths, diff

def get_corrupted_images(folder, bs=8, remove_exif=False):
    all_images = files.get_all_images_in_folder(folder)
    trans = transforms.Compose([
                                    transforms.Resize((128, 128)),
                                    transforms.ToTensor(),
                                ])
    # return the bad images
    
   
    dupes, unused = infer_batch(all_images, trans, bs, remove_exif=remove_exif)
  
    f_dict = get_file_extension_breakdown(all_images)
    parameters.log.info(f"Here's the count of file types: {f_dict.items()}")
    
    return unused

def get_file_extension_breakdown(paths):
    f_ext = {}
    for p in paths:
        filename, file_extension = os.path.splitext(p)
        if file_extension in f_ext:
            f_ext[file_extension] +=1
        else:
            f_ext[file_extension] = 1
    return f_ext

def is_row_approximately_similar2(row_data):
    mean = np.mean(row_data, axis=0)
    return np.all(np.abs(row_data - mean) < 35)

def sudden_crop(row_data, prev_row, row_size):
    # check the current row and return true if 30% or more is different from the row/column before
    prev_avg = np.mean(prev_row, axis=0)
    sudden_change = (np.abs(row_data - prev_avg) < 35).sum()
    if (row_size-sudden_change)/row_size > 0.3:
        return True
    return False

def border_transparency(img: pathlib.Path, base_dir, crop_empty_space=True, crop_empty_border=True,
                        fill_stray_signature=True,  use_thumbnail=False, fill_transparent=True):
    #parameters.log.debug("Opening image")
    try:
        original_image = Image.open(img)
    except Exception as e:
        parameters.log.exception("Trying to convert png via cv2, solved for iCCP: CRC error", exc_info=e)
        ext = os.path.splitext(img)
        if ext[1].lower() == ".png":
            cv2_img = cv2.imread(img, -1)
            cv2.imwrite(img, cv2_img)
            # use conversion below for direct cv2 --> pillow, bc different RBG standards
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            parameters.log.warning(img, "Check img format and if it's compatible with pillow or cv2")
        original_image = Image.open(img)
        
    #parameters.log.info("Image opened")
    filled = False
    #parameters.log.info(original_image.mode)
    if original_image.has_transparency_data: # fill transparent images
        filled = True
        temp_image = original_image
        if original_image.mode != "RGBA":
            temp_image = temp_image.convert('RGBA')
        
        extrema = temp_image.getextrema() # since img is rgba, we have a list of 4 tuples [(min, max) x 4]
        if extrema[3][0] < 255:
            blank_image = Image.new('RGBA', temp_image.size, (255, 255, 255, 255))
            blank_image.alpha_composite(temp_image)
            image = blank_image.convert('RGB')
        else: # all alpha channels are 255, save rgb one to save memory
            image = temp_image.convert("RGB")
    else:
        try:
            image = original_image.convert('RGB')
        except OSError as e:
            # image is truncated
            parameters.log.info(f"{e}, {img}")
            files.export_images(img,base_dir, "ERROR_FILES")
            return None, None, False, False, None

    owidth, oheight = image.width, image.height
    left, upper, right, lower = 0,0,owidth, oheight
    # we subtract one cause this is the index used for the numpy array
    left_col, top_row, right_col, bottom_row  = 0, 0,image.width - 1, image.height - 1
    text_bboxes = []
    if fill_stray_signature: # fill floating signatures
        text_bboxes = detect_text_with_ocr(image)
        for bbox in text_bboxes: # there can be multiple bboxes
            #bbox = [upper left corner x, upper left corner y, lower right corner x, lower right corner y]
            mini_crop = np.array(image.crop(bbox[0]))
            mini_w, mini_h, _ = mini_crop.shape
            mini_top, mini_bottom = mini_crop[0,:,:], mini_crop[mini_w-1,:,:]
            mini_left, mini_right = mini_crop[:,0,:], mini_crop[:,mini_h-1,:]


            if (np.array_equal(mini_top, mini_bottom) and np.array_equal(mini_left, mini_right) 
            and np.allclose(np.mean(mini_top, axis=0), np.mean(mini_left, axis=0))):
                
                color = tuple(mini_top[0])
                image.paste(color, bbox[0])


    pixels_data = np.array(image)
    half_ow, half_oh = int(owidth/2), int(oheight/2)
    if crop_empty_space:
        # jump is going to be 1% of the img, we calculated 1% is better than having a fixed step
        jump = int(0.01*max(oheight, owidth))
        while is_row_approximately_similar2(pixels_data[top_row,:,:]) and top_row < half_oh-10:
            top_row += 1
            if is_row_approximately_similar2(pixels_data[top_row+jump,:,:]):
                top_row+=jump+1
            
        while is_row_approximately_similar2(pixels_data[:,left_col,:])and left_col < half_ow-10:
            left_col += 1
            if is_row_approximately_similar2(pixels_data[:,left_col+jump,:]):
                left_col+=jump+1

        while is_row_approximately_similar2(pixels_data[bottom_row,:,:]) and bottom_row > half_oh+10:
            bottom_row -= 1
            if is_row_approximately_similar2(pixels_data[bottom_row-jump,:,:]):
                bottom_row-=(jump+1)
            
        while is_row_approximately_similar2(pixels_data[:,right_col,:]) and right_col > half_ow+10:
            right_col -= 1
            if is_row_approximately_similar2(pixels_data[:,right_col-jump,:]):
                right_col-=(jump+1)
        #parameters.log.info(top_row, left_col, bottom_row, right_col)

    # this is a buffer size, we require some buffer (empty space) with the image
    ohow_ratio = oheight/owidth
    owoh_ratio = owidth/oheight
    h_buf_percent = 0.025 if ohow_ratio < 2 else 0.01
    w_buf_percent = 0.025 if owoh_ratio < 2 else 0.01
    buffer_h = int(oheight * h_buf_percent)
    buffer_w = int(owidth * w_buf_percent)
    top_border, bottom_border, left_border, right_border = False, False, False, False
    border_blur = int(0.0025 * max(oheight, owidth))
    if crop_empty_border:
        if top_row > upper:
            top_border = sudden_crop(pixels_data[top_row+border_blur,:,:], pixels_data[top_row-1,:,:], owidth)
        if bottom_row < lower-1:
            bottom_border = sudden_crop(pixels_data[bottom_row+1,:,:], pixels_data[bottom_row-border_blur,:,:], owidth)
        if left_col > left:
            left_border = sudden_crop(pixels_data[:,left_col+border_blur,:], pixels_data[:,left_col-1,:], oheight)
        if right_col < right-1:
            right_border = sudden_crop(pixels_data[:,right_col+1,:], pixels_data[:,right_col-border_blur,:], oheight)
        
    
    # we update the boundary border, we include a pad if the background is a gradient or monocolor
    # we don't add a padding if the image has a border
    
    if oheight > 512:
        if top_border: 
            upper = top_row + border_blur # border blur basically cuts deeper if there's a sudden border
        elif top_row > buffer_h: # we add or subtract the buffer to add some spacing, elif bc also not x_border
            upper = top_row - buffer_h
        if bottom_border:
            lower = bottom_row - border_blur
        elif lower - bottom_row > buffer_h:
            lower = bottom_row + buffer_h   
    if owidth > 512:
        if left_border:
            left = left_col + border_blur
        elif left_col > buffer_w:
            left = left_col - buffer_w
        if right_border:
            right = right_col - border_blur
        elif right - right_col > buffer_w:
            right = right_col + buffer_w
    
    
    
    new_width = right-left
    new_height = lower-upper
    # if original image has a H-W ratio below 2, and the post-ratio is too much cropping, skip and let it be a manual problem
    post_img_ratio = 2.4
    nhnw_ratio = new_height/new_width
    
    nwnh_ratio = new_width/new_height
    
    if nhnw_ratio > post_img_ratio:
        if ohow_ratio <= 2 or (left != 0 or right != owidth):
            parameters.log.info(f"Check: {img}\nImg too tall for horizontal crop, skipping horizontal crop, ratio: {ohow_ratio:0.2f}/{1} --> {nhnw_ratio:0.2f}/{1}")
            left = 0
            right = owidth
             
    if nwnh_ratio > post_img_ratio:
        if owoh_ratio <=2 or (upper != 0 or lower != oheight):
            parameters.log.info(f"Check: {img}\nImg too wide for vertical crop, skipping vertical crop, ratio: {1}/{owoh_ratio:0.2f} --> {1}/{nwnh_ratio:0.2f}")
            upper = 0
            lower = oheight
    
    
    
    cropped = (left != 0 or right != owidth or upper != 0 or lower != oheight)
    if cropped:
        parameters.log.debug(f"Crop needed for: {img}")
        image = image.crop((left, upper, right, lower))
    return original_image, image, cropped, filled, text_bboxes

def overlapping_area(coord1, coord2):
    """input coords is the format as (top, left, width, height)"""
    rect1 = (coord1[0], coord1[1],coord1[0]+coord1[2], coord1[1]+coord1[3])
    rect2 = (coord2[0], coord2[1],coord2[0]+coord2[2], coord2[1]+coord2[3])
    dx = min(rect1[2], rect2[2]) - max(rect1[0], rect2[0])
    dy = min(rect1[3], rect2[3]) - max(rect1[1], rect2[1])
    area = dx * dy
    if dx < 0 or dy < 0:
        # no overlap
        area = 0
    return area   

def overlapping_area_ratio(coord1, coord2):
    """return the overlapping area ratio from the perspectuve of the first coord

    Args:
        coord1 (_type_): _description_
        coord2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    overlap_area = overlapping_area(coord1, coord2) 
    self_area = coord1[2] * coord1[3]
    ratio = overlap_area / self_area
    return ratio
    
# we're going to use the base function over this one since the one above is faster for full img,
# this one is faster if use_thumbnail is set to true


def border_transparency2(img_path, crop_empty_space=True,fill_stray_signature=True, use_thumbnail=True):
    original_image = Image.open(img_path)
    filled = False
    if original_image.mode == 'RGBA':
        filled = True
        original_image = Image.alpha_composite(Image.new('RGBA', original_image.size, (255, 255, 255)), original_image).convert('RGB')
    else:
        original_image = original_image.convert('RGB')
    #bbox_list = detect_text_with_ocr(original_image)
    #if bbox_list:
    #    for bbox in bbox:
    #        text_selection = im.crop(())
    # use a smaller img for faster/simpler process, using 256 to minimize margin of error
    if use_thumbnail:
        o_size = original_image.size # width, height, channel
        scale_factor = min(256/o_size[0], 256/o_size[1])
        parameters.log.debug(scale_factor)
        image = original_image.resize((int(o_size[0]*scale_factor), int(o_size[1]*scale_factor)))
    else:
        image = original_image

    pixel_data = np.array(image)
    oheight, owidth, _ = pixel_data.shape
    err_threshold = 35
    width_pad, height_pad = int(owidth * 0.025), int(oheight * 0.025)

    # get the averages along the row and columns
    row_avg = np.sum(pixel_data, axis=1, keepdims=True)/owidth
    col_avg = np.sum(pixel_data, axis=0, keepdims=True)/oheight
    # use all to make a vector mask when all pixels in a row/column is under the threshold
    row_cond = np.all((np.abs(pixel_data-row_avg) < err_threshold), axis=(2, 1))
    col_cond = np.all((np.abs(pixel_data-col_avg) < err_threshold), axis=(2, 0))
    # get the first and last occurence of the conditions.  
    # If a pic has lots of white empty space above and below and a character in the middle
    # then the row_cond looks like [True, True,... True, False, ... False, True, ..., True], identifying which rows we can remove
    upper, lower, left, right = np.argmin(row_cond), np.argmin(np.flip(row_cond)), np.argmin(col_cond), np.argmin(np.flip(col_cond))
    upper_flat, lower_flat, left_flat, right_flat = False, False, False, False


    if use_thumbnail:
        upper, lower, left, right = int(upper/scale_factor), int(lower/scale_factor), int(left/scale_factor), int(right/scale_factor)
        width_pad, height_pad = int(width_pad/scale_factor), int(height_pad/scale_factor)
        owidth, oheight = o_size[0], o_size[1]

    left = max(0, left - width_pad)
    right = min(owidth, (owidth - right) + width_pad)
    upper = max(0, upper - height_pad)
    lower = min(oheight, (oheight - lower) + height_pad)
    cropped = (left != 0 or right != owidth or upper != 0 or lower != oheight)
    parameters.log.debug(left, right, upper, lower)
    parameters.log.debug(0, owidth, 0,  oheight)

    


    if cropped:
        parameters.log.debug(f"Img before: {image.size}")
        original_image = original_image.crop((left, upper, right, lower))
        parameters.log.debug(f"Img after: {image.size}")

    return original_image, cropped, filled

def round_and_crop_to_bucket(x:float, reso_step=64) -> int:
    x = int(x+0.5) # round to nearest int
    return x - x%reso_step # crop to nearest multiple of reso_step

def get_bucket_size(image_height, image_width, base_height=1024, base_width=1024, bucket_steps=64) -> tuple[int, int]:
        # we didn't impliment upscale in this bucket size cause it's not a feature we use
        
        # implimentation from kohya's bucket manager with some explanation of the math behind it
        #base h x w is (1024, 1024) for XL and (512 x 512) or (768, 768) for SD1.5 and SD2
        image_ratio = image_width / image_height
        max_area = base_height * base_width
        if image_width* image_height > max_area: # we need to rescale the image down
            # explanation of the sqrt in kohya's code:
            # (w, h) is the image resolution, s is the scale factor needed to resize the image
            # (w_res, h_res) is the resolution used for the max area
            # max_area = w_res * h_res and AR (aspect ratio) = w/h
            # the max area is also equal to s*w * s*h, because the rescaled image needs to fit in the max area
            # the goal is to find either s*w or s*h, which is one of the rescaled sizes 
            # so we do s*w = sqrt(max_area * AR) = sqrt(s*w * s*h * w/h) = sqrt(s^2 * w^2)
            
            resized_width = math.sqrt(max_area * image_ratio)
            resized_height = max_area / resized_width
            assert abs(resized_width / resized_height - image_ratio) < 1e-2, "aspect is illegal"
        
            # at this point, resized_width and height are floats and we need to get the closest int value
            
            # bucket resolution by clipping based on width
            b_width_rounded = round_and_crop_to_bucket(resized_width)
            b_height_in_wr = round_and_crop_to_bucket(b_width_rounded / image_ratio)
            ar_width_rounded = b_width_rounded / b_height_in_wr
            
            # bucket resolution by clipping based on height
            b_height_rounded = round_and_crop_to_bucket(resized_height)
            b_width_in_hr = round_and_crop_to_bucket(b_height_rounded * image_ratio)
            ar_height_rounded = b_width_in_hr / b_height_rounded
            
            # check the error between the aspect ratio and choose the one that's smallest
            # most times the resulting bucket size would be the same
            if abs(ar_width_rounded - image_ratio) < abs(ar_height_rounded - image_ratio):
                resized_size = (b_width_rounded, int(b_width_rounded / image_ratio + 0.5))
            else:
                resized_size = (int(b_height_rounded * image_ratio + 0.5), b_height_rounded)
        
        else:
            resized_size = (image_width, image_height)
        
        # remove any outer pixels from the bottom and right of the image that doesn't match the bucket steps (usualy 64)
        bucket_width = resized_size[0] - resized_size[0] % bucket_steps
        bucket_height = resized_size[1] - resized_size[1] % bucket_steps
        
        bucketed_resolution = (bucket_width, bucket_height)
        
        return bucketed_resolution
    
def similarity_example(images_paths,*, threshold=0.9, hash_size=32, bands=32):
    near_duplicates = files.find_near_duplicates(images_paths, threshold=threshold, hash_size=hash_size, bands=bands)
    if near_duplicates:
        parameters.log.info(f"Found {len(near_duplicates)} near-duplicate images in images (threshold {threshold:.2%})")
        for a,b,s in near_duplicates:
            parameters.log.info(f"{s:.2%} similarity: file 1: {a} - file 2: {b}")
    else:
        parameters.log.info(f"No near-duplicates found in images (threshold {threshold:.2%})")

# testing below ###############

def make_bucket_resolutions(max_reso=(1536, 1536), min_size=512, max_size=2048, divisible=64):
    max_width, max_height = max_reso
    max_area = max_width * max_height
    resos = set()
    width = int(math.sqrt(max_area) // divisible) * divisible
    resos.add((width, width))
    width = min_size
    while width <= max_size:
        height = min(max_size, int((max_area // width) // divisible) * divisible)
        if height >= min_size:
            resos.add((width, height))
            resos.add((height, width))
            # there were some code here that was commented, but removed for space
        width += divisible

    resos = list(resos)
    resos.sort()
    return resos

class bucket_manager_simple():
    def __init__(self):
        self.bucket_reso = 1536
        self.bucket_reso_tuple = (self.bucket_reso, self.bucket_reso)
        self.max_bucket_reso = 2048
        self.min_bucket_reso = 512
        self.bucket_steps = 64
        self.max_area = self.bucket_reso * self.bucket_reso
        self.bucket_shapes = make_bucket_resolutions(self.bucket_reso_tuple, self.min_bucket_reso, self.max_bucket_reso, self.bucket_steps)
        self.bucket_counter = Counter()
        
    def select_bucket(self, image_width, image_height):
        aspect_ratio = image_width / image_height
        if image_width * image_height > self.max_area: # downsampling needed (keep aspect ratio)
            resized_width = math.sqrt(self.max_area * aspect_ratio)
            resized_height = self.max_area / resized_width
            assert abs(resized_width / resized_height - aspect_ratio) < 1e-2, "aspect is illegal"
            # resize image by scaling the height or width to the closest multiple of the bucket resolution
            # then choose the resize that has the smallest aspect ratio difference 
            b_width_rounded = self.round_to_steps(resized_width)
            b_height_in_wr = self.round_to_steps(b_width_rounded / aspect_ratio)
            ar_width_rounded = b_width_rounded / b_height_in_wr

            b_height_rounded = self.round_to_steps(resized_height)
            b_width_in_hr = self.round_to_steps(b_height_rounded * aspect_ratio)
            ar_height_rounded = b_width_in_hr / b_height_rounded

            if abs(ar_width_rounded - aspect_ratio) < abs(ar_height_rounded - aspect_ratio):
                resized_size = (b_width_rounded, int(b_width_rounded / aspect_ratio + 0.5))
            else:
                resized_size = (int(b_height_rounded * aspect_ratio + 0.5), b_height_rounded)
        else: # no need to resize
            resized_size = (image_width, image_height) 

        bucket_width = resized_size[0] - resized_size[0] % self.reso_steps
        bucket_height = resized_size[1] - resized_size[1] % self.reso_steps
        reso = (bucket_width, bucket_height)
        ar_error = (reso[0] / reso[1]) - aspect_ratio
        return reso, resized_size, ar_error

    def update_counter(self, bucket_info):
        self.bucket_counter.update(bucket_info)
        

def get_crop_ltrb(bucket_reso, image_size):
        bucket_ar = bucket_reso[0] / bucket_reso[1]
        image_ar = image_size[0] / image_size[1]
        if bucket_ar > image_ar:
            # bucketのほうが横長→縦を合わせる
            resized_width = bucket_reso[1] * image_ar
            resized_height = bucket_reso[1]
        else:
            resized_width = bucket_reso[0]
            resized_height = bucket_reso[0] / image_ar
        crop_left = (bucket_reso[0] - resized_width) // 2
        crop_top = (bucket_reso[1] - resized_height) // 2
        crop_right = crop_left + resized_width
        crop_bottom = crop_top + resized_height
        return crop_left, crop_top, crop_right, crop_bottom

#from kohya, train_util.py, simplified a bit
def trim_and_resize_if_required(image: Image.Image, expected_bucket_reso, resized_size):
    image_height, image_width = image.shape[0:2]
    original_size = (image_width, image_height)  # size before resize

    if image_width != resized_size[0] or image_height != resized_size[1]:
        image = cv2.resize(image, resized_size, interpolation=cv2.INTER_AREA)

    image_height, image_width = image.shape[0:2]

    if image_width > expected_bucket_reso[0]:
        trim_size = image_width - expected_bucket_reso[0]
        p = trim_size // 2 
        # logger.info(f"w {trim_size} {p}")
        image = image[:, p : p + expected_bucket_reso[0]]
    if image_height > expected_bucket_reso[1]:
        trim_size = image_height - expected_bucket_reso[1]
        p = trim_size // 2 
        # logger.info(f"h {trim_size} {p})
        image = image[p : p + expected_bucket_reso[1]]

    crop_ltrb = get_crop_ltrb(expected_bucket_reso, original_size)

    assert (image.shape[0] == expected_bucket_reso[1] 
            and image.shape[1] == expected_bucket_reso[0]), (
            f"internal error, illegal trimmed size: {image.shape}, {expected_bucket_reso}")
            
    # image is already resized and trimmed at this point, the returned values are direclty converted to np arrays and
    # used elsewhere via npz format and latents
            
    return image, original_size, crop_ltrb

def likly_gradient(img_object):

    np_img = np.array(img_object.convert('RGB'))

    min_channel = np.min(np_img, axis=-1)
    max_channel = np.max(np_img, axis=-1)
    diff_channel = max_channel - min_channel

    # check for monocolor:
    colored_avg = np.average(diff_channel > 10)
    if colored_avg < 0.01: # if less than 1% of the img has non-gray color
        return 0

    # adapted skin color detection to numpy from here:
    # https://github.com/WillBrennan/SkinDetector/blob/master/skin_detector/skin_detector.py

    def get_rgb_mask(rgb_img, diff_chan):
        lower_thresh = np.array([0, 50, 0], dtype=np.uint8)
        upper_thresh = np.array([255, 230, 220], dtype=np.uint8)

        # idk if the 255 multiplier is necessary
        #mask_a = 255 * np.all(np.logical_and(rgb_img > lower_thresh, rgb_img < upper_thresh), axis=-1)
        #parameters.log.debug(mask_a[0, 0])

        # idk where they got the 20 and 255 from, no info regarding experiments or numerical calculations for them
        #mask_b = 255 * ((rgb_img[:, :, 2] - rgb_img[:, :, 1]) / 20)
        #mask_c = 255 * (diff_chan / 20)
        #mask_d = np.bitwise_and(np.uint64(mask_a), np.uint64(mask_b))
        #mask_rgb = np.bitwise_and(np.uint64(mask_c), np.uint64(mask_d))

        #mask_rgb[mask_rgb < 128] = 0
        #mask_rgb[mask_rgb >= 128] = 1

        r_g_dominant = rgb_img[:, :, 0] > rgb_img[:, :, 1]

        mask_rgb = np.all(np.logical_and(rgb_img > lower_thresh, rgb_img < upper_thresh), axis=-1)

        mask_rgb = np.logical_and(r_g_dominant, mask_rgb)
        mask_rgb = np.logical_and(diff_chan, mask_rgb)
        parameters.log.debug("RBG", mask_rgb[70])
        return mask_rgb.astype(float)


    def get_hsv_mask(hsv_img):
        parameters.log.debug("HSV", hsv_img)
        lower_thresh = np.array([45, 52, 108], dtype=np.uint8)
        upper_thresh = np.array([255, 255, 255], dtype=np.uint8)
        mask_hsv = np.all(np.logical_and(hsv_img > lower_thresh, hsv_img < upper_thresh), axis=-1)
        parameters.log.debug("HSV", mask_hsv[70])
        return mask_hsv.astype(float)

    def get_ycrcb_mask(ycrcb_img):
        parameters.log.debug("YCBR",ycrcb_img)
        lower_thresh = np.array([90, 100, 130], dtype=np.uint8)
        upper_thresh = np.array([230, 120, 180], dtype=np.uint8)
        mask_ycrcb = np.all(np.logical_and(ycrcb_img > lower_thresh, ycrcb_img < upper_thresh), axis=-1)
        parameters.log.debug("YCBR", mask_ycrcb[70])
        return mask_ycrcb.astype(float)

    mask_hsv = get_hsv_mask(np.array(img_object.convert('HSV')))
    mask_rgb = get_rgb_mask(np_img, diff_channel)
    mask_ycrcb = get_ycrcb_mask(np.array(img_object.convert('YCbCr')))

    n_masks = 3.0
    mask = (mask_hsv + mask_rgb + mask_ycrcb) / n_masks
    parameters.log.debug(mask)
    thresh=0.5
    mask[mask < thresh] = 0
    mask[mask >= thresh] = 1
    mask = mask.astype(int)


    mask = mask[:, np.newaxis]

    parameters.log.debug("Avg mask", mask.shape)
    parameters.log.debug("Img", np_img.shape)
    masked_values = np_img
    masked_values[mask] = [0, 0, 0]
    """
    from PIL import Image
    #parameters.log.info("masked val", masked_values.shape, masked_values)
    from matplotlib import pyplot as plt
    img = Image.fromarray(masked_values, 'RGB')
    img.show()
    x = input("next")
    """
    return np.average(mask)


def fake_gradient(img_object):
    np_img = np.array(img_object.convert('RGB'))
    H, W, _ = np_img.shape
    min_channel = np.min(np_img, axis=-1)
    max_channel = np.max(np_img, axis=-1)
    diff_channel = max_channel - min_channel

    # check for monocolor:
    colored_avg = np.average(diff_channel > 10)
    if colored_avg < 0.01: # if less than 1% of the img has non-gray color
        return 0
    flat_image = np_img.reshape(-1, 3)
    colors, counts = np.unique(flat_image, return_counts = True, axis = 0)
    sorted_count = sorted(counts, reverse=True)
    max_color = 50
    curr_sum = 0
    # returns the number of colors needed to describe 80% of the img
    percent_ratio = 0.8
    HW = H*W
    parameters.log.debug(counts)
    for i, c in enumerate(sorted_count):
        curr_sum +=c
        if curr_sum/(HW) > percent_ratio:
            return i
        if c < 3 and i < max_color:
            return max_color
        elif c < 3 and i > max_color:
            return i

    return i


def intensity_count(img_object):
    # adapting code/theory from https://stackoverflow.com/a/58270890
    # I had similar idea of finding the contribution of blue on dark colors, but someone beat me to the punch
    # we also try to ignore white pixels, by removing pixels above (240, 240, 240) RGB
    np_img = np.array(img_object.convert('RGB'))
    np_square_img = np.square(np_img, dtype=np.float32)

    min_channel = np.min(np_img, axis=-1)
    max_channel = np.max(np_img, axis=-1)
    diff_channel = max_channel - min_channel

    # calculate brightness with rgb
    brightness_arr = (0.299 * np_square_img[:, :, 0]) + (0.587 * np_square_img[:, :, 1]) + (
                0.114 * np_square_img[:, :, 2])

    # 16256 ~ 127.5^2
    brightness_loc = brightness_arr > 16256
    bright_nonwhite_loc = np.logical_and(brightness_loc, diff_channel > 10)

    # group pixels into a 3x3 grid

    # zero initialization
    H, W, _ = np_img.shape
    grid_height = H // 3
    grid_width = W // 3
    grid_avg = np.zeros((3, 3), dtype=np.float32)
    for i in range(3):
        for j in range(3):
            start_row, start_col = i * grid_height, j * grid_width
            end_row = (i + 1) * grid_height if i < 2 else H
            end_col = (j + 1) * grid_width if j < 2 else W

            # Compute the average of the current grid cell
            grid_avg[i, j] = np.mean(brightness_loc[start_row:end_row, start_col:end_col], axis=(0, 1), dtype=np.float32)
    parameters.log.debug(grid_avg)
    # sum of different grid shapes
    upper_sum = grid_avg[0, 0] + grid_avg[0, 1] + grid_avg[0, 2]
    upper_n_sum = upper_sum + grid_avg[1, 0] + grid_avg[1, 2]
    upper2_sum = upper_n_sum + grid_avg[1,1]
    lower_sum = grid_avg[2, 0] + grid_avg[2, 1] + grid_avg[2, 2]
    plus_shaped_sum = grid_avg[0,1] + grid_avg[1,0] + grid_avg[1,1] + grid_avg[1,2] + grid_avg[2,1]
    quadrent_sum = grid_avg[0,0] + grid_avg[0,2] + grid_avg[2,0] + grid_avg[2,2]

    # difference of different grid shapes
    center_diff = max(plus_shaped_sum/5 - quadrent_sum/4, 0.001)
    top_bottom_diff = max(np.average(upper_sum/3 - lower_sum/3), 0.001)
    bottom_top_diff = max(np.average(lower_sum/3 - upper_sum/3), 0.001)
    bottom_top2_diff = max(np.average(lower_sum/3 - upper2_sum/6), 0.001)
    parameters.log.debug(center_diff, top_bottom_diff, bottom_top_diff)

    brightness_ratio = np.average(bright_nonwhite_loc)

    contrast = 0
    underlight = 0
    if brightness_ratio > 0.005:
        if center_diff > 0.1: # if center is significantly brighter than the surroundings
            contrast = center_diff
        elif top_bottom_diff > 0.1: # if upper is significantly brighter than lower
            contrast = top_bottom_diff
        elif bottom_top_diff > 0.1:
            contrast = bottom_top_diff
        else:
            contrast = max(center_diff, top_bottom_diff, bottom_top_diff)

        if bottom_top2_diff > 0.1: # if lower is brighter than upper
            underlight = bottom_top2_diff

    return np.average(np_img), brightness_ratio, underlight, contrast

def resize_image_keep_aspect(image, max_size=2048):
    """Resize image while maintaining aspect ratio, ensuring max dimensions do not exceed max_size."""
    h, w = image.shape[:2]
    scale = min(max_size / w, max_size / h)
    new_w, new_h = int(w * scale), int(h * scale)
    return  cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

print_bool = True

def detect_compression_artifacts(image_path):
    """Detect JPEG compression artifacts using OpenCV."""
    # Load image in grayscale for processing
    # File size in KB
    
    default_value={
        "file_size_kb": -1,
        "sharpness (Laplacian Variance)": -1,
        "blockiness": -1,
        "compression_severity": "N/A"
    }
    
    
    width, height = imagesize.get(image_path)
    if width > 1536 and height > 1536:
        return default_value
    elif image_path.endswith(".png") and width * height > 2022400: #1280 * 1280, note 1024*1.25 = 1280
        return default_value
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return "Error: Could not load image."
    h, w = img.shape[:2]
    if h > 2048 or w > 2048:
        img = resize_image_keep_aspect(img)
        h, w = img.shape[:2]

    # Measure sharpness using Laplacian variance
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()

    # Detect block artifacts
    dct_size = 8  # (JPEG compression is based on 8x8 DCT)
    threshold = 5 # checking for images with more than 5 pixel STD
    # get the number of blocks in h and w
    h_block_count = h//dct_size
    w_block_count = w//dct_size
    
    def get_spaced_elem(block_count, numElems=11): # we get sampled 0.1, 0.2, ..., 0.9, by removing the endpoints (0, and 1)
        sampled_index_with_endpoint = np.round(np.linspace(0, block_count-1, numElems)).astype(int)
        sampled_index = sampled_index_with_endpoint[1:-1]
        return sampled_index
    
    # we sample row and column every 10%, so we sample 9 rows (8px*w) and columns (8px*h) 
    row_blocks = [img[i:i+dct_size, (hb*dct_size)-1 : (hb*dct_size)+7] 
                  for i in range(0, h - (dct_size-1), dct_size) 
                  for hb in get_spaced_elem(w_block_count)]
    col_blocks = [img[(wb*dct_size)-1 : (wb*dct_size)+7, j:j+dct_size]
                  for j in range(0, w - (dct_size-1), dct_size) 
                  for wb in get_spaced_elem(h_block_count)] 
    
    # Apply DCT to each block that contains differences in pixel ranges (eg skip monocolor blocks)
    filtered_blocks = [block for block in (row_blocks + col_blocks) if np.std(block) > threshold]
    dct_blocks = [cv2.dct(np.float32(block)) for block in filtered_blocks]
    
        
    
    # dct (discrete cosine transformation) has the average frequencies on top left and high-frequency on bottom right
    # Measure high-frequency components
    artifact_score = np.mean([np.abs(dct[4:, 4:]).mean() for dct in dct_blocks])
    
    

    # Estimate compression severity
    compression_severity = "low"
    if artifact_score > 10 and laplacian_var < 100:
        compression_severity = "high"
    elif artifact_score > 5 or laplacian_var < 200:
        compression_severity = "medium"         
    file_size_kb = os.path.getsize(image_path) / 1024
    return {
        "file_size_kb": round(file_size_kb, 2),
        "sharpness (Laplacian Variance)": round(laplacian_var, 2),
        "blockiness": round(artifact_score, 2),
        "compression_severity": compression_severity
    }

def check_artifacts_multiple_images(image_paths: list) -> list:#not used
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=parameters.PARAMETERS["max_images_loader_thread"]) as executor:
        futures = {executor.submit(detect_compression_artifacts, path): path for path in image_paths}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(image_paths), desc="Checking Jpeg artifacts"):
            path = futures[future]
            try:
                results.append((path, future.result()))
            except Exception as e:
                print(f"Error processing {path}: {e}")
    
    return results

class ImageDataset(Dataset):
        def __init__(self, image_paths):
            self.image_paths = image_paths
        
        def __len__(self):
            return len(self.image_paths)
        
        def __getitem__(self, idx):
            image_path = self.image_paths[idx]
            return image_path, detect_compression_artifacts(image_path)
def collate_fn_unmerged_result(batch):
    # Return batch as-is, without merging elements
    return list(zip(*batch))

def check_artifacts_with_dataloader(image_paths: list, batch_size=8, num_workers=4) -> list:
    results = {}
    dataset = ImageDataset(image_paths)
    dataloader = DataLoader(dataset, batch_size=batch_size, num_workers=num_workers, shuffle=False, collate_fn=collate_fn_unmerged_result)
    for paths, batch in tqdm(dataloader, total=len(dataloader), desc="Checking Jpeg artifacts"):
        #print(paths, batch)
        for path, result in zip(paths, batch):
            results[path] = result
    
    return results
import time

def detect_jpeg_artifacts(image_paths):
    # checks the files and returns a list of paths that contains jpeg artifacts
    t1 = time.time()
    
    results = check_artifacts_with_dataloader(image_paths)
    debug = True
    if debug:
        parameters.log.info(f"Printing img counts")
        c = Counter()
        c.update((os.path.splitext(i)[1] for i in image_paths))
        
        for k, v in c.most_common():
            parameters.log.info(f"Counter {k}, {v}")
        run_sum = 0
        for p, v in results.items():
            try:
                if v["compression_severity"] != "low":
                    run_sum+=1
            except:
                print(p, v)
        total_bad_jpegs = run_sum
        #total_bad_jpegs = sum([1 if v["compression_severity"] != "low" else 0 for p, v in results.items()])
        parameters.log.info(f"Total bad jpeg quality {total_bad_jpegs}")
    
    t2 = time.time()
    parameters.log.info(f"time taken, {t2-t1}")
    return results
    
def merge_overlapping_tuples(pair_list):
    # Build adjacency list
    graph = defaultdict(set)
    for a, b in pair_list:   
        graph[a].add(b)
        graph[b].add(a)

    # Perform DFS to find connected components
    visited = set()
    merged_groups = []

    def dfs(node, group):
        stack = [node]
        while stack:
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                group.add(curr)
                stack.extend(graph[curr] - visited)

    for node in graph:
        if node not in visited:
            group = set()
            dfs(node, group)
            merged_groups.append(tuple(sorted(group)))

    return merged_groups
def triangular_ij_pair(i_range:int, j_range:int): # if i==j: return n*n+1 / 2
    return [(i, j) for i in range(i_range) for j in range(j_range) if  i > j]

def clean_ocr(ocr_results):
    """
    input is a list of dict
    result = {
            "name": self.name,
            "coordinates": (self.top, self.left, self.width, self.height),
            "confidence": self.confidence
        }
    * there's cases of other data being contained in the dict due to the save function,
    when we merge rects, we'll keep the other metadata in the chosen "primary" rect
    
    ocr_results is a list of tuples and the first value in the tuple are values for the top left and bottom right corners
    Idea is similar to HDBSCAN, but there's few assumptions which guide the decision. 
    First, detected text (words, not characters) have a direction (vertical [japanese,chinese, etc] or horizontal [English, Japanese, chinese, etc])
    The detection box is padded very slightly via the detection algorithm's unclip_ratio value (default value : 2.0)
    Args:
        Ex: [( (x1, y1, width, height), _, _ ), ...]

    Returns:
        _type_: ocr_result with some boundary boxes merged
    """
    ocr_len = len(ocr_results)
    if ocr_len<= 1:
        return ocr_results

    index_dict = {i:r for i, r in enumerate(ocr_results)} # store reference to rect_objects
    coord_list = [index_dict[i]["coordinates"] for i in range(len(ocr_results))]

    # make a dictionary to store overlapping pairs, i --> list of overlapping idx
    overlap_dict = {i:[] for i in range(ocr_len)}
    
    for i, j in triangular_ij_pair(ocr_len, ocr_len):
        if overlapping_area(coord_list[i], coord_list[j]) > 0:
            overlap_dict[i] = overlap_dict.get(i) + [j]
            
            overlap_dict[j] = overlap_dict.get(j) + [i]
    #print(overlap_dict.items())
    # separate horizontal and vertical rects
    h_rect_idx, v_rect_idx = [], []
    for i, coord in enumerate(coord_list):
        width, height = coord[2], coord[3]
        if height > width:
            
            v_rect_idx.append(i)
        else:
            
            h_rect_idx.append(i)
    
    # vertical_case
    v_result = merge_rects(v_rect_idx, overlap_dict, coord_list)
    h_result = merge_rects(h_rect_idx, overlap_dict, coord_list, vertical_orientation=False)
    
    new_list = []
    remove_val = set()
    for main_index, remove_indicies, new_coord in v_result + h_result:
        new_list.append(index_dict[main_index])
        remove_val.add(main_index)
        remove_val.update(remove_indicies)
        new_list[-1]["coordinates"] = (new_coord[0], new_coord[1], new_coord[2], new_coord[3])
    for i in range(len(ocr_results)):
        if i not in remove_val:
            new_list.append(index_dict[i])
    return new_list
    
def merge_rects(relevant_rect_idx, overlap_dict, ocr_results, vertical_orientation=True):
    merge_pairs = [] # pairs of indexes that can be paired, then we can group them via common values
    thresh = 0.15
    for i in relevant_rect_idx: 
        i_rect = ocr_results[i] #(x1, y1,width, height)
        i_height_thresh = int(thresh * i_rect[3])
        i_width_thresh = int(thresh * i_rect[2])
        
        if overlap_dict[i]:
            for j in overlap_dict[i]:
                j_rect = ocr_results[j]
                # since we're using x,y, width and height, we need to do some calculations to get the top and bottom
                # or left and right threashold values
                if vertical_orientation: 
                    if (i_rect[1]-i_height_thresh < j_rect[1] < i_rect[1]+i_height_thresh and
                        i_rect[1]+i_rect[3]-i_height_thresh < j_rect[1]+j_rect[3] < i_rect[1]+i_rect[3]+i_height_thresh): 
                        # check top and bottom is within threshold
                        merge_pairs.append((i, j))
                else: # horizontal rects
                    if (i_rect[0]-i_width_thresh < j_rect[0] < i_rect[0]+i_width_thresh and
                        i_rect[0]+i_rect[2]-i_width_thresh < j_rect[0]+j_rect[2] < i_rect[0]+i_rect[2]+i_width_thresh): 
                        # check top and bottom is within threshold
                        merge_pairs.append((i, j))
       
    
    # we now have all pairs that needs to be merged
    merged = merge_overlapping_tuples(merge_pairs)
    #print("merged", merged)
    new_result = []
    for merge_idx in merged:
        merge_idx = sorted(merge_idx)
        main_idx = merge_idx[0]
        #if len(merge_idx) ==2:
        #    print(f"r1 {ocr_results[merge_idx[0]]}, r2 {ocr_results[merge_idx[1]]}")
        other_idx = [idx for idx in merge_idx if idx != main_idx]
        new_x1 = min(ocr_results[i][0] for i in merge_idx)
        new_y1 = min(ocr_results[i][1] for i in merge_idx)
        
        new_x2 = max(ocr_results[i][0]+ocr_results[i][2] for i in merge_idx)
        new_y2 = max(ocr_results[i][1]+ocr_results[i][3] for i in merge_idx)
        new_result.append([main_idx, other_idx, (new_x1, new_y1, new_x2-new_x1, new_y2-new_y1)]) 
        #if len(merge_idx) ==2:
        #    print(new_result[-1][-1])
    return new_result 