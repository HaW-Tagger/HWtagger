# Installation

We don't know if it works with linux, we don't have access to a computer running Linux and an NVIDIA card directly.

## Windows instructions

### If you own a NVIDIA GPU

You can install the CUDA toolkit and CUDNN versions 11.8 if you want to run the auto-taggers on your GPU, the app should work without it though, just slowly while using them.

You can follow this tutorial on how to install it:
https://medium.com/geekculture/install-cuda-and-cudnn-on-windows-linux-52d1501a8805#3e72
In the tutorial, it's also explained that to download the CUDNN installer you need an NVIDIA account.

### Installation

We assume you already have python installed, We both use python 3.10.11, other versions may work but the used libraries may require specific versions.

Clone the repository:
`
git clone https://github.com/HaW-Tagger/HWtagger/
`

Run the install.bat

Download the following models: https://huggingface.co/PhoenixAscencio/HWtagger and place the models folder in this repository

The installation should be done

### Running the tagger

You can run the tagger by using the run.bat

#### How to wiki link

https://github.com/HaW-Tagger/HWtagger/wiki/How-to-use-(basic-tutorial)
