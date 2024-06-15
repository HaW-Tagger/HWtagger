# code for editing safetensor header
# we assume safetensors made with darrian/easy_trainer, which might extend to kohya based models

import json
import struct

from resources import parameters


def open_safetensor(filename):
    # how to get header, from https://stackoverflow.com/a/77597522
    with open("lora.safetensors", "rb") as f:
        length_of_header = struct.unpack('<Q', f.read(8))[0]
        header_data = f.read(length_of_header)
        header = json.loads(header_data)

    parameters.log.info(header)  # should be a dict that contains what you need

    # idk how to save a new header.  # do it later