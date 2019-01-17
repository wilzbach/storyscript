# -*- coding: utf-8 -*-
from pytest import raises

from storyscript.ErrorCodes import ErrorCodes
from storyscript.exceptions import ProcessingError
from storyscript.exceptions.CompilerError import CompilerError, ConstDict


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


def test_const_dict():
    d = ConstDict({'foo': 'bar', 'f2': 'b2'})
    assert d.foo == 'bar'
    assert d.f2 == 'b2'
    with raises(Exception):
        d.bar


def test_compiler_error_extra_parameters():
    e2 = CompilerError('my_custom_error', my_param='p1', my_param2='p2')
    assert e2.extra.my_param == 'p1'
    assert e2.extra.my_param2 == 'p2'
