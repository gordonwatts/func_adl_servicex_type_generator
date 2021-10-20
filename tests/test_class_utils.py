from pathlib import Path
from func_adl_servicex_type_generator.class_utils import (
    class_ns_as_path,
    class_split_namespace,
    import_for_class,
    remove_namespaces,
)


def test_split_single_name():
    c_ns, c_name = class_split_namespace("Jets")
    assert c_ns == ""
    assert c_name == "Jets"


def test_split_ns_simple():
    c_ns, c_name = class_split_namespace("xAOD.Jets")
    assert c_ns == "xAOD"
    assert c_name == "Jets"


def test_as_path_simple_ns():
    r = class_ns_as_path("xAOD")
    assert isinstance(r, Path)
    assert str(r) == "xAOD"


def test_as_path_no_ns():
    r = class_ns_as_path("")
    assert str(r) == "."


def test_import_no_ns():
    assert import_for_class("Jets", "base") == "from base.jets import Jets"


def test_import_ns():
    assert import_for_class("xAOD.Jets", "basic") == "from basic.xAOD.jets import Jets"


def test_remove_namespace_none():
    assert remove_namespaces("int") == "int"


def test_remove_namespace_simple():
    assert remove_namespaces("xAOD.Junk") == "Junk"


def test_remove_namespace_arg():
    assert remove_namespaces("Iterable[xAOD.Junk]") == "Iterable[Junk]"


def test_remove_namespace_args():
    assert remove_namespaces("Iterable[xAOD.Junk, xAOD.Fool]") == "Iterable[Junk, Fool]"


def test_remove_namespace_initial():
    assert remove_namespaces("xAOD.Iterable[xAOD.Junk]") == "Iterable[Junk]"
