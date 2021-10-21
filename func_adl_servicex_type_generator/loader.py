from pathlib import Path
from typing import List, Tuple

import yaml

from func_adl_servicex_type_generator.class_utils import class_split_namespace
from func_adl_servicex_type_generator.data_model import (
    class_info,
    collection_info,
    method_arg_info,
    method_info,
)


def method_loader(methods: List[dict]) -> List[method_info]:
    """Return the list of methods from the input

    Args:
        methods (List[dict]): List of found methods

    Returns:
        List[method_info]: List of methods in our data class format
    """
    result = []
    for d in methods:
        result.append(
            method_info(
                name=d["name"],
                return_type=d["return_type"],
                arguments=[
                    method_arg_info(a["name"], None, a["type"]) for a in d["arguments"]
                ]
                if "arguments" in d
                else [],
            )
        )

    return result


def load_yaml(config_path: Path) -> Tuple[List[collection_info], List[class_info]]:
    """Return data from a loaded info file

    Args:
        config_path (Path): The path to the file we are using

    Returns:
        Tuple[List[collection_info], List[class_info]]]: [description]
    """
    data = yaml.safe_load(config_path.read_text())

    data_collections = data["collections"]
    data_classes = data["classes"]

    collections = [
        collection_info(
            name=c["collection_name"],
            collection_type=c["python_container_type"],
            collection_item_type=c["python_item_type"],
            collection_item_type_name=class_split_namespace(c["python_item_type"])[1],
            cpp_item_type=c["cpp_item_type"],
            cpp_collection_type=c["cpp_container_type"],
            cpp_include_file=[c["include_file"]]
            if ("include_file" in c) and (len(c["include_file"]) > 0)
            else [],
        )
        for c in data_collections
    ]

    classes = [
        class_info(name=c["python_name"], methods=method_loader(c["methods"]))
        for c in data_classes
    ]

    return (collections, classes)
