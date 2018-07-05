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


def test_storyscript_syntax_error_token_message(error):
    expected = ('Failed reading story because of unexpected "value" at'
                'line 1, column 2')
    assert error.token_message('value', 1, 2) == expected


def test_storyscript_syntax_error_pretty_token(patch, error):
    patch.object(StoryscriptSyntaxError, 'reason')
    message = '"{}" not allowed at line {}, column {}.\n\n> {}'
    args = (error.item, error.item.line, error.item.column, error.reason())
    assert error.pretty() == message.format(*args)


def test_storyscript_syntax_error_pretty_tree(patch, magic):
    patch.object(StoryscriptSyntaxError, 'reason')
    error = StoryscriptSyntaxError(0, magic(data='data'))
    args = (error.reason(), error.item.line())
    assert error.pretty() == '{} at line {}'.format(*args)


def test_storyscript_syntax_error_str_(patch, error):
    patch.object(StoryscriptSyntaxError, 'pretty', return_value='pretty')
    assert str(error) == StoryscriptSyntaxError.pretty()
