import json, magic 

def validate_file_type_and_mime(file_object: bytes, file_name: str):
    valid_file = False
    with open("config/miscellaneous/FileTypesDict.json", "r") as f:
        config_dict = json.load(f)

    if ((file_name in config_dict["supported_file_types"]) and ()):
        valid_file = True

    return valid_file
