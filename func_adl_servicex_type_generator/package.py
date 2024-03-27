import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import jinja2

from func_adl_servicex_type_generator.class_utils import (
    class_ns_as_path,
    class_split_namespace,
    remove_ns_stem,
)
from func_adl_servicex_type_generator.data_model import (
    class_info,
    enum_info,
    file_info,
    method_arg_info,
    method_info,
)

from .class_utils import package_qualified_class


@jinja2.pass_context  # type: ignore
def subrender_filter(context, value):
    if value is None:
        return value

    _template = context.eval_ctx.environment.from_string(value)
    result = _template.render(**context)
    if context.eval_ctx.autoescape:
        result = jinja2.Markup(result)  # type: ignore
    return result


def prep_jinja2_env(env: jinja2.Environment):
    env.filters["subrender"] = subrender_filter


@dataclass
class config_info:
    "Config variables to be written out"
    name: str
    value: str


def template_package_scaffolding(
    data: Dict[str, Any], template_path: Path, output_path: Path, files: List[file_info]
):
    """Generate the package scaffolding:


    Args:
        data (Dict[str, Any]): Template replacement data needed for package
                               initialization
        template_path:         Location of our templates that we use to
                               generate the package
        output_path:           Location where we want to write the generated
                               package
        files:                 List of files to write out
    """
    # Load up the template structure and environment
    loader = jinja2.FileSystemLoader(str(template_path / "package"))
    env = jinja2.Environment(loader=loader)
    prep_jinja2_env(env)

    # Remove the package if it was there before
    if output_path.exists():
        shutil.rmtree(output_path)

    # Create the output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate import statements for the collection classes
    template_data = dict(data)

    # Fix up the sx_dataset
    if not isinstance(template_data["sx_dataset_name"], list):
        template_data["sx_dataset_name"] = [(template_data["sx_dataset_name"], "")]

    # Generate the package
    for t in loader.list_templates():
        template = env.get_template(t)
        output_file = output_path / t
        output_file.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Rendering {output_file}")
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

    # Write out all the files
    for f in files:
        output_file_path = dest_path / Path(f.file_name)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file_path, "w") as f_out:
            for line in f.contents:
                if line is not None:
                    f_out.write(line)
                f_out.write("\n")


@dataclass
class ns_info:
    """list of classes by namespace"""

    # Tne full name of the namespace
    ns_name: str

    # The relative path to where the files should be
    ns_path: Path


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


_g_cpp_to_py_type_map = {
    "float": "float",
    "int": "int",
    "unsigned int": "int",
    "short": "int",
    "unsigned short": "int",
    "unsigned long long": "int",
    "long long": "int",
    "long": "int",
    "double": "float",
    "bool": "bool",
}

_g_py_single_types = {i for _, i in _g_cpp_to_py_type_map.items()}


def clean_cpp_type(cpp_class_name: Optional[str]) -> Optional[str]:
    """Remove the prefixes and post-fixes from a C++ class name.

    Args:
        cpp_class_name (str): The C++ class name

    Returns:
        str: The cleaned C++ class name
    """
    if cpp_class_name is None:
        return None

    # Remove the prefixes and post-fixes
    cpp_class_name = cpp_class_name.strip()
    if cpp_class_name.startswith("const "):
        cpp_class_name = cpp_class_name[6:].strip()
    while cpp_class_name.endswith("*"):
        cpp_class_name = cpp_class_name[:-1].strip()

    return cpp_class_name


def count_pointer_depth(cpp_class_name: Optional[str]) -> int:
    """Count number of pointer levels in this declaration

    Args:
        cpp_class_name (Optional[str]): Class name to do counting on.
        If None, then return zero

    Returns:
        int: How many pointers
    """
    if cpp_class_name is None:
        return 0

    cpp_class_name = cpp_class_name.strip()
    count = 0
    while cpp_class_name.endswith("*"):
        cpp_class_name = cpp_class_name[:-1].strip()
        count += 1
    return count


