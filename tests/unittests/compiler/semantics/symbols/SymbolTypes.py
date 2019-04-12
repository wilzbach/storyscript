# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import mark

from storyscript.compiler.semantics.symbols.SymbolTypes import AnyType, \
    BooleanType, FloatType, IntType, ListType, NoneType, \
    ObjectType, StringType, singleton


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
    (ListType(AnyType.instance()), 'list[any]'),
    (ObjectType(IntType.instance(), StringType.instance()),
        'map[int,string]'),
])
def test_boolean_str(type_, expected):
    assert str(type_) == expected


def test_none_eq():
    assert NoneType.instance() == NoneType.instance()
    assert NoneType.instance() != IntType.instance()
    assert NoneType.instance() != AnyType.instance()


def test_none_assign():
    assert not NoneType.instance().can_be_assigned(IntType.instance)
    assert not NoneType.instance().can_be_assigned(AnyType.instance)


def test_none_op():
    none = NoneType.instance()
    assert none.op(none, Token('MINUS', '-')) is None
    assert none.op(IntType.instance(), Token('MINUS', '-')) is None
    assert none.op(IntType.instance(), Token('PLUS', '+')) is None
    assert none.op(StringType.instance(), Token('PLUS', '+')) == \
        StringType.instance()
    assert none.op(AnyType.instance(), None) is AnyType.instance()
