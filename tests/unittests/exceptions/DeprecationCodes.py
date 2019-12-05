# -*- coding: utf-8 -*-
from pytest import fixture, raises

from storyscript.exceptions.DeprecationCodes import DeprecationCodes


@fixture
def deprecation(monkeypatch):
    deprecation_tuple = ("D0123", "Test deprecation.")
    monkeypatch.setattr(
        DeprecationCodes, "foobar", deprecation_tuple, raising=False
    )
    return deprecation_tuple


def test_is_deprecation(deprecation):
    res = DeprecationCodes.is_deprecation("foobar")
    assert res is True

    res = DeprecationCodes.is_deprecation("nofoobar")
    assert res is False

    with raises(AssertionError) as e:
        DeprecationCodes.is_deprecation([])
    assert str(e.value) == "Deprecation name should be a string."


def test_get_deprecation(deprecation):
    res = DeprecationCodes.get_deprecation("foobar")
    assert res == deprecation
