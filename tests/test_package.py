import os
from pathlib import Path

import pytest
from func_adl_servicex_type_generator.data_model import (
    class_info,
    collection_info,
    enum_info,
    enum_value_info,
    extra_parameter,
    file_info,
    method_arg_info,
    method_info,
    normal_parameter,
    parameter_action,
)
from func_adl_servicex_type_generator.package import (
    py_type_from_cpp,
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
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [],
        "metadata": {},
    }
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    # Make sure basics are there
    assert output_path.exists()
    assert (output_path / "pyproject.toml").exists()

    # Make sure the src file has the proper package name now
    assert (output_path / data["package_name"]).exists()


def test_template_package_extra_file(tmp_path: Path, template_path):
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [],
        "metadata": {},
    }
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    files = [
        file_info(
            file_name="junk.py",
            init_lines=["line1", "line2"],
            contents=["line3", "line4"],
        )
    ]

    template_package_scaffolding(data, template_path, output_path, files)

    f_path = output_path / str(data["package_name"]) / "junk.py"
    assert f_path.exists()
    text = f_path.read_text()
    assert text == "line3\nline4\n"


def test_template_package_extra_file_in_subdir(tmp_path: Path, template_path):
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [],
        "metadata": {},
    }
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    files = [
        file_info(
            file_name="templates/junk.py",
            init_lines=["line1", "line2"],
            contents=["line3", "line4"],
        )
    ]

    template_package_scaffolding(data, template_path, output_path, files)

    f_path = output_path / str(data["package_name"]) / "templates" / "junk.py"
    assert f_path.exists()
    text = f_path.read_text()
    assert text == "line3\nline4\n"


