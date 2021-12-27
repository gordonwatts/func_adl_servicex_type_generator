from pathlib import Path
from typing import Callable, Optional, Set, Tuple


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


def process_by_namespace(name: str, transform: Callable[[str], str]) -> str:
    """Strip off and rebuild a python namespace, calling
    the transform function on each item.

    Jet -> transform(Jet)
    MyClass[Jet] -> transform(MyClass)[transform(Jet)]

    Args:
        name (str): Name to start with

    Returns:
        str: transformed name, reassembled
    """
    typename = ""
    depth_level = 0
    argument = ""
    index = 0
    transformed = False
    while index < len(name):
        if depth_level > 0:
            if name[index] == "]":
                depth_level -= 1
                if depth_level == 0:
                    typename += (
                        "["
                        + ", ".join(
                            [
                                process_by_namespace(a.strip(), transform)
                                for a in argument.split(",")
                            ]
                        )
                        + "]"
                    )
                else:
                    argument += name[index]
            elif name[index] == "[":
                depth_level += 1
                argument += name[index]
            else:
                argument += name[index]
            index += 1
        else:
            if name[index] == "[":
                typename = transform(typename)
                transformed = True
                depth_level += 1
                index += 1
            else:
                typename += name[index]
                index += 1

    if not transformed:
        typename = transform(typename)

    return typename


def remove_namespaces(name: str) -> str:
    """Remove the namespaces from a fully qualified name

    Args:
        name (str): The fully qualified name

    'xAOD.Jet' -> 'Jet'
    'Iterable[xAOD.Jet]' -> 'Iterable[Jet]'
    'float' -> 'float'

    Returns:
        str: The name without the namespaces
    """
    return process_by_namespace(name, lambda x: class_split_namespace(x)[1])


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


def package_qualified_class(
    class_name: Optional[str], package_name: str, all_classes: Set[str]
) -> Optional[str]:
    """Return a package name qualified class, as long as the class is one
    of the classes we are processing in this package.

    xAOD.Jet -> package_name.xAOD.Jet
    float -> float
    Iterable[xAOD.Jet] -> Iterable[package_name.xAOD.Jet]
    None -> None

    Args:
        class_name (str): Name of class we should return
        package_name (str): Name of the python package
        all_classes (List[str]): List of all class names in package

    Returns:
        str: The qualified class name
    """

    def _remove_namespace(name: str) -> str:
        if name in all_classes:
            name_parts = name.split(".")
            name_parts.append(name_parts[-1])
            name_parts[-2] = name_parts[-2].lower()
            return f"{package_name}.{'.'.join(name_parts)}"
        return name

    if class_name is None:
        return None

    return process_by_namespace(class_name, _remove_namespace)
