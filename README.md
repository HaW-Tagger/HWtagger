# Introduction
Most of our models, LORAs and the eclispeXL checkpoint (https://civitai.com/models/486131/eclipse-xl) were made using this tool.
Here is a link to the release article on civitai: https://civitai.com/articles/5751/hw-tagger-release

A changelog is available at the bottom of this page


# Installation

We don't know if it works with linux, we don't have access to a computer running Linux and an NVIDIA card directly, but it should work better if the dependencies are properly met. (Update: We have a few reports of it working with linux).

## Windows instructions

### If you own a NVIDIA GPU

The instructions requires installing the CUDA toolkit and CUDNN versions 11.8 if you want to run the auto-taggers on your GPU, the app should work without it though, just slowly while using them.

You can follow this tutorial on how to install it:
https://medium.com/geekculture/install-cuda-and-cudnn-on-windows-linux-52d1501a8805#3e72
In the tutorial, it's also explained that to download the CUDNN installer you need an NVIDIA account.

### Installation

We assume you already have python and git installed.
We both use python 3.10.11. Using this specific version of python is **HIGHLY** recommended because the last Tensorflow doesn't support GPUs on Windows starting from version 2.11, and xformers that is compatible with this version of tensorflow (2.10) requires python 3.10.
Tensorflow is only used to handle the dataloader for the code that loads the taggers, scorer, etc ... For Windows, any tensorflow version between 2.0.0 to 2.10 should be fine to use, any tensorflow version above 2.10 doesn't directly support GPUs on Windows, that's why we recommend using python 3.10.X
Even if you solve the tensorflow problem, you might hit a problem with xformers on windows, so this is the recommended version, because the compatibility between tensorflow, pytorch and xformers are resolved.
I want to make it compatible with all versions, but xformers and CUDA are a pain in the ass.

Clone the repository:
`
git clone https://github.com/HaW-Tagger/HWtagger/
`

Run the install.bat (make sure to have CUDA toolkit or else xformers may cause install errors)

- You can remove xformer and other libraries that's related to the gpu and the app will still work, but you'll have limitations with the tagger)

Download the following models: https://huggingface.co/PhoenixAscencio/HWtagger and place the models folder in this repository (models should be placed in the models folder, screenshot of folder structure attached in link).

The installation should be done

### Running the tagger

You can run the tagger by using the run.bat

*for linux, you might need to change how the venv is activated from .venv\scripts\activate to .venv\bin\activate

#### How to wiki link

https://github.com/HaW-Tagger/HWtagger/wiki/How-to-use-(basic-tutorial)

# Changelog

## 14/07/24
Added:
 - Rare tags count sort (less than 2% frequency)
 - Buttons to remove tags from a category
 - Frequency tags view tab with category filtering
 - Batch button to cleanup useless information in the rejected tags
 - Keybinds for next and prev (left arrow and right arrow), CTRLS+S for saving
 - BACKUP settings for files (CTRL+Z is WIP and is currently disabled because it costs too much RAM, need optimizations, but the logic is working)

Changes:
 - Maybe more accurate similarity detection so that it doesn't save the database when it holds the same information
 - Discarded batch button moves the file to a TEMP_DISCARDED folder and moves it to the DISCARDED folder when loading the database again
 - Popup image updated when selecting multiple images (mainly when selecting one image more)
 - Sample TOML creates a file directly and more settings, no settings for the positive and negative tags for now
 - Group names are available for search (check tooltip)

Fix:
 - Token length sort is sorting properly

## 25/06/24
- Changes: the scrollwheel doesn't affect the settings page anymore
- Changes: Added spacers to the database view and an highlight entry so that you can highlight certain tags, not saved
- Added: New button to filter the sentence (currently no logic is in it, so the button does nothing)
- Added: Export function to the database view, you can merge parts of one database to a new folder, either merging it to an existing database or creating a new database
- Added: sample TOML now creates a sample TOML in the location of the database that you can use in the LoraEasyTrainer (currently negative prompt and positive prompts are not visible in the settings)
- Fix: Negative search is working
- Fix: Sentence is now properly visible
- Fix: White base color in settings
- Fix: Tooltip show that you can click on w to go the the danbooru wiki for the selected tag 

## 17/06/24
 - Checks for a second model folder in case the first one fails
 - Fixed a folder path issue on linux
 - Fixed the xformers version/requirements
 - Added the image popup in the database viewer
 - Added confirmation dialogue when opening for edit multiple images
 - Updated the default parameters and added a reload default parameters button
 - Removed base danbooru filtering that cause weird behaviours with our own filtering
