import tensorflow as tf

import sys
print(sys.version)

print(tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

import tensorflow.python.platform.build_info as build
print(build.build_info)

print("cuda version", build.build_info['cuda_version'])
print("cudnn version", build.build_info['cudnn_version'])