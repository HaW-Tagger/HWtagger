import os, torch, json, ast
from safetensors.torch import load_file, save_file, safe_open

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

if __name__ == "__main__":
    test_path = ""
    metadata = load_metadata_from_safetensors(test_path)
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