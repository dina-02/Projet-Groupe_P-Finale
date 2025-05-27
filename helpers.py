import json
import os.path

import toml
import yaml
import numpy as np
import os
from typing import Dict, Literal

import pandas as pd



def get_serialized_data(path: str) -> Dict:
    """
    Reads and deserializes data from a file based on its extension. Supported formats are YAML, JSON, and TOML.

    This function opens the file at the specified path, identifies its extension, and deserializes its content
    into a Python dictionary or list (depending on the format). The following file extensions are supported:
    - `.yaml` or `.yml` (YAML format)
    - `.json` (JSON format)
    - `.toml` (TOML format)

    If the file extension is unsupported, a `ValueError` is raised.

    :param path: The file path of the serialized data to be loaded.
                  This must be a valid path to a file with a supported extension (.yaml, .json, or .toml).
    :return: A Python dictionary or list containing the deserialized data.
             The return type depends on the content of the file (e.g., a dictionary for JSON and TOML, a list or dictionary for YAML).
    :raises ValueError: If the file extension is not supported or the file cannot be opened.
    """
    _, extension = os.path.splitext(path)

    with open(path, mode="r", encoding="utf-8") as file:
        if extension == ".yaml":
            return yaml.safe_load(file)
        elif extension == ".json":
            return json.load(file)
        elif extension == ".toml":
            return toml.load(file)

        raise ValueError(f"Unsupported file extension {extension} | file={path}")

