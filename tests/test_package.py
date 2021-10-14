import os
from pathlib import Path

import pytest
from func_adl_servicex_type_generator.data_model import class_info, collection_info
from func_adl_servicex_type_generator.package import (
    template_package_scaffolding,
    write_out_classes,
)


@pytest.fixture
def template_path():
    yield Path("./template")


def test_template_package(tmp_path, template_path):
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "collections": [],
    }
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

    # Make sure basics are there
    assert output_path.exists()
    assert (output_path / "pyproject.toml").exists()

    # Make sure the src file has the proper package name now
    assert (output_path / data["package_name"]).exists()


def test_template_collection_with_object(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "collections": [
            collection_info("Jets", "Iterable[Jet]", "Jet"),
        ],
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

    # Look at the output file and see if it contains what we expect
    assert (output_path / data["package_name"] / "event_collection.py").exists()

    assert "from func_adl_servicex_xaodr21 import Jet" in (
        (output_path / data["package_name"] / "event_collection.py").read_text()
    )


def test_template_poetry_integration(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "collections": [
            collection_info("Jets", "Iterable[Jet]", "Jet"),
        ],
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

    # Make sure basics are there
    assert output_path.exists()
    assert (output_path / "pyproject.toml").exists()

    # Make sure the src file has the proper package name now
    assert (output_path / data["package_name"]).exists()

    # Next, add a single class to make sure that works here!
    classes = [
        class_info("Jet"),
    ]
    write_out_classes(classes, template_path, output_path / data["package_name"])

    # Make sure poetry is comfortable with this file
    r = os.system(
        f'powershell -command "cd {output_path}; my_python -m poetry install"'
    )
    assert r == 0
    event_python_path = Path(data["package_name"]) / "event_collection.py"
    r = os.system(
        f'powershell -command "cd {output_path}; my_python -m poetry run python {event_python_path}"'
    )
    assert r == 0
    r = os.system(
        f'powershell -command "cd {output_path}; my_python -m poetry env remove"'
    )
    assert r != 0


def test_class_simple(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("Jets"),
    ]

    write_out_classes(classes, template_path, tmp_path)

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    # Make sure the jets class will load
    assert "from .jets import Jets" in ((tmp_path / "__init__.py").read_text())


def test_class_namespace(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets"),
    ]

    write_out_classes(classes, template_path, tmp_path)

    assert (tmp_path / "xAOD" / "jets.py").exists()
    assert (tmp_path / "xAOD" / "__init__.py").exists()
    assert (tmp_path / "__init__.py").exists()

    assert "from .jets import Jets" in ((tmp_path / "xAOD" / "__init__.py").read_text())
