import argparse
import itertools
from pathlib import Path
from typing import Optional

from func_adl_servicex_type_generator.class_utils import (
    package_qualified_class,
    split_release,
)
from func_adl_servicex_type_generator.loader import load_yaml
from func_adl_servicex_type_generator.package import (
    template_package_scaffolding,
    write_out_classes,
)


def run():
    parser = argparse.ArgumentParser(description="Generate python package")
    parser.add_argument(
        "yaml_type_file",
        type=Path,
        help="The yaml file that contains the type info",
    )
    parser.add_argument(
        "--version",
        type=str,
        help="The version of the package to generate (1.1.0b2 or 1.1.0, etc.)",
    )
    parser.add_argument(
        "--output_directory",
        type=Path,
        help="The output directory for the generated python package",
        default=Path("../func_adl_servicex_xaodrXX"),
    )
    args = parser.parse_args()

    generate_package(args.yaml_type_file, args.version, args.output_directory)
    return 0


def generate_package(
    yaml_type_file: Path, version: str, output_directory: Optional[Path]
):
    # Load in the base data
    data = load_yaml(yaml_type_file)

    # Extract release info
    release_name = data.config["atlas_release"]
    release_tuple = split_release(release_name)
    package_name = f"func_adl_servicex_xaodr{release_tuple[0]}"

    # Extract the version info. Look for any non alphabet characters and split
    # the version string by that.
    assert version is not None
    if version[0] == "v":
        version = version[1:]
    if "b" in version:
        version_base, pre_version = version.split("b")
        pre_version = "b" + pre_version
    elif "a" in version:
        version_base, pre_version = version.split("a")
        pre_version = "a" + pre_version
    else:
        version_base = version
        pre_version = ""

    # Try to get a package name
    release_series = release_tuple[0]
    package_name = f"func_adl_servicex_xaodr{release_series}"

    output_directory = (
        output_directory if output_directory is not None else Path(f"../{package_name}")
    )

    # Fix up the collection types
    all_class_names = {c.name for c in data.classes}
    for c in data.collections:
        new_c = package_qualified_class(
            c.collection_type, package_name, all_class_names
        )
        assert new_c is not None
        c.collection_type = new_c

    template_data = {
        "package_name": package_name,
        "package_version": f"{version_base}.{release_name}{pre_version}",
        "package_info_description": f"xAOD R{release_tuple[0]} {data.config['atlas_release']}",  # noqa
        "calibration_types": [""] + list(data.config["dataset_types"]),
        "backend_default_name": f"atlasr{release_tuple[0]}",
        "collections": data.collections,
        "metadata": data.metadata,
        "release_series": release_series,
    }

    template_path = Path(__file__).parent / ".." / "template"
    assert template_path.exists()
    output_path = output_directory

    template_package_scaffolding(template_data, template_path, output_path, data.files)

    base_init_lines = list(itertools.chain(*[f.init_lines for f in data.files]))

    write_out_classes(
        data.classes,
        template_path,
        output_path / template_data["package_name"],
        package_name,
        [""] + list(data.config["dataset_types"]),
        "release_series",
        base_init_lines=base_init_lines,
        config_vars=data.config,
    )
