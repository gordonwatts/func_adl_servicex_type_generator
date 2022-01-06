from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from func_adl_servicex_type_generator.class_utils import class_split_namespace
from func_adl_servicex_type_generator.data_model import (
    class_info,
    collection_info,
    extra_parameter,
    metadata_info,
    method_arg_info,
    method_info,
    parameter_action,
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


def load_parameters(params: List[Dict[str, Any]]) -> List[extra_parameter]:
    "Load extra parameters from the file yaml"
    return [
        extra_parameter(
            name=p["name"],
            type=p["type"],
            default_value=p["default_value"],
            actions=[
                parameter_action(
                    value=a["value"],
                    md_names=a["metadata_names"],
                )
                for a in p["actions"]
            ],
        )
        for p in params
    ]


def load_yaml(
    config_path: Path,
) -> Tuple[List[collection_info], List[class_info], Dict[str, metadata_info]]:
    """Return data from a loaded info file

    Args:
        config_path (Path): The path to the file we are using

    Returns:
        Tuple[List[collection_info], List[class_info]]]: [description]
    """
    data = yaml.safe_load(config_path.read_text())

    data_collections = data["collections"]
    data_classes = data["classes"]
    data_metadata = data["metadata"]

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
            link_libraries=c["link_libraries"],
            parameters=[]
            if "extra_parameters" not in c
            else load_parameters(c["extra_parameters"]),
        )
        for c in data_collections
    ]

    classes = [
        class_info(
            name=c["python_name"],
            cpp_name=c["cpp_name"],
            methods=method_loader(c["methods"]),
            python_container_type=None
            if "is_container_of_python" not in c
            else c["is_container_of_python"],
            cpp_container_type=None
            if "is_container_of_cpp" not in c
            else c["is_container_of_cpp"],
            include_file=c["include_file"] if "include_file" in c else "",
            is_alias=("is_alias" in c) and (c["is_alias"] == "True"),
            behaviors=c["also_behaves_like"] if "also_behaves_like" in c else [],
        )
        for c in data_classes
    ]

    metadata = {m["name"]: metadata_info(data=m["data"]) for m in data_metadata}

    return (collections, classes, metadata)
