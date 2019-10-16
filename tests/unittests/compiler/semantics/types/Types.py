# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import mark, raises

from storyscript.compiler.semantics.types.Types import AnyType, \
    BaseType, BooleanType, FloatType, IntType, ListType, MapType, \
    NoneType, NullType, ObjectType, RegExpType, StringType, singleton
from storyscript.hub.TypeMappings import TypeMappings


def test_singleton():
    c = 0

    def test_fn():
        nonlocal c
        c = c + 1
        return c
    single_fn = singleton(test_fn)
    assert single_fn() == 1
    assert single_fn() == 1
    assert c == 1


@mark.parametrize('type_,expected', [
    (BooleanType.instance(), 'boolean'),
    (IntType.instance(), 'int'),
    (FloatType.instance(), 'float'),
    (NoneType.instance(), 'none'),
    (AnyType.instance(), 'any'),
    (RegExpType.instance(), 'regexp'),
    (ListType(AnyType.instance()), 'List[any]'),
    (MapType(IntType.instance(), StringType.instance()),
        'Map[int,string]'),
    (NullType.instance(), 'null'),
])
def test_boolean_str(type_, expected):
    assert str(type_) == expected


def test_none_eq():
    assert NoneType.instance() == NoneType.instance()
    assert NoneType.instance() != IntType.instance()
    assert NoneType.instance() != AnyType.instance()


def test_none_assign():
    assert not NoneType.instance().can_be_assigned(IntType.instance())
    assert not NoneType.instance().can_be_assigned(AnyType.instance())


def test_none_op():
    none = NoneType.instance()
    assert none.binary_op(none, Token('MINUS', '-')) is None
    assert none.binary_op(IntType.instance(), Token('MINUS', '-')) is None
    assert none.binary_op(IntType.instance(), Token('PLUS', '+')) is None
    assert none.binary_op(StringType.instance(), Token('PLUS', '+')) is None
    assert none.binary_op(AnyType.instance(), None) is None


def test_none_explicit_from():
    assert NoneType.instance().explicit_from(IntType.instance()) is None
    assert NoneType.instance().explicit_from(AnyType.instance()) is None


def test_null_explicit_from():
    assert NullType.instance().explicit_from(NoneType.instance()) is None
    assert NullType.instance().explicit_from(AnyType.instance()) \
        is NullType.instance()
    assert NullType.instance().explicit_from(IntType.instance()) \
        is NullType.instance()


def test_null_hashable():
    assert not NullType.instance().hashable()


def test_base_type_not_implemented():
    with raises(NotImplementedError):
        BaseType().op(None)


def test_type_class_mapping():
    assert TypeMappings.type_class_mapping('float') == FloatType
    assert TypeMappings.type_class_mapping('boolean') == BooleanType
    assert TypeMappings.type_class_mapping('int') == IntType
    assert TypeMappings.type_class_mapping('string') == StringType
    assert TypeMappings.type_class_mapping('any') == AnyType
    assert TypeMappings.type_class_mapping('object') == ObjectType
    assert TypeMappings.type_class_mapping('list') == ListType
    assert TypeMappings.type_class_mapping('map') == MapType
