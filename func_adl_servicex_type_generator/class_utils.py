from pathlib import Path
from typing import Tuple


def class_split_namespace(name: str) -> Tuple[str, str]:
    """Split a class into a namespace and a name.

    xAOD.Jets -> ('xAOD', 'Jets')

    Args:
        name (str): Fully qualified name

    Returns:
        Tuple[str, str]: The namespace and then the class
    """
    last_dot = name.rfind(".")
    if last_dot == -1:
        return "", name

    return name[:last_dot], name[last_dot + 1 :]


def class_ns_as_path(name: str) -> Path:
    """Split a namespace into a multi-directory level directory

    Args:
        name (str): The namespace

    Returns:
        Path: The path to the directory
    """
    return Path(name.replace(".", "/"))


def import_for_class(class_name: str, package_name: str) -> str:
    """Generate the import statement for a class

    Import statement is generated w.r.t. the root of the package,
    and is relative.

    Args:
        class_name (str): The fully qualified class name

    Returns:
        str: The import statement
    """
    ns, name = class_split_namespace(class_name)
    lst = [package_name]
    if len(ns) > 0:
        lst.append(ns)
    return f"from {'.'.join(lst)} import {name}"
