# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.exceptions import StoryscriptSyntaxError


@fixture
def error(magic):
    return StoryscriptSyntaxError(0, magic())


def test_storyscript_syntax_error_init():
    error = StoryscriptSyntaxError(0, 'token')
    assert error.error_type == 0
    assert error.token == 'token'
    assert issubclass(StoryscriptSyntaxError, SyntaxError)


def test_storyscript_syntax_error_reason(error):
    assert error.reason() == 'unknown'


def test_storyscript_syntax_error_str(patch, error):
    patch.object(StoryscriptSyntaxError, 'reason')
    message = '"{}" not allowed at line {}, column {}.\n\n{}'
    assert str(error) == message.format(error.token, error.token.line,
                                        error.token.column, error.reason())
