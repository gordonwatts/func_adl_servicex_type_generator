from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set
from .class_utils import package_qualified_class

import shutil

import jinja2
from func_adl_servicex_type_generator.class_utils import (
    class_ns_as_path,
    class_split_namespace,
    import_for_class,
)

from func_adl_servicex_type_generator.data_model import class_info, method_info


def template_package_scaffolding(
    data: Dict[str, Any], template_path: Path, output_path: Path
):
    """Generate the package scaffolding:


    Args:
        data (Dict[str, Any]): Template replacement data needed for package
                               initialization
        template_path:         Location of our templates that we use to
                               generate the package
        output_path:           Location where we want to write the generated
                               package
    """
    # Load up the template structure and environment
    loader = jinja2.FileSystemLoader(str(template_path / "package"))
    env = jinja2.Environment(loader=loader)

    # Remove the package if it was there before
    if output_path.exists():
        shutil.rmtree(output_path)

    # Create the output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate import statements for the collection classes
    template_data = dict(data)

    # Generate the package
    for t in loader.list_templates():
        template = env.get_template(t)
        output_file = output_path / t
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("wt") as out:
            for line in template.render(template_data).splitlines():
                out.write(line)
                out.write("\n")

    # We rename the src directory to be the package name now
    assert (output_path / "src").exists()
    dest_path = output_path / template_data["package_name"]
    if not dest_path.exists():
        (output_path / "src").rename(dest_path)
    else:
        for f in (output_path / "src").iterdir():
            dest = dest_path / f.name
            if dest.exists():
                dest.unlink()
            f.rename(dest)


@dataclass
class ns_info:
    """list of classes by namespace"""

    # Tne full name of the namespace
    ns_name: str

    # The relative path to where the files should be
    ns_path: Path


def import_for_good_class(type_name: str, package_name: str, all_classes: Set[str]):
    """Return an import statement for a class as long as it is a class we known about

    Args:
        type_name (str): The type to get the import statement for
        package_name (str): The name of the package to generate the import for
        all_classes (Set[str]): All good classes
    """
    if type_name not in all_classes:
        return []

    return [import_for_class(type_name, package_name)]


def imports_for_method(
    method: method_info,
    parent_class_name: str,
    package_name: str,
    all_class_names: Set[str],
) -> List[str]:
    """Generate a list of imports for all the special types needed.

    If this method references the method being defined, do not create
    an import statement.

    Args:
        method (method_info): The method
        parent_class_name (str): The name of the class that contains this method
        package_name (str): The name of the package (for use in import statement)
        all_class_names (Set[str]): All known classes
    """
    # Do the return type
    result = (
        import_for_good_class(method.return_type, package_name, all_class_names)
        if (method.return_type is not None)
        and (method.return_type != parent_class_name)
        else []
    )

    # Next, do the arguments
    for a in method.arguments:
        result += import_for_good_class(a.arg_type, package_name, all_class_names)

    return result


def cpp_collection_element(
    py_class_name: Optional[str], class_dict: Dict[str, class_info]
) -> Optional[str]:
    """If this class is a collection, return the element name, as a C++ class name.

    Args:
        py_class_name (Optional[str]): The python class name to look up
        class_dict (Dict[str, class_info]): All classes where we can do a
            careful looking

    Returns:
        Optional[str]: The element class name if this is a collection, or None.
    """
    if py_class_name is None:
        return None

    c = class_dict.get(py_class_name, None)
    if c is None:
        return None

    return c.cpp_container_type


def cpp_return_type(
    py_class_name: Optional[str], class_dict: Dict[str, class_info]
) -> Optional[str]:
    if py_class_name is None:
        return None

    c = class_dict.get(py_class_name, None)
    if c is None:
        return py_class_name

    return c.cpp_name


_g_cpp_to_py_type_map = {
    "float": "float",
    "int": "int",
    "unsigned int": "int",
    "unsigned long long": "int",
    "long long": "int",
    "long": "int",
    "size_t": "int",
    "double": "float",
    "bool": "bool",
}


