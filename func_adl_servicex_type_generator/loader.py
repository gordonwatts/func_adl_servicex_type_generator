from pathlib import Path
from typing import List, Tuple
import yaml

from func_adl_servicex_type_generator.data_model import class_info, collection_info


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
        )
        for c in data_collections
    ]

    classes = [class_info(name=c["python_name"]) for c in data_classes]

    return (collections, classes)
