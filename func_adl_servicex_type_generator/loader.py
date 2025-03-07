from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

from func_adl_servicex_type_generator.class_utils import class_split_namespace
from func_adl_servicex_type_generator.data_model import (
    class_info,
    collection_info,
    enum_info,
    enum_value_info,
    extra_parameter,
    file_info,
    metadata_info,
    method_arg_info,
    method_info,
    normal_parameter,
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
                arguments=(
                    [
                        method_arg_info(a["name"], None, a["type"])
                        for a in d["arguments"]
                    ]
                    if "arguments" in d
                    else []
                ),
                param_arguments=(
                    [
                        method_arg_info(a["name"], None, a["type"])
                        for a in d["parameter_arguments"]
                    ]
                    if "parameter_arguments" in d
                    else []
                ),
                param_helper=d["param_helper"] if "param_helper" in d else None,
                param_type_cb=(
                    d["param_type_callback"] if "param_type_callback" in d else None
                ),
            )
        )

    return result


def load_parameters(params: List[Dict[str, Any]]) -> List[normal_parameter]:
    "Load extra parameters from the file yaml"
    return [
        normal_parameter(
            name=p["name"],
            type=p["type"],
            default_value=p["default_value"] if "default_value" in p else None,
        )
        for p in params
    ]


def enum_loader(enums: List[Dict[str, Any]]) -> List[enum_info]:
    "Load extra parameters from the file yaml"
    return [
        enum_info(
            name=e["name"],
            values=[
                enum_value_info(name=v["name"], value=v["value"]) for v in e["values"]
            ],
        )
        for e in enums
    ]


def load_parameters_extra(params: List[Dict[str, Any]]) -> List[extra_parameter]:
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
                    bank_rename=a["bank_rename"],
                )
                for a in p["actions"]
            ],
        )
        for p in params
    ]


@dataclass
class LoadedData:
    "Data loaded from the yaml file"

    # List of collections
    collections: List[collection_info]

    # List of classes
    classes: List[class_info]

    # Metadata Info
    metadata: Dict[str, metadata_info]

    # Files we read back
    files: List[file_info]

    # Config
    config: Dict[str, str]


def load_yaml(
    config_path: Path,
) -> LoadedData:
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
    data_files = data["files"]

    collections = [
        collection_info(
            name=c["collection_name"],
            collection_type=c["python_container_type"],
            collection_item_type=c["python_item_type"],
            collection_item_type_name=class_split_namespace(c["python_item_type"])[1],
            cpp_item_type=c["cpp_item_type"],
            cpp_collection_type=c["cpp_container_type"],
            cpp_include_file=(
                [c["include_file"]]
                if ("include_file" in c) and (len(c["include_file"]) > 0)
                else []
            ),
            link_libraries=c["link_libraries"],
            parameters=(
                [] if "parameters" not in c else load_parameters(c["parameters"])
            ),
            extra_parameters=(
                []
                if "extra_parameters" not in c
                else load_parameters_extra(c["extra_parameters"])
            ),
            method_callback=c["method_callback"] if "method_callback" in c else "",
        )
        for c in data_collections
    ]

    classes = [
        class_info(
            name=c["python_name"],
            cpp_name=c["cpp_name"],
            methods=method_loader(c["methods"]) if "methods" in c else [],
            python_container_type=(
                None
                if "is_container_of_python" not in c
                else c["is_container_of_python"]
            ),
            cpp_container_type=(
                None if "is_container_of_cpp" not in c else c["is_container_of_cpp"]
            ),
            include_file=c["include_file"] if "include_file" in c else "",
            is_alias=("is_alias" in c) and (c["is_alias"] == "True"),
            behaviors=c["also_behaves_like"] if "also_behaves_like" in c else [],
            enums=enum_loader(c["enums"]) if "enums" in c else [],
            library=c["library"] if "library" in c else None,
        )
        for c in data_classes
    ]

    metadata = {m["name"]: metadata_info(data=m["data"]) for m in data_metadata}

    files = [
        file_info(
            file_name=f["name"], init_lines=f["init_lines"], contents=f["contents"]
        )
        for f in data_files
    ]

    config = data["config"]

    return LoadedData(collections, classes, metadata, files, config)