def py_type_from_cpp(
    cpp_class_name: Optional[str], cpp_class_dict: Dict[str, class_info]
) -> str:
    """Return the Python equivalent type for a C++ class type.

    Will raise an exception if it can't find the mapping.

    Args:
        cpp_class_name (str): The C++ class name
        cpp_class_dict (Dict[str, class_info]): Dict of all classes, indexed by C++ name

    Returns:
        str: The python class name
    """
    if cpp_class_name is None:
        raise RuntimeError("C++ class name is None")

    # Remove the prefixes and post-fixes
    if cpp_class_name.startswith("const "):
        cpp_class_name = cpp_class_name[6:]
    if cpp_class_name.endswith("*"):
        cpp_class_name = cpp_class_name[:-1]

    py_type = cpp_class_dict.get(cpp_class_name, None)
    if py_type is not None:
        return py_type.name

    py_type = _g_cpp_to_py_type_map.get(cpp_class_name, None)
    if py_type is not None:
        return py_type

    raise RuntimeError(f"Unknown C++ type {cpp_class_name}")


def write_out_classes(
    all_classes: Iterable[class_info],
    template_path: Path,
    project_src_path: Path,
    package_name: str,
):
    """Write out the templates for all classes

    This means correctly dealing with any namespace information here as well.

    Args:
        all_classes (Iterable[class_info]): List of classes to emit
        template_path (Path): Location of our templates
        project_src_path (Path): The root of the package source directory
            (top level __init__.py file location)
        project_name (str): Name of package for use in import statements
    """
    # Load up the template structure and environment
    loader = jinja2.FileSystemLoader(str(template_path / "files"))
    env = jinja2.Environment(loader=loader)
    class_template_file = env.get_template("object.py")
    init_template_file = env.get_template("__init__.py")

    all_classes_names = {c.name for c in all_classes}
    py_all_classes_dict = {c.name: c for c in all_classes}
    cpp_all_classes_dict = {c.cpp_name: c for c in all_classes}

    for c in all_classes:
        # Make sure the directory is present and ready for us to write to
        c_ns, c_name = class_split_namespace(c.name)
        class_file = project_src_path / class_ns_as_path(c_ns) / f"{c_name.lower()}.py"
        class_file.parent.mkdir(parents=True, exist_ok=True)

        dir_path = class_file.parent
        ns_name = ""
        while dir_path != project_src_path.parent:
            init_path = dir_path / "__init__.py"
            if not init_path.exists():
                with init_path.open("wt") as out:
                    out.write(init_template_file.render())
                    out.write("\n")  # Get around whitespace trimming
            if ns_name != "":
                import_line = f"from . import {ns_name}"
                init_text = init_path.read_text()
                if import_line not in init_text:
                    with init_path.open("a") as out:
                        out.write(import_line)
                        out.write("\n")
            ns_name = dir_path.name
            dir_path = dir_path.parent

        with (class_file.parent / "__init__.py").open("at") as out_to:
            out_to.write(
                f"{c_name.lower()} = _load_me('{package_name}.{c_ns}.{c_name.lower()}')\n"
            )
        # jet_v1 = _load_me('func_adl_servicex_xaodr21.xAOD.jet_v1')

        # Get the imports we need at the top of the file
        import_statements = []
        if c.python_container_type is not None:
            import_statements.append("from typing import Iterable")

        # Add all the objects this needs to inherit from
        inheritance_list: List[str] = []
        if c.python_container_type is not None:
            if c.python_container_type in all_classes_names:
                inheritance_list.append(
                    f"Iterable[{package_qualified_class(c.python_container_type, package_name, all_classes_names)}]"
                )

        # Methods
        methods = [
            {
                "fully_qualified_name": f"{c.cpp_name}",
                "name": m.name,
                "cpp_return_type": m.return_type,
                "return_type": package_qualified_class(
                    py_type_from_cpp(m.return_type, cpp_all_classes_dict),
                    package_name,
                    all_classes_names,
                ),
                "is_pointer": "True" if m.return_is_pointer else "False",
                "return_type_element": cpp_collection_element(
                    m.return_type, py_all_classes_dict
                ),
                "arguments": m.arguments,
            }
            for m in c.methods
        ]

        # Write out the object file
        text = class_template_file.render(
            class_name=c_name,
            methods=c.methods,
            include_file=c.include_file,
            import_statements=import_statements,
            class_split_namespace=class_split_namespace,
            inheritance_list=inheritance_list,
            methods_info=methods,
            package_name=package_name,
        )

        with class_file.open("wt") as out:
            for line in text.splitlines():
                out.write(line)
                out.write("\n")