def normalize_cpp_type(cpp_class_name: Optional[str]) -> Optional[str]:
    """Normalize a C++ type for lookup (remove
    extra spaces, etc.))

    Args:
        cpp_class_name (str): The C++ class name

    Returns:
        str: The normalized C++ class name
    """
    if cpp_class_name is None:
        return None

    result = cpp_class_name

    def replace_till_done(s: str, old: str, new: str) -> str:
        while True:
            n_result = s.replace(old, new)
            if n_result == s:
                break
            s = n_result
        return s

    result = replace_till_done(result, "  ", " ")
    result = replace_till_done(result, "> >", ">>")
    result = replace_till_done(result, "< <", "<<")

    return result


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
    cpp_class_name = clean_cpp_type(cpp_class_name)
    if cpp_class_name is None:
        raise RuntimeError("C++ class name is None")

    py_type = cpp_class_dict.get(cpp_class_name, None)
    if py_type is not None:
        return py_type.name

    py_type = _g_cpp_to_py_type_map.get(cpp_class_name, None)
    if py_type is not None:
        return py_type

    if len(cpp_class_name) == 1:
        return cpp_class_name

    # Last resort, it is an enum. We need to strip the last name off, see if we can do the lookup.
    # If so, check for the enum in the class.
    last_space = cpp_class_name.rfind("::")
    if last_space >= 0:
        enum_name = cpp_class_name[last_space + 2 :]  # noqa
        enum_ns = cpp_class_name[:last_space]
        py_type = cpp_class_dict.get(enum_ns, None)
        if py_type is not None:
            for e in py_type.enums:
                if e.name == enum_name:
                    return f"{py_type.name}.{e.name}"

    raise RuntimeError(f"Unknown C++ type {cpp_class_name}")


