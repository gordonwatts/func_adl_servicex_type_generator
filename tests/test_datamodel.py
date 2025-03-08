from func_adl_servicex_type_generator.data_model import class_info
import pytest


def test_class_with_space_as_container():
    "Make sure spaces in class names don't cause a problem"
    with pytest.raises(AssertionError):
        class_info("xAOD.Jets", "xAOD::Jets", [], None, "unsigned jets", "jet.hpp")


def test_class_with_space_as_name():
    "Make sure spaces in class names don't cause a problem"
    with pytest.raises(AssertionError):
        class_info("xAOD Jets", "xAOD::Jets", [], None, "unsigned jets", "jet.hpp")
