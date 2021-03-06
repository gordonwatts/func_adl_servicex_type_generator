import os
from pathlib import Path

import pytest
from func_adl_servicex_type_generator.data_model import (
    class_info,
    collection_info,
    extra_parameter,
    file_info,
    method_arg_info,
    method_info,
    normal_parameter,
    parameter_action,
)
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        "sx_dataset_name": "SXDSAtlasxAODR21",
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
        classes, template_path, output_path / data["package_name"], data["package_name"]
    )

    # Make sure poetry is comfortable with this file
    r = os.system(
        f'powershell -command "cd {output_path}; my_python -m poetry install"'
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
        class_info("Jets", "Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package")

    assert (tmp_path / "jets.py").exists()
    assert (tmp_path / "__init__.py").exists()

    init_text = (tmp_path / "__init__.py").read_text()
    assert 'jets = _load_me("package.jets")' in init_text


def test_class_with_init_config(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("Jets", "Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(
        classes, template_path, tmp_path, "package", config_vars={"atlas": "1.1.1"}
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

    write_out_classes(classes, template_path, tmp_path, "package")

    assert not (tmp_path / "jets1.py").exists()


def test_class_namespace(tmp_path, template_path):
    """Write out a very simple top level class.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets", "xAOD::Jets", [], None, None, "jet.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package")

    assert (tmp_path / "xAOD" / "jets.py").exists()

    assert (tmp_path / "xAOD" / "__init__.py").exists()
    init_text = (tmp_path / "xAOD" / "__init__.py").read_text()
    assert 'jets = _load_me("package.xAOD.jets")' in init_text

    assert (tmp_path / "__init__.py").exists()
    init_text = (tmp_path / "__init__.py").read_text()
    assert "from . import xAOD" in init_text


def test_class_as_container(tmp_path, template_path):
    """Write out a return that is a container that we (should) know about.

    Args:
        tmp_path ([type]): [description]
    """
    classes = [
        class_info("xAOD.Jets", "xAOD::Jets", [], "xAOD::Fork", "xAOD.Fork", "jet.hpp"),
        class_info("xAOD.Fork", "xAOD::Fork", [], None, None, "fork.hpp"),
    ]

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()
    assert "'return_type': 'vector<DataVector<xAOD::Jet_v1>>'" in all_text


# def test_simple_method_rtn_collection(tmp_path, template_path):
#     """Write out a very simple top level class with a method.

#     Args:
#         tmp_path ([type]): [description]
#     """
#     classes = [
#         class_info(
#             "xAOD.Jets",
#             "xAOD::Jets",
#             [
#                 method_info(
#                     name="others",
#                     return_type="VectorOfFloats",
#                     return_is_pointer=False,
#                     arguments=[],
#                 )
#             ],
#             None,
#             None,
#             "jet.hpp",
#         ),
#         class_info(
#             "VectorOfFloats", "VectorOfFloatsCPP", [], "double", "float", "vector.hpp"
#         ),
#     ]

#     write_out_classes(classes, template_path, tmp_path, "package")

#     jets_text = (tmp_path / "xAOD" / "jets.py").read_text()
#     assert "others(self) -> package.VectorOfFloats:" in jets_text
#     assert "'return_type_element': 'double'" in jets_text
#     assert "'return_type_collection': 'VectorOfFloatsCPP'" in jets_text
# TODO: Fix or remove


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

    write_out_classes(classes, template_path, tmp_path, "package")

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

    write_out_classes(classes, template_path, tmp_path, "package")

    all_text = (tmp_path / "xAOD" / "jets.py").read_text()

    assert "@property" in all_text
    assert "def pt(self) -> package.fetcher[float]:" in all_text


# def test_method_reference_rtn_type(tmp_path, template_path):
#     """Write out a very simple top level class with a method.

#     Args:
#         tmp_path ([type]): [description]
#     """
#     classes = [
#         class_info(
#             "xAOD.Jets",
#             "xAOD::Jets",
#             [
#                 method_info(
#                     name="pt",
#                     return_type="float",
#                     return_is_pointer=False,
#                     arguments=[],
#                 )
#             ],
#             None,
#             None,
#             "jet.hpp",
#         ),
#         class_info(
#             "xAOD.Taus",
#             "xAOD::Taus",
#             [
#                 method_info(
#                     name="pt",
#                     return_type="xAOD.Jets",
#                     return_is_pointer=False,
#                     arguments=[],
#                 )
#             ],
#             None,
#             None,
#             "tau.hpp",
#         ),
#     ]

#     write_out_classes(classes, template_path, tmp_path, "package")

#     tau_text = (tmp_path / "xAOD" / "taus.py").read_text()
#     assert "import package" in tau_text
#     assert "pt(self) -> package.xAOD.Jets:" in tau_text
# TODO: Fix or remove
