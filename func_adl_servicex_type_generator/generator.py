import itertools
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

    data = load_yaml(args.yaml_type_file)

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
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "sx_dataset_name": "SXDSAtlasxAODR21",
        "backend_default_name": "xaod_r21",
        "collections": data.collections,
        "metadata": data.metadata,
    }

    template_path = Path("./template")
    assert template_path.exists()
    output_path = Path(f"../{template_data['package_name']}")

    template_package_scaffolding(template_data, template_path, output_path, data.files)

    base_init_lines = list(itertools.chain(*[f.init_lines for f in data.files]))

    write_out_classes(
        data.classes,
        template_path,
        output_path / template_data["package_name"],
        package_name,
        base_init_lines=base_init_lines,
    )
