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


def remove_namespaces(name: str) -> str:
    """Remove the namespaces from a fully qualified name

    Args:
        name (str): The fully qualified name

    Returns:
        str: The name without the namespaces
    """
    typename = ""
    depth_level = 0
    argument = ""
    index = 0
    split_typename = False
    while index < len(name):
        if depth_level > 0:
            if name[index] == "]":
                depth_level -= 1
                if depth_level == 0:
                    typename += (
                        "["
                        + ", ".join(
                            [remove_namespaces(a.strip()) for a in argument.split(",")]
                        )
                        + "]"
                    )
            else:
                argument += name[index]
            index += 1
        else:
            if name[index] == "[":
                _, typename = class_split_namespace(typename)
                split_typename = True
                depth_level += 1
                index += 1
            else:
                typename += name[index]
                index += 1

    if not split_typename:
        _, typename = class_split_namespace(typename)

    return typename


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
    lst.append(name.lower())
    return f"from {'.'.join(lst)} import {name}"
