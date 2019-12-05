# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.exceptions.Deprecation import Deprecation
from storyscript.exceptions.DeprecationCodes import DeprecationCodes


@fixture
def deprecation(monkeypatch):
    deprecation_tuple = ("D0123", "Test deprecation {count}.")
    monkeypatch.setattr(
        DeprecationCodes, "foobar", deprecation_tuple, raising=False
    )
    return deprecation_tuple


def test_deprecation(deprecation):
    deprecation_obj = Deprecation("foobar", format_args={"count": 1})
    deprecation_msg = deprecation_obj.message()
    assert deprecation_msg == "Test deprecation 1."
    assert str(deprecation_obj) == "Test deprecation 1."

    deprecation_obj = Deprecation("nofoobar")
    deprecation_msg = deprecation_obj.message()
    assert deprecation_msg == "Unknown deprecation message"
    assert str(deprecation_obj) == "Unknown deprecation message"