def test_template_collection_with_object(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [],
                [],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    # Look at the output file and see if it contains what we expect
    assert (output_path / data["package_name"] / "event_collection.py").exists()

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "Iterable[Jet]" in text

    assert "'container_type': 'DataVector<Jet>'" in text
    assert "'element_type': 'Jet'" in text
    assert "'contains_collection': True," in text
    assert "'include_files': ['xAODJet/Jet.h',]" in text


def test_template_collection_with_extra_args(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [normal_parameter("name", "str", None)],
                [extra_parameter("calibrated", "bool", "True", [])],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    # Look at the output file and see if it contains what we expect
    assert (output_path / data["package_name"] / "event_collection.py").exists()

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "def Jets(self, name: str, calibrated: bool = True) -> Iterable[Jet]" in text
    assert "def process_Jets" in text


def test_template_collection_with_md(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [],
                [
                    extra_parameter(
                        "calibrated",
                        "bool",
                        "True",
                        [parameter_action("True", ["md_doit"], "my_bank")],
                    )
                ],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    # Look at the output file and see if it contains what we expect
    assert (output_path / data["package_name"] / "event_collection.py").exists()

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "            old_md = _param_metadata['md_doit']" in text


def test_paction_bool_true(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [],
                [
                    extra_parameter(
                        "calibrated",
                        "bool",
                        "True",
                        [parameter_action("True", ["md_doit"], "my_bank")],
                    )
                ],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "match_param_value(param_values['calibrated'], True)" in text


def test_paction_bool_any(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [],
                [
                    extra_parameter(
                        "calibrated",
                        "bool",
                        "True",
                        [parameter_action("'*Any*'", ["md_doit"], "my_bank")],
                    )
                ],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "match_param_value(param_values['calibrated'], '*Any*')" in text


def test_paction_bool_none(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [],
                [
                    extra_parameter(
                        "calibrated",
                        "bool",
                        "True",
                        [parameter_action("'*None*'", ["md_doit"], "my_bank")],
                    )
                ],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "match_param_value(param_values['calibrated'], '*None*')" in text


def test_paction_int(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [],
                [
                    extra_parameter(
                        "calibrated",
                        "int",
                        "True",
                        [parameter_action("55", ["md_doit"], "my_bank")],
                    )
                ],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "match_param_value(param_values['calibrated'], 55)" in text


def test_paction_str(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                ["xAODJet"],
                [],
                [
                    extra_parameter(
                        "calibrated",
                        "str",
                        "True",
                        [parameter_action("'55'", ["md_doit"], "my_bank")],
                    )
                ],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "match_param_value(param_values['calibrated'], '55')" in text


def test_template_collection_no_include(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                [],
                [],
                [],
                [],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "'include_files': []" in text


def test_template_collection_not_collection(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets", "Iterable[Jet]", "Jet", "Jet", "Jet", "Jet", [], [], [], [], ""
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "'contains_collection': False," in text


def test_template_collection_with_namespace(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[func_adl_servicex_xaodr21.xAOD.jet.Jet]",
                "xAOD.Jet",
                "Jet",
                "xAOD::Jet",
                "DataVector<xAOD::Jet>",
                ["xAODJet/Jet.h"],
                [],
                [],
                [],
                "",
            ),
        ],
        "metadata": {},
    }

    output_path = tmp_path / "my_package"
    template_package_scaffolding(data, template_path, output_path, [])

    # Look at the output file and see if it contains what we expect
    evt_col_file = output_path / data["package_name"] / "event_collection.py"

    text = evt_col_file.read_text()

    assert "import func_adl_servicex_xaodr21" in text
    assert "Iterable[func_adl_servicex_xaodr21.xAOD.jet.Jet]" in text


def test_template_poetry_integration(tmp_path, template_path):
    """Run a full integration test, including doing the poetry install."""
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [
            collection_info(
                "Jets",
                "Iterable[Jet]",
                "Jet",
                "Jet",
                "Jet",
                "DataVector<Jet>",
                ["xAODJet/Jet.h"],
                [],
                [],
                [],
                "",
            ),
        ],
        "metadata": {},
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    # Make sure basics are there
    assert output_path.exists()
    assert (output_path / "pyproject.toml").exists()

    # Make sure the src file has the proper package name now
    assert (output_path / data["package_name"]).exists()

    # Next, add a single class to make sure that works here!
    classes = [
        class_info("Jet", "Jet", [], None, None, "jet.hpp"),
    ]
    write_out_classes(
        classes,
        template_path,
        output_path / data["package_name"],
        data["package_name"],
        [""],
        "21",
    )

    # Make sure poetry is comfortable with this file
    python_location = r"C:\Users\gordo\Code\iris-hep\venv\Scripts\python.exe"
    r = os.system(
        f'powershell -command "cd {output_path}; {python_location} -m poetry check"'
    )
    assert r == 0


def test_template_single_sx_dataset(tmp_path, template_path):
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": [""],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [],
        "metadata": {},
    }
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    sx_dataset = output_path / "func_adl_servicex_xaodr21" / "sx_dataset.py"
    assert sx_dataset.exists()

    # Make sure it has only one dataset in it.
    text = sx_dataset.read_text()
    assert "class SXDSAtlasxAODR21(" in text
    assert "class FuncADLQuery(" in text
    assert "Defaults to `xaod_r21`" in text


def test_template_single_sx_flavors(tmp_path, template_path):
    data = {
        "package_name": "func_adl_servicex_xaodr21",
        "package_version": "1.0.22.2.187",
        "package_info_description": "xAOD R21 22.2.187",
        "calibration_types": ["", "PHYS"],
        "release_series": "21",
        "backend_default_name": "xaod_r21",
        "collections": [],
        "metadata": {},
    }
    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path, [])

    sx_dataset = output_path / "func_adl_servicex_xaodr21" / "sx_dataset.py"
    assert sx_dataset.exists()

    # Make sure it has only one dataset in it.
    text = sx_dataset.read_text()
    assert "class SXDSAtlasxAODR21(" in text
    assert "class SXDSAtlasxAODR21PHYS(" in text
    assert 'default_config("PHYS")' in text
    assert 'default_config("")' not in text


def test_class_simple(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("Jets", "Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    init_text = (tmp_path / "__init__.py").read_text()
    assert 'jets = _load_me("package.jets")' in init_text


def test_class_with_just_enum(tmp_path, template_path):
    """Write out a very simple top level class with enum

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "Jets",
            "Jets",
            [],
            None,
            None,
            "jet.hpp",
            enums=[enum_info(name="Color", values=[enum_value_info("Red", 1)])],
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    class_text = (tmp_path / "jets.py").read_text()
    assert "class Color(Enum)" in class_text
    assert "Red = 1" in class_text
    assert "from enum import Enum" in class_text

    assert "'metadata_type': 'define_enum'" not in class_text


def test_class_with_external_enum(tmp_path, template_path):
    """Two classes. One with enums, and the other class uses
    those enums.

    - Make sure the import works correctly
    - Make sure the enum is fully qualified in its reference.
    """
    classes = [
        class_info(
            "Jets",
            "Jets",
            [
                method_info(
                    name="pt_enum",
                    return_type="float",
                    arguments=[method_arg_info("color", None, "EnumOnly.Color")],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
        ),
        class_info(
            "EnumOnly",
            "EnumOnly",
            [],
            None,
            None,
            "jet.hpp",
            enums=[
                enum_info(
                    name="Color",
                    values=[enum_value_info("Red", 1), enum_value_info("Blue", 2)],
                )
            ],
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "jets.py").exists()
    class_text = (tmp_path / "jets.py").read_text()

    assert (
        "def pt_enum(self, color: package.enumonly.EnumOnly.Color) -> float"
        in class_text
    )
    assert "import package" in class_text

    assert "define_enum" in class_text
    assert "'namespace': 'EnumOnly'" in class_text


def test_class_with_referenced_enum(tmp_path, template_path):
    """Make sure to reference a local enum in the class, and set metadata
    correctly.
    """
    classes = [
        class_info(
            "Jets",
            "Jets",
            [
                method_info(
                    name="pt_enum",
                    return_type="float",
                    arguments=[method_arg_info("color", None, "Jets.Color")],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
            enums=[
                enum_info(
                    name="Color",
                    values=[enum_value_info("Red", 1), enum_value_info("Blue", 2)],
                )
            ],
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    class_text = (tmp_path / "jets.py").read_text()
    assert "class Color(Enum)" in class_text
    assert "def pt_enum(self, color: Jets.Color) -> float" in class_text

    assert "'metadata_type': 'define_enum'" in class_text
    assert "'namespace': 'Jets'" in class_text
    assert "'name': 'Color'" in class_text
    assert "'Red'" in class_text


def test_class_with_enum_and_int(tmp_path, template_path):
    """Make sure to reference a local enum in the class, and set metadata
    correctly.
    """
    classes = [
        class_info(
            "Jets",
            "Jets",
            [
                method_info(
                    name="pt_enum",
                    return_type="float",
                    arguments=[method_arg_info("color", None, "int")],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
            enums=[
                enum_info(
                    name="Color",
                    values=[enum_value_info("Red", 1), enum_value_info("Blue", 2)],
                )
            ],
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    class_text = (tmp_path / "jets.py").read_text()
    assert "'metadata_type': 'define_enum'" not in class_text


def test_class_with_just_enums(tmp_path, template_path):
    """Write out a very simple top level class with enum

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "Jets",
            "Jets",
            [],
            None,
            None,
            "jet.hpp",
            enums=[
                enum_info(
                    name="Color",
                    values=[enum_value_info("Red", 1), enum_value_info("Blue", 2)],
                )
            ],
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    class_text = (tmp_path / "jets.py").read_text()
    assert "class Color(Enum)" in class_text
    assert "Red = 1\n        Blue = 2" in class_text
    assert "from enum import Enum" in class_text


def test_class_simple_release_different(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("Jets", "Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(
        classes, template_path, tmp_path, "package", ["", "PHYS", "PHYSLITE"], "101"
    )

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    init_text = (tmp_path / "__init__.py").read_text()
    assert "SXDSAtlasxAODR101" in init_text
    assert "SXDSAtlasxAODR101PHYS" in init_text
    assert "SXDSAtlasxAODR101PHYSLITE" in init_text


def test_class_simple_multiple_calib_release(tmp_path, template_path):
    """Write out multiple calibration types

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("Jets", "Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(
        classes,
        template_path,
        tmp_path,
        "package",
        ["", "PHYS", "PHYSLITE"],
        "101",
    )

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    init_text = (tmp_path / "__init__.py").read_text()
    assert "SXDSAtlasxAODR101" in init_text
    assert "SXDSAtlasxAODR101PHYS" in init_text
    assert "SXDSAtlasxAODR101PHYSLITE" in init_text


def test_class_with_init_config(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("Jets", "Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(
        classes,
        template_path,
        tmp_path,
        "package",
        [""],
        "22",
        config_vars={"atlas": "1.1.1"},
    )

    init_text = (tmp_path / "__init__.py").read_text()
    assert 'atlas = "1.1.1"' in init_text


def test_class_alias(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("Jets", "Jets", [], None, None, "jet.hpp"),
        class_info("Jets1", "Jets1", [], None, None, "jet1.hpp", True),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert not (tmp_path / "jets1.py").exists()


def test_class_namespace(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets", "xAOD::Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "xAOD" / "jets.py").exists()

    assert (tmp_path / "xAOD" / "__init__.py").exists()
    init_text = (tmp_path / "xAOD" / "__init__.py").read_text()
    assert 'jets = _load_me("package.xAOD.jets")' in init_text

    assert (tmp_path / "__init__.py").exists()
    init_text = (tmp_path / "__init__.py").read_text()
    assert "from . import xAOD" in init_text


def test_class_namespace_method_ref(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [method_info("ajet", "xAOD::Forks", [], [], None)],
            None,
            None,
            "jet.hpp",
        ),
        class_info(
            "xAOD.Forks",
            "xAOD::Forks",
            [],
            None,
            None,
            "jet.hpp",
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "xAOD" / "jets.py").exists()
    class_text = (tmp_path / "xAOD" / "jets.py").read_text()

    assert "def ajet(self) -> package.xAOD.forks.Forks" in class_text
    assert "import package" in class_text


def test_class_as_container(tmp_path, template_path):
    """Write out a return that is a container that we (should) know about.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets", "xAOD::Jets", [], "xAOD::Fork", "xAOD.Fork", "jet.hpp"),
        class_info("xAOD.Fork", "xAOD::Fork", [], None, None, "fork.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "xAOD" / "jets.py").exists()
    file_text = (tmp_path / "xAOD" / "jets.py").read_text()
    jet_class = [ln for ln in file_text.split("\n") if "class Jets" in ln]
    assert len(jet_class) == 1
    assert "(Iterable[package.xAOD.fork.Fork])" in jet_class[0]


def test_class_as_unknown_container(tmp_path, template_path):
    """Write out a return that is a container that we (should) know about.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets", "xAOD::Jets", [], "xAOD::Fork", "xAOD.Fork", "jet.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "xAOD" / "jets.py").exists()
    file_text = (tmp_path / "xAOD" / "jets.py").read_text()
    jet_class = [ln for ln in file_text.split("\n") if "class Jets" in ln]
    assert len(jet_class) == 1
    assert "(Iterable[xAOD.Fork])" not in jet_class[0]


def test_class_as_container_no_ns(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets", "xAOD::Jets", [], "Fork", "Fork", "jet.hpp"),
        class_info("Fork", "Fork", [], None, None, "fork.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "xAOD" / "jets.py").exists()
    file_text = (tmp_path / "xAOD" / "jets.py").read_text()
    jet_class = [ln for ln in file_text.split("\n") if "class Jets" in ln]
    assert len(jet_class) == 1
    assert "(Iterable[package.fork.Fork])" in jet_class[0]


def test_class_as_container_include(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets", "xAOD::Jets", [], "Fork", "Fork", "jet.hpp"),
        class_info("Fork", "Fork", [], None, None, "fork.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert (tmp_path / "xAOD" / "jets.py").exists()
    file_text = (tmp_path / "fork.py").read_text()
    jet_class = [ln for ln in file_text.split("\n") if "fork.hpp" in ln]
    assert len(jet_class) == 2
    assert "body_includes" in jet_class[1]


def test_simple_method(tmp_path, template_path):
    """Write out a very simple top level class with a method.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [
                method_info(
                    name="pt",
                    return_type="float",
                    arguments=[],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
        )
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()
    assert "pt(self) -> float:" in all_text
    assert "'return_type': 'float'" in all_text


def test_method_with_behavior(tmp_path, template_path):
    """Write out a very simple top level class with a method.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [
                method_info(
                    name="pt1",
                    return_type="float",
                    arguments=[],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
            behaviors=["xAOD::Tracks"],
        ),
        class_info(
            "xAOD.Tracks",
            "xAOD::Tracks",
            [
                method_info(
                    name="pt2",
                    return_type="float",
                    arguments=[],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()
    assert "pt1(self) -> float:" in all_text
    assert "pt2(self) -> float:" in all_text
    assert "deref_count" not in all_text


def test_method_with_behavior_deref(tmp_path, template_path):
    """Write out a very simple top level class with a method.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [
                method_info(
                    name="pt1",
                    return_type="float",
                    arguments=[],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
            behaviors=["xAOD::Tracks**"],
        ),
        class_info(
            "xAOD.Tracks",
            "xAOD::Tracks",
            [
                method_info(
                    name="pt2",
                    return_type="float",
                    arguments=[],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()
    assert "'deref_count': 2" in all_text


def test_simple_method_ptr(tmp_path, template_path):
    """Write out a very simple top level class with a method.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [
                method_info(
                    name="pt",
                    return_type="float*",
                    arguments=[],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
        )
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()
    assert "pt(self) -> float:" in all_text
    assert "'return_type': 'float*'" in all_text


def test_simple_method_return_type_cleaning(tmp_path, template_path):
    """Write out a vector and make sure the class hows up "clean".

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [
                method_info(
                    name="pt",
                    return_type="vector<DataVector<xAOD::Jet_v1>  >",
                    arguments=[],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
        ),
        class_info(
            "vector_DataVector_xAOD_Jet_v1",
            "vector<DataVector<xAOD::Jet_v1>  >",
            [],
            None,
            None,
            "vector",
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()
    assert "'return_type': 'vector<DataVector<xAOD::Jet_v1>>'" in all_text


def test_simple_method_with_args(tmp_path, template_path):
    """Write out a very simple top level class with a method.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [
                method_info(
                    name="pt",
                    return_type="float",
                    arguments=[method_arg_info("err", None, "float")],
                    param_arguments=[],
                    param_helper=None,
                )
            ],
            None,
            None,
            "jet.hpp",
        )
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    assert "pt(self, err: float) -> float:" in (
        (tmp_path / "xAOD" / "jets.py").read_text()
    )


def test_method_with_param_args(tmp_path, template_path):
    """Write out a very simple top level class with a method."""
    classes = [
        class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [
                method_info(
                    name="pt",
                    return_type="float",
                    arguments=[method_arg_info("err", None, "float")],
                    param_arguments=[method_arg_info("rtn_type", None, "cpp_type[U]")],
                    param_helper="fetcher",
                )
            ],
            None,
            None,
            "jet.hpp",
        )
    ]

    write_out_classes(classes, template_path, tmp_path, "package", [""], "22")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()

    assert "@property" in all_text
    assert "def pt(self) -> package.fetcher[float]:" in all_text


def test_py_type_from_cpp_class_name():
    class_dict = {
        "xAOD::Jets": class_info("xAOD.Jets", "xAOD::Jets", [], None, None, "jet.hpp"),
        "xAOD::Taus": class_info("xAOD.Taus", "xAOD::Taus", [], None, None, "tau.hpp"),
    }

    assert py_type_from_cpp("xAOD::Jets", class_dict) == "xAOD.Jets"


def test_py_type_from_cpp_class_enum():
    class_dict = {
        "xAOD::Jets": class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [],
            None,
            None,
            "jet.hpp",
            enums=[enum_info(name="Color", values=[enum_value_info("Red", 1)])],
        ),
        "xAOD::Taus": class_info("xAOD.Taus", "xAOD::Taus", [], None, None, "tau.hpp"),
    }

    assert py_type_from_cpp("xAOD::Jets::Color", class_dict) == "xAOD.Jets.Color"


def test_py_type_from_cpp_class_bad():
    class_dict = {
        "xAOD::Jets": class_info(
            "xAOD.Jets",
            "xAOD::Jets",
            [],
            None,
            None,
            "jet.hpp",
            enums=[enum_info(name="Color", values=[enum_value_info("Red", 1)])],
        ),
        "xAOD::Taus": class_info("xAOD.Taus", "xAOD::Taus", [], None, None, "tau.hpp"),
    }

    with pytest.raises(RuntimeError) as e:
        py_type_from_cpp("xAOD::Jets::ColorR", class_dict)

    assert "ColorR" in str(e.value)
