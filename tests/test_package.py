import os
from pathlib import Path

import pytest
from func_adl_servicex_type_generator.data_model import (
    class_info,
    collection_info,
    method_arg_info,
    method_info,
)
from func_adl_servicex_type_generator.package import (
    imports_for_method,
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
            ),
        ],
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

    # Look at the output file and see if it contains what we expect
    assert (output_path / data["package_name"] / "event_collection.py").exists()

    evt_col_path = output_path / data["package_name"] / "event_collection.py"
    text = evt_col_path.read_text()
    assert "from func_adl_servicex_xaodr21.jet import Jet" in text
    assert "Iterable[Jet]" in text

    assert "'container_type': 'DataVector<Jet>'" in text
    assert "'element_type': 'Jet'" in text
    assert "'contains_collection': True," in text
    assert "'include_files': ['xAODJet/Jet.h',]" in text


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
                "Jets", "Iterable[Jet]", "Jet", "Jet", "Jet", "DataVector<Jet>", [], []
            ),
        ],
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

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
                "Jets", "Iterable[Jet]", "Jet", "Jet", "Jet", "Jet", [], []
            ),
        ],
    }

    assert template_path.exists()
    output_path = tmp_path / "my_package"

    template_package_scaffolding(data, template_path, output_path)

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
                "Iterable[xAOD.Jet]",
                "xAOD.Jet",
                "Jet",
                "xAOD::Jet",
                "DataVector<xAOD::Jet>",
                ["xAODJet/Jet.h"],
                [],
            ),
        ],
    }

    output_path = tmp_path / "my_package"
    template_package_scaffolding(data, template_path, output_path)

    # Look at the output file and see if it contains what we expect
    evt_col_file = output_path / data["package_name"] / "event_collection.py"

    text = evt_col_file.read_text()

    assert "from func_adl_servicex_xaodr21.xAOD.jet import Jet" in text
    assert "Iterable[Jet]" in text


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
            ),
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
    # event_python_path = Path(data["package_name"]) / "event_collection.py"
    # r = os.system(
    #     f'powershell -command "cd {output_path}; my_python -m poetry run python '
    #     f'{event_python_path}"'
    # )
    # assert r == 0
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
    assert (tmp_path / "__init__.py").exists()


def test_class_as_container(tmp_path, template_path):
    """Write out a very simple top level class.

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
    assert "(Iterable[Fork])" in jet_class[0]

    import_class = [ln for ln in file_text.split("\n") if "import Fork" in ln]
    assert len(import_class) == 1
    assert "from package.xAOD.fork import Fork" in import_class[0]


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
    assert "(Iterable[Fork])" in jet_class[0]

    import_class = [ln for ln in file_text.split("\n") if "import Fork" in ln]
    assert len(import_class) == 1
    assert "from package.fork import Fork" in import_class[0]


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
    assert len(jet_class) == 1
    assert "files" in jet_class[0]


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
                    return_is_pointer=False,
                    arguments=[],
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
    assert "'is_pointer': 'False'" in all_text


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
                    return_type="float",
                    return_is_pointer=True,
                    arguments=[],
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
    assert "'is_pointer': 'True'" in all_text


def test_simple_method_rtn_collection(tmp_path, template_path):
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
                    name="others",
                    return_type="VectorOfFloats",
                    return_is_pointer=False,
                    arguments=[],
                )
            ],
            None,
            None,
            "jet.hpp",
        ),
        class_info(
            "VectorOfFloats", "VectorOfFloatsCPP", [], "double", "float", "vector.hpp"
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package")

    jets_text = (tmp_path / "xAOD" / "jets.py").read_text()
    assert "others(self) -> VectorOfFloats:" in jets_text
    assert "'return_type_element': 'double'" in jets_text
    assert "'return_type_collection': 'VectorOfFloatsCPP'" in jets_text


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
                    return_is_pointer=False,
                    arguments=[method_arg_info("err", None, "float")],
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


def test_method_reference_rtn_type(tmp_path, template_path):
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
                    return_is_pointer=False,
                    arguments=[],
                )
            ],
            None,
            None,
            "jet.hpp",
        ),
        class_info(
            "xAOD.Taus",
            "xAOD::Taus",
            [
                method_info(
                    name="pt",
                    return_type="xAOD.Jets",
                    return_is_pointer=False,
                    arguments=[],
                )
            ],
            None,
            None,
            "tau.hpp",
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package")

    assert "from package.xAOD.jets import Jets" in (
        (tmp_path / "xAOD" / "taus.py").read_text()
    )
    assert "pt(self) -> Jets:" in ((tmp_path / "xAOD" / "taus.py").read_text())


def test_method_reference_rtn_type_same_as_class(tmp_path, template_path):
    """Method returns class that is being defined - so no import should exist.

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
                    return_type="xAOD.Jets",
                    return_is_pointer=False,
                    arguments=[],
                )
            ],
            None,
            None,
            "jet.hpp",
        ),
    ]

    write_out_classes(classes, template_path, tmp_path, "package")

    assert "pt(self) -> 'Jets':" in ((tmp_path / "xAOD" / "jets.py").read_text())
    assert "from package.xAOD.jets import Jets" not in (
        (tmp_path / "xAOD" / "jets.py").read_text()
    )


def test_method_import_nothing():
    m = method_info("pt", "double", False, [])
    assert len(imports_for_method(m, "hi", "junk", {"one", "two"})) == 0


def test_method_import_return_type():
    m = method_info("pt", "xAOD.Jet_v1", False, [])

    r = imports_for_method(m, "hi", "junk", {"xAOD.Jet_v1"})
    assert len(r) == 1
    assert r[0] == "from junk.xAOD.jet_v1 import Jet_v1"


def test_method_import_return_type_enclosing():
    m = method_info("pt", "xAOD.Jet_v1", False, [])

    r = imports_for_method(m, "xAOD.Jet_v1", "junk", {"xAOD.Jet_v1"})
    assert len(r) == 0


def test_method_import_arguments():
    m = method_info(
        "pt",
        "double",
        False,
        [
            method_arg_info("arg1", None, "xAOD.Jet_v1"),
            method_arg_info("arg2", None, "xAOD.TauJet"),
        ],
    )

    r = imports_for_method(m, "hi", "junk", {"xAOD.Jet_v1", "xAOD.TauJet"})
    assert len(r) == 2

    assert "from junk.xAOD.jet_v1 import Jet_v1" in r
    assert "from junk.xAOD.taujet import TauJet" in r
