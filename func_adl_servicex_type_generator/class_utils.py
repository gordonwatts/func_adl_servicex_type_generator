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

    return name[:last_dot], name[last_dot + 1 :]  # noqa: E203


def remove_ns_stem(stem: str, name: str) -> str:
    """Remove the namespace from the name.

    Assumes this is a python namespace/object name.

    Args:
        stem (str): The namespace
        name (str): The fully qualified name

    Returns:
        str: The name without the namespace
    """
    if name.startswith(stem + "."):
        return name[len(stem) + 1 :]
    return name


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


def package_qualified_class(
    class_name: Optional[str], package_name: str, all_classes: Set[str]
) -> Optional[str]:
    """Return a package name qualified class, as long as the class is one
    of the classes we are processing in this package.

    xAOD.Jet -> package_name.xAOD.jet.Jet
    float -> float
    Iterable[xAOD.Jet] -> Iterable[package_name.xAOD.Jet]
    None -> None
    xAOD.Jet.Enum -> package_name.xAOD.jet.Jet.Enum

    Args:
        class_name (str): Name of class we should return
        package_name (str): Name of the python package
        all_classes (List[str]): List of all class names in package

    Returns:
        str: The qualified class name
    """

    def _remove_namespace(name: str) -> str:
        is_in_classes = name in all_classes
        is_enum_in_classes = name.rsplit(".", 1)[0] in all_classes
        if is_in_classes:
            name_parts = name.split(".")
            new_name_parts = name_parts[:-1] + [name_parts[-1].lower(), name_parts[-1]]
            return f"{package_name}.{'.'.join(new_name_parts)}"
        if is_enum_in_classes:
            name_parts = name.split(".")
            new_name_parts = name_parts[:-2] + [
                name_parts[-2].lower(),
                name_parts[-2],
                name_parts[-1],
            ]
            return f"{package_name}.{'.'.join(new_name_parts)}"
        if name == "Iterable":
            return f"{package_name}.FADLStream"
        return name

    if class_name is None:
        return None

    return process_by_namespace(class_name, _remove_namespace)


def split_release(release: str) -> Tuple[int, int, int]:
    """Returns a string release split into integer numbers

    Args:
        release (str): The release name, like 22.2.147

    Returns:
        Tuple[int, int, int]: Returns a tuple, like (22, 2, 147).
    """
    numbers = release.split(".")
    return (int(numbers[0]), int(numbers[1]), int(numbers[2]))
