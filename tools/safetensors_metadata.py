import os, torch, json, ast
from safetensors.torch import load_file, save_file, safe_open
from safetensors import safe_open

from resources import parameters


def load_metadata_from_safetensors(safetensors_file: str) -> dict:
    """
    This method locks the file. see https://github.com/huggingface/safetensors/issues/164
    If the file isn't .safetensors or doesn't have metadata, return empty dict.
    """
    if os.path.splitext(safetensors_file)[1] != ".safetensors":
        return {}

    with safe_open(safetensors_file, framework="pt", device="cpu") as f:
        metadata = f.metadata()
    if metadata is None:
        metadata = {}
    return metadata

def dict_from_str(key1, value1):
    dictionary = {}
    try:
        converted_str = ast.literal_eval(value1)
        if type(converted_str) is dict:
            for key2, value2 in converted_str.items():
                dictionary[key1] = dict_from_str(key2, value2)
        elif type(converted_str) is str:
            for element in converted_str:
                dictionary[key1] = dict_from_str(key1, element)
        elif type(converted_str) is list:
            for element in converted_str:
                dictionary[key1] = dict_from_str(key1, element)
        else:
            dictionary[key1] = converted_str
    except ValueError:
        dictionary[key1] = value1
    except SyntaxError:
        dictionary[key1] = value1
    return dictionary

def print_metadata(path):
    metadata = load_metadata_from_safetensors(path)
    print(metadata)
    metadata_dict = {}
    for key1, value1 in metadata.items():
        metadata_dict.update(dict_from_str(key1, value1))
    for key1, value1 in metadata_dict.items():
        if type(value1) is dict:
            for key2, value2 in value1.items():
                if type(value2) is dict:
                    for key3, value3 in value2.items():
                        parameters.log.info(f"{key1}: {key2}: {key3}: {value3}")
                else:
                    parameters.log.info(f"{key1}: {key2}: {value2}")
        else:
            parameters.log.info(f"{key1}: {value1}")

def print_metadata2(path):
    #from diffusers import AutoencoderKL
    parameters.log.info(f"Loading model: {path}")
    
    # pt stands for pickle tensor
    tensors = {}
    with safe_open(path, framework="pt", device="cpu") as f:
        for key in f.keys():
            tensors[key] = f.get_tensor(key)
            print(key) # keep this as print
    
    #vae = AutoencoderKL.from_pretrained(path, torch_dtype=torch.float32)
    #torch_model = vae
    #torch_model = torch.load(path)
    #state_dict = torch_model.state_dict()
    #for k, v in state_dict.items():
    #    print(k)

def save_file():
    #this is to save the code for saving safetensors, don't import it, keep for reference
    #vae.state_dict()
    
    #save_file(state_dict, os.path.join(filename))
    pass

if __name__ == "__main__":
    test_path = ""
    print_metadata(test_path)