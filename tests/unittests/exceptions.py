# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.exceptions import StoryscriptSyntaxError


@fixture
def error(magic):
    return StoryscriptSyntaxError(0, magic(spec=['line', 'column']))


def test_storyscript_syntax_error_init():
    error = StoryscriptSyntaxError(0, 'item')
    assert error.error_type == 0
    assert error.item == 'item'
    assert issubclass(StoryscriptSyntaxError, SyntaxError)


def test_storyscript_syntax_error_reason(error):
    assert error.reason() == 'unknown'


def test_storyscript_syntax_error__str__token(patch, error):
    patch.object(StoryscriptSyntaxError, 'reason')
    message = '"{}" not allowed at line {}, column {}.\n\n> {}'
    args = (error.item, error.item.line, error.item.column, error.reason())
    assert str(error) == message.format(*args)


def test_storyscript_syntax_error__str__tree(patch, magic):
    patch.object(StoryscriptSyntaxError, 'reason')
    error = StoryscriptSyntaxError(0, magic(data='data'))
    args = (error.reason(), error.item.line())
    assert str(error) == '{} at line {}'.format(*args)
