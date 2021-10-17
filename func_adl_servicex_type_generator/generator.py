from pathlib import Path
import argparse

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

    collections, classes = load_yaml(args.yaml_type_file)

    package_name = "func_adl_servicex_xaodr21"

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
