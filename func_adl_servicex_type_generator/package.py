from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

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

    # Create the output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate import statements for the collection classes
    collection_imports = [
        import_for_class(c.collection_item_type, data["package_name"])
        for c in data["collections"]
    ]
    template_data = dict(data)
    template_data["import_statements"] = collection_imports

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
    method: method_info, package_name: str, all_class_names: Set[str]
) -> List[str]:
    """Generate a list of imports for all the special types needed

    Args:
        method (method_info): The method
        package_name (str): The name of the package (for use in import statement)
    """
    # Do the return type
    result = (
        import_for_good_class(method.return_type, package_name, all_class_names)
        if method.return_type is not None
        else []
    )

    # Next, do the arguments
    for a in method.arguments:
        result += import_for_good_class(a.arg_type, package_name, all_class_names)

    return result


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

    all_classes_names = {c.name for c in all_classes}

    for c in all_classes:
        # Make sure the directory is present and ready for us to write to
        c_ns, c_name = class_split_namespace(c.name)
        class_file = project_src_path / class_ns_as_path(c_ns) / f"{c_name.lower()}.py"
        class_file.parent.mkdir(parents=True, exist_ok=True)

        dir_path = class_file.parent
        while (not (dir_path / "__init__.py").exists()) and (
            dir_path != project_src_path.parent
        ):
            (dir_path / "__init__.py").touch()
            dir_path = dir_path.parent

        # Get the imports we need at the top of the file
        import_statements = [
            line
            for m in c.methods
            for line in imports_for_method(m, package_name, all_classes_names)
        ]

        # Write out the object file
        text = class_template_file.render(
            class_name=c_name,
            methods=c.methods,
            import_statements=import_statements,
            class_split_namespace=class_split_namespace,
        )

        with class_file.open("wt") as out:
            for line in text.splitlines():
                out.write(line)
                out.write("\n")

        # Make sure the object is exported in the init file
        # TODO: Make this work again - right now taken out because it introduces
        # circular dependencies.
        # with (class_file.parent / "__init__.py").open("at") as out:
        #     out.write(f"from .{c_name.lower()} import {c_name}\n")