def write_out_classes(
    all_classes: Iterable[class_info],
    template_path: Path,
    project_src_path: Path,
    package_name: str,
    release_series: str,
    base_init_lines: List[str] = [],
    config_vars: Dict[str, str] = {},
):
    """Write out the templates for all classes

    This means correctly dealing with any namespace information here as well.

    Args:
        all_classes (Iterable[class_info]): List of classes to emit
        template_path (Path): Location of our templates
        project_src_path (Path): The root of the package source directory
            (top level __init__.py file location)
        project_name (str): Name of package for use in import statements
        release_series (str): Which release is this (22, or 21, etc.)
    """
    # Load up the template structure and environment
    loader = jinja2.FileSystemLoader(str(template_path / "files"))
    env = jinja2.Environment(loader=loader)
    prep_jinja2_env(env)

    class_template_file = env.get_template("object.py")
    init_template_file = env.get_template("__init__.py")

    all_classes_names = {c.name for c in all_classes}
    py_all_classes_dict = {c.name: c for c in all_classes}
    cpp_all_classes_dict = {c.cpp_name: c for c in all_classes}

    # We need to do two passes. This is because the __init__ template. First pass
    # we write out the classes and accumulate information, and the second pass we just
    # write the __init__ files.

    class_load_info: Dict[Path, Tuple[str, List[str]]] = {}
    sub_module_load_info: Dict[Path, Set[str]] = {}

    for c in all_classes:
        # We do not write out aliases...
        if c.is_alias:
            continue

        # Make sure the directory is present and ready for us to write to
        c_ns, c_name = class_split_namespace(c.name)
        class_file = project_src_path / class_ns_as_path(c_ns) / f"{c_name.lower()}.py"
        class_file.parent.mkdir(parents=True, exist_ok=True)

        # Gather info for the __init__ file: classes and sub-modules
        if class_file.parent not in class_load_info:
            ns = "" if c_ns == "" else f".{c_ns}"
            class_load_info[class_file.parent] = (ns, [])
        class_load_info[class_file.parent][1].append(c_name.lower())

        dir_path = class_file.parent
        ns_name = ""
        while dir_path != project_src_path.parent:
            if dir_path not in sub_module_load_info:
                sub_module_load_info[dir_path] = set()
            if ns_name != "":
                sub_module_load_info[dir_path].add(ns_name)
            ns_name = dir_path.name
            dir_path = dir_path.parent

        # Get the imports we need at the top of the file
        import_statements = []
        if c.python_container_type is not None:
            import_statements.append("from typing import Iterable")

        # Add all the objects this needs to inherit from
        inheritance_list: List[str] = []
        if c.python_container_type is not None:
            if (c.python_container_type in all_classes_names) or (
                c.python_container_type in _g_py_single_types
            ):
                inheritance_list.append(
                    f"Iterable[{package_qualified_class(c.python_container_type, package_name, all_classes_names)}]"  # NOQA
                )

        # Methods from this class
        def generate_methods(methods: List[method_info], deref_count: int = 0):
            r = [
                {
                    "fully_qualified_name": normalize_cpp_type(c.cpp_name),
                    "name": m.name,
                    "cpp_return_type": normalize_cpp_type(m.return_type),
                    "return_type": package_qualified_class(
                        py_type_from_cpp(m.return_type, cpp_all_classes_dict),
                        package_name,
                        all_classes_names,
                    ),
                    "return_type_element": normalize_cpp_type(
                        cpp_collection_element(
                            py_type_from_cpp(m.return_type, cpp_all_classes_dict),
                            py_all_classes_dict,
                        )
                    ),
                    "arguments": [
                        {
                            "arg_type": package_qualified_class(
                                a.arg_type, package_name, all_classes_names
                            ),
                            "name": a.name,
                        }
                        for a in m.arguments
                    ],
                    "param_call_args": m.param_arguments,
                    "param_helper_class": m.param_helper,
                    "param_type_cb": m.param_type_cb,
                }
                for m in methods
            ]

            if deref_count > 0:
                for m in r:
                    m["deref_count"] = deref_count

            return r

        def lookup_enum(
            arg: method_arg_info, all_classes: Iterable[class_info]
        ) -> Optional[enum_info]:
            """Return the enum info for the argument if it is an enum.

            Args:
                arg (method_info): The argument to check
                all_classes (Iterable[class_info]): All classes to look through

            Returns:
                Optional[enum_info]: The enum info if this is an enum, or None
            """
            cpp_type = clean_cpp_type(arg.arg_type)
            if cpp_type is None:
                return None
            cpp_type_info = cpp_type.rsplit(".", 2)

            for c in all_classes:
                for e in c.enums:
                    if e.name == cpp_type_info[1] and cpp_type_info[0] == c.cpp_name:
                        return e

            return None

        def generate_enums(
            method_list: List[method_info], all_classes: Iterable[class_info]
        ) -> Dict[str, List[enum_info]]:
            """Return a list of the referenced enum definitions for this call.

            Args:
                method_list (List[method_info]): List of the methods that we need to look at
                all_classes (List[class_info]): List of all classes (and thus enums in them)

            Raises:
                RuntimeError: _description_

            Returns:
                Dict[str, Dict[str, Any]]: List, by method name, of all enums referenced.
            """
            result: Dict[str, List[enum_info]] = {
                m.name: [
                    e_info
                    for arg in m.arguments
                    if (e_info := lookup_enum(arg, all_classes)) is not None
                ]
                for m in method_list
                if m.return_type is not None
            }
            return result

        methods = generate_methods(c.methods)
        referenced_enums = generate_enums(c.methods, all_classes)

        # Methods from behavior as classes
        for b in c.behaviors:
            name = clean_cpp_type(b)
            assert name is not None
            if name not in cpp_all_classes_dict:
                raise RuntimeError(f"Unknown behavior class {name} for class {c.name}")
            methods += generate_methods(
                cpp_all_classes_dict[name].methods, count_pointer_depth(b)
            )

        # Write out the object file
        text = class_template_file.render(
            class_name=c_name,
            methods=c.methods,
            include_file=c.include_file,
            import_statements=import_statements,
            class_split_namespace=class_split_namespace,
            remove_ns_stem=remove_ns_stem,
            ns_stem=f"{package_name}.{c_name.lower()}",
            inheritance_list=inheritance_list,
            methods_info=methods,
            package_name=package_name,
            enums_info=c.enums,
            referenced_enums=referenced_enums,
        )

        with class_file.open("wt") as out:
            for line in text.splitlines():
                out.write(line)
                out.write("\n")

    # Write out the __init__ files
    init_paths = set(class_load_info.keys()) | set(sub_module_load_info.keys())
    for p in init_paths:
        c_imports = []
        m_stub = ""
        if p in class_load_info:
            m_stub, c_imports = class_load_info[p]

        sub_ns = []
        if p in sub_module_load_info:
            sub_ns = sub_module_load_info[p]

        with (p / "__init__.py").open("wt") as out:
            out.write(
                init_template_file.render(
                    class_imports=c_imports,
                    module_stub=m_stub,
                    sub_namespaces=sub_ns,
                    package_name=package_name,
                    sx_dataset_name=f"SXDSAtlasxAODR{release_series}",
                    base_init_lines=base_init_lines,
                    base_variables=[config_info(k, v) for k, v in config_vars.items()],
                )
            )
            # out.write("\n")  # Get around whitespace trimming
