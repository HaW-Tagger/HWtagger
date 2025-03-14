import os.path
import pathlib
from PIL import Image
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
from torch.utils.data.dataloader import default_collate
from tqdm.auto import tqdm


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

def border_transparency(img: pathlib.Path, crop_empty_space=True, crop_empty_border=True,
                        fill_stray_signature=True,  use_thumbnail=False):
    parameters.log.debug("Opening image")
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
        image = original_image.convert('RGB')

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
            bottom_border = sudden_crop(pixels_data[bottom_row-border_blur,:,:], pixels_data[bottom_row+1,:,:], owidth)
        if left_col > left:
            left_border = sudden_crop(pixels_data[:,left_col+border_blur,:], pixels_data[:,left_col-1,:], oheight)
        if right_col < right-1:
            right_border = sudden_crop(pixels_data[:,right_col-border_blur,:], pixels_data[:,right_col+1,:], oheight)
        
    

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
    post_img_ratio = 2.3
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