# Introduction
Most of our models, LORAs and the eclispeXL checkpoint (https://civitai.com/models/486131/eclipse-xl) were made using this tool.
Here is a link to the release article on civitai: https://civitai.com/articles/5751/hw-tagger-release

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
We both use python 3.10.11. Using this specific version of python is **HIGHLY** recommended because the last Tensorflow version that supports GPU on windows is compatible only up to python version 3.10.11.

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
