from pytest import raises

from storyscript.compiler.semantics.types.GenericTypes import GenericType


def test_build_type_mapping_not_implemented():
    with raises(NotImplementedError):
        GenericType().build_type_mapping({})
