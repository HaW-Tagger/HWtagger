import os
os.environ["XFORMERS_FORCE_DISABLE_TRITON"] = "1"

import warnings
warnings.filterwarnings("ignore")

import torch
from torch.utils.data.dataloader import default_collate
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PIN_MEMORY = True if torch.cuda.is_available() else False

from src_files.data.path_dataset import PathDataset_test

# keep the contents of this file barebones and isolated as possible
# the pytorch dataloader imports the number of processes set by the number of workers
# and imports everything (reinitializes some stuff) to spawn x number of processes,
# so we want to avoid that 

# update: or I tried, can't get this to work, google or AI doesn't help

def custom_collate(batch):
    #len_batch = len(batch)
    return default_collate(batch)

def build_dataset(img_transformation, paths=[], bs=4, num_workers=4, use_bgr=False, reused_dataloader=None):
    # imgClassification, Image Completeness
    if reused_dataloader:
        return reused_dataloader
    # swin and other smilingwolf tagger uses bgr: https://huggingface.co/spaces/SmilingWolf/wd-tagger/blob/main/app.py
    dataset = PathDataset_test(paths, img_transformation, convert_bhwc=False, convert_bgr=use_bgr, 
                            to_np=True, fill_transaprent=True)
    loader = torch.utils.data.DataLoader(dataset, batch_size=bs, num_workers=num_workers, 
                                        shuffle=False, collate_fn=custom_collate, pin_memory=PIN_MEMORY)
    return loader