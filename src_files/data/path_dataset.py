from torch.utils.data import Dataset
from PIL import Image
import os
import numpy as np

from PIL.ExifTags import TAGS 

from multiprocessing import Manager

COMPATIBLE_IMG_TYPES = ('RGB', 'RGBA', '1', 'L', 'P')
class PathDataset(Dataset):
    def __init__(self, img_list, transform=None):
        self.img_list = img_list
        self.transform = transform

    def __getitem__(self, index):
        path = self.img_list[index]
        img = Image.open(path).convert('RGB')
        img = self.transform(img)
        return img, path

    def __len__(self):
        return len(self.img_list)
    
class PathDataset_test(Dataset):
    
    def __init__(self, img_list, transform=None, convert_bhwc=False, convert_bgr=False, to_np=False, fill_transaprent=False, 
                 remove_exif=False, break_on_monocolor=False, shared_dict=None):
        self.img_list = img_list
        self.transform = transform
        self.convert_bhwc = convert_bhwc
        self.convert_bgr = convert_bgr
        self.to_np = to_np
        self.fill = fill_transaprent
        self.remove_exif = remove_exif
        self.break_on_monocolor = break_on_monocolor
        self.length = len(self.img_list) # assuming the dataset length doesn't change
        
        # https://github.com/ptrblck/pytorch_misc/blob/master/shared_dict.py
        if shared_dict:
            self.shared_dict = shared_dict
        else:
            m = Manager()
            self.shared_dict = m.dict()

    def __getitem__(self, index):
        path = self.img_list[index]
        if index not in self.shared_dict:
            try: # check for truncated images
                with Image.open(path) as img:
                    img_format = img.format.lower()
                    # https://stackoverflow.com/a/74188794
                    if self.remove_exif and (img_format == "jpeg" or img_format == "jpg"): 
                        # check corrupted exif , exif is only for jpeg for images
                        if img.getexif():
                            # create new image with the image data and return it
                            #print('removing EXIF from', path, '...')
                            data = list(img.getdata())
                            image_without_exif = Image.new(img.mode, img.size)
                            image_without_exif.putdata(data)
                            # convert to 
                            image_without_exif.save(path)
                            img = image_without_exif
                    if img_format not in ("png", "jpeg", "jpg"):
                        print(f"{path},from {img_format},to {os.path.splitext(path)[1][1:].upper()}")
                        # save as png and if it originally wasn't png, then delete the old one
                        img = img.convert('RGBA')
                        img.save(os.path.splitext(path)[0]+".png", "PNG")
                        if os.path.splitext(path)[0]+".png" != path: 
                            os.remove(path)
                            path = os.path.splitext(path)[0]+".png"
                    
                    if self.fill and img.has_transparency_data: 
                        if img.mode not in COMPATIBLE_IMG_TYPES:
                            img = img.convert('RGBA')
                        else:
                            img = img.convert('RGBA')
                        blank_image = Image.new('RGBA', img.size, (255, 255, 255))
                        blank_image.alpha_composite(img)
                        img = blank_image.convert('RGB')
                        
                    else:
                        if img.mode == "P": 
                            # some PNGS in P (Pallete) mode may have transparency embedded even if it's not PA mode
                            # IMG MODES: https://pillow.readthedocs.io/en/latest/handbook/concepts.html#modes
                            img = img.convert('RGBA')
                            
                        img = img.convert('RGB')
                    
                    if self.break_on_monocolor:
                        # this method will return none for monocolor images
                        monocolor_max_diff = 10
                        extrema = img.getextrema()
                        if all(extrema[i][1]-extrema[i][0] < 10 for i in range(3)):
                            print("all one color", path)
                            return None, path
                    
                    img = self.transform(img)
                    if self.convert_bhwc:
                        # https://discuss.pytorch.org/t/torchvision-totensor-dont-change-channel-order/82038/3
                        img = img.permute((1, 2, 0)).contiguous()
                    
                    if self.to_np:
                        img = np.array(img, dtype=np.float32)
                    if self.convert_bgr: # this converts RGB to BGR
                        channel_permute = [2, 1, 0]
                        img = img[:, :, channel_permute]
                        
                    self.shared_dict[index] = img
                    return img, path
            except Exception as e:
                print("\n",e, path)
                return None, path

        return self.shared_dict[index], path
            
    def __len__(self):
        return self.length 
    
class PathDataset_qtloader(Dataset):
    def __init__(self, img_list, max_size=128):
        self.img_list = img_list
        self.max_size = max_size

    def __getitem__(self, index):
        path = self.img_list[index]
        
        image_object = Image.open(path)
        image_object.thumbnail((self.max_size, self.max_size))
        if image_object.mode not in ('RGB', 'RGBA', '1', 'L', 'P'):
            image_object = image_object.convert('RGBA')
        
        return np.array(image_object)

    def __len__(self):
        return len(self.img_list)
    

class PathDataset_aesthetics(Dataset):
    def __init__(self, img_list, max_size=256, fill_transaprent=False, make_square=True):
        self.img_list = img_list
        self.max_size = max_size
        self.fill = fill_transaprent
        self.make_square = make_square

    def __getitem__(self, index):
        path = self.img_list[index]
        try: # check for truncated images
            with Image.open(path) as img:
                img_format = img.format.lower()
                if img_format not in ("png", "jpeg", "jpg"):
                    print(f"{path},from {img_format},to {os.path.splitext(path)[1][1:].upper()}")
                    # save as png and if it originally wasn't png, then delete the old one
                    img = img.convert('RGBA')
                    img.save(os.path.splitext(path)[0]+".png", "PNG")
                    if os.path.splitext(path)[0]+".png" != path: 
                        os.remove(path)
                        path = os.path.splitext(path)[0]+".png"
                if self.fill and img.has_transparency_data: 
                    if img.mode not in COMPATIBLE_IMG_TYPES:
                        img = img.convert('RGBA')
                    blank_image = Image.new('RGBA', img.size, (255, 255, 255))
                    blank_image.alpha_composite(img)
                    img = blank_image.convert('RGB')
                else:
                    if img.mode == "P": 
                        # some PNGS in P (Pallete) mode may have transparency embedded even if it's not PA mode
                        # IMG MODES: https://pillow.readthedocs.io/en/latest/handbook/concepts.html#modes
                        img = img.convert('RGBA')
                        
                    img = img.convert('RGB')
                
                # transformations
                size = img.size # width, height, channel
                if self.make_square:
                    new_im = Image.new('RGB', (self.max_size, self.max_size), (255, 255, 255))
                    new_im.paste(img, (int((self.max_size - size[0]) / 2), int((self.max_size - size[1]) / 2)))
                elif self.max_size:
                    
                    scale_factor = min(self.max_size/size[0], self.max_size/size[1])
                    #print(scale_factor)
                    img = img.resize((int(size[0]*scale_factor), int(size[1]*scale_factor)))
                
                return img, path
        except Exception as e:
            print("\n",e, path)
            return None, path

    def __len__(self):
        return len(self.img_list)


"""
        def custom_collate(batch):
            return default_collate(batch)
        print("loading images")
        dataset = PathDataset_qtloader([img.path for img in self.db.images], self.max_length)#collate_fn=custom_collate
        loader = torch.utils.data.DataLoader(dataset, batch_size=8, num_workers=4, shuffle=False)
        index = 0
        for img_thumbs in tqdm(loader):
            for thumb in img_thumbs:
                self.db.images[index].image_object = Image.fromarray(thumb)
                index+=1
        print("loaded imgs")
"""