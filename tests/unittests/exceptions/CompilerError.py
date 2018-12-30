# -*- coding: utf-8 -*-
from storyscript.ErrorCodes import ErrorCodes
from storyscript.exceptions import CompilerError, ProcessingError


def test_compilererror():
    assert issubclass(CompilerError, ProcessingError)


def test_error_message(patch):
    patch.many(ErrorCodes, ['is_error', 'get_error'])
    e = CompilerError(None, message='test error')
    assert str(e) == 'test error'

    ErrorCodes.is_error.return_value = True
    ErrorCodes.get_error.return_value = [None, 'foo']
    e2 = CompilerError('my_custom_error')
    assert str(e2) == 'foo'

    ErrorCodes.is_error.return_value = False
    e3 = CompilerError(None)
    assert str(e3) == 'Unknown compiler error'
