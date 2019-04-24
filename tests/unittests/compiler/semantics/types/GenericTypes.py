from pytest import raises

from storyscript.compiler.semantics.types.GenericTypes import GenericType


def test_build_type_mapping_not_implemented():
    with raises(NotImplementedError):
        GenericType([None]).build_type_mapping({})


def test_base_type_name_not_implemented():
    with raises(NotImplementedError):
        GenericType([None]).base_type_name()
