import os
from pathlib import Path
from func_adl_servicex_type_generator.data_model import collection_info

from func_adl_servicex_type_generator.package import template_package_scaffolding


def test_template_package(tmp_path):
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.r22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
    }
    template_path = Path("./template")
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

    # Make sure basics are there
    assert output_path.exists()
    assert (output_path / "pyproject.toml").exists()

    # Make sure poetry is comfortable with this file
    r = os.system(f'powershell -command "cd {output_path}; poetry check"')
    assert r == 0

    # Make sure the src file has the proper package name now
    assert (output_path / data["package_name"]).exists()


def test_template_event(tmp_path):
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.r22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "collections": [
            collection_info("Jets", "Iterable[Jet]"),
        ],
    }

    template_path = Path("./template")
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

    # Make sure basics are there
    assert output_path.exists()
    assert (output_path / "pyproject.toml").exists()

    # Make sure poetry is comfortable with this file
    event_python_path = output_path / data["package_name"] / "event_collection.py"
    r = os.system(f'powershell -command "cd {output_path}; python {event_python_path}"')
    assert r == 0

    # Make sure the src file has the proper package name now
    assert (output_path / data["package_name"]).exists()
