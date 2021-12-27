from pathlib import Path
import argparse
from func_adl_servicex_type_generator.class_utils import package_qualified_class

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
    args = parser.parse_args()

    package_name = "func_adl_servicex_xaodr21"

    collections, classes = load_yaml(args.yaml_type_file)

    # Fix up the collection types
    all_class_names = {c.name for c in classes}
    for c in collections:
        new_c = package_qualified_class(
            c.collection_type, package_name, all_class_names
        )
        assert new_c is not None
        c.collection_type = new_c

    data = {
        "package_name": package_name,
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "sx_dataset_name": "SXDSAtlasxAODR21",
        "backend_default_name": "xaod_r21",
        "collections": collections,
    }

    template_path = Path("./template")
    assert template_path.exists()
    output_path = Path(f"../{data['package_name']}")

    template_package_scaffolding(data, template_path, output_path)

    write_out_classes(
        classes, template_path, output_path / data["package_name"], package_name
    )
