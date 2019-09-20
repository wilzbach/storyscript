# -*- coding: utf-8 -*-
from pytest import raises

from storyscript.exceptions.Diagnostics import ConstDict


def test_const_dict():
    """
    Ensures that the const dictionary provides access
    """
    d = ConstDict({'foo': 'bar', 'f2': 'b2'})
    assert d.foo == 'bar'
    assert d.f2 == 'b2'
    with raises(Exception):
        d.bar
