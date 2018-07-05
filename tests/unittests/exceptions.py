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
    expected = ('Failed reading story because of unexpected "value" at '
                'line 1, column 2')
    assert error.token_message('value', 1, 2) == expected


def test_storyscript_syntax_error_tree_message(error):
    expected = ('Failed reading story because of unexpected "value" at '
                'line 1')
    assert error.tree_message('value', 1) == expected


def test_storyscript_syntax_error_pretty_token(patch, error):
    patch.object(StoryscriptSyntaxError, 'token_message')
    error.error_type = 'unknown'
    result = error.pretty()
    args = (error.item, error.item.line, error.item.column)
    StoryscriptSyntaxError.token_message.assert_called_with(*args)
    assert result == StoryscriptSyntaxError.token_message()


def test_storyscript_syntax_error_pretty_tree(patch, error):
    patch.object(StoryscriptSyntaxError, 'tree_message')
    error.item.data = 'data'
    error.error_type = 'unknown'
    result = error.pretty()
    args = (error.item, error.item.line())
    StoryscriptSyntaxError.tree_message.assert_called_with(*args)
    assert result == StoryscriptSyntaxError.tree_message()


def test_storyscript_syntax_error_str_(patch, error):
    patch.object(StoryscriptSyntaxError, 'pretty', return_value='pretty')
    assert str(error) == StoryscriptSyntaxError.pretty()
