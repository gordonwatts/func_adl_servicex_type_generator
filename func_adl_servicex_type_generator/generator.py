import itertools
from pathlib import Path
import argparse
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
        "--output_directory",
        type=Path,
        help="The output directory for the generated python package",
        default=Path("../func_adl_servicex_xaodrXX"),
    )
    args = parser.parse_args()

    data = load_yaml(args.yaml_type_file)

    # Extract release info
    release_name = data.config["atlas_release"]
    release_tuple = split_release(release_name)
    package_name = f"func_adl_servicex_xaodr{release_tuple[0]}"

    # Fix up the collection types
    all_class_names = {c.name for c in data.classes}
    for c in data.collections:
        new_c = package_qualified_class(
            c.collection_type, package_name, all_class_names
        )
        assert new_c is not None
        c.collection_type = new_c

    # Build up all the dataset types we are going to support
    dataset_object_basename = f"SXDSAtlasxAODR{release_tuple[0]}"
    dataset_types = [(dataset_object_basename, "")] + [
        (dataset_object_basename + ds_type, ds_type)
        for ds_type in data.config["dataset_types"]
    ]

    template_data = {
        "package_name": package_name,
        "package_version": f"1.1.5.{release_name}",
        "package_info_description": f"xAOD R{release_tuple[0]} {data.config['atlas_release']}",
        "sx_dataset_name": dataset_types,
        "backend_default_name": f"xaod_r{release_tuple[0]}",
        "collections": data.collections,
        "metadata": data.metadata,
    }

    template_path = Path(__file__).parent / ".." / "template"
    assert template_path.exists()
    output_path = args.output_directory

    template_package_scaffolding(template_data, template_path, output_path, data.files)

    base_init_lines = list(itertools.chain(*[f.init_lines for f in data.files]))

    write_out_classes(
        data.classes,
        template_path,
        output_path / template_data["package_name"],
        package_name,
        str(release_tuple[0]),
        base_init_lines=base_init_lines,
        config_vars=data.config,
    )
