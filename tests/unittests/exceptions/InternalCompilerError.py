# -*- coding: utf-8 -*-

from pytest import raises

from storyscript.exceptions import InternalCompilerError, internal_assert


def test_internal_assert_0():
    with raises(InternalCompilerError) as e:
        internal_assert(0)
    assert e.value.message == 'Internal Error'


def test_internal_assert_equal():
    with raises(InternalCompilerError) as e:
        internal_assert(1, 2)
    assert e.value.message == '1 != 2'
