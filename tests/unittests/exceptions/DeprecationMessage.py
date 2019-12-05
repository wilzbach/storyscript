# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.exceptions.Deprecation import Deprecation
from storyscript.exceptions.DeprecationCodes import DeprecationCodes
from storyscript.exceptions.DeprecationMessage import DeprecationMessage


@fixture
def deprecation(monkeypatch):
    deprecation_tuple = ("D0123", "Test deprecation {count}.")
    monkeypatch.setattr(
        DeprecationCodes, "foobar", deprecation_tuple, raising=False
    )
    return deprecation_tuple


def test_deprecation_process(deprecation):
    deprecation_obj = Deprecation("foobar", format_args={"count": 1})
    deprecation_msg = DeprecationMessage(deprecation_obj, None)
    deprecation_msg.process()
    assert deprecation_msg.error_tuple == deprecation

    deprecation_obj = Deprecation("nofoobar")
    deprecation_msg = DeprecationMessage(deprecation_obj, None)
    deprecation_msg.process()
    assert (
        deprecation_msg.error_tuple
        == DeprecationCodes.unidentified_deprecation
    )


def test_deprecation_hint(deprecation):
    deprecation_obj = Deprecation("foobar", format_args={"count": 1})
    deprecation_msg = DeprecationMessage(deprecation_obj, None)
    deprecation_msg.process()
    assert deprecation_msg.hint() == "Test deprecation 1."

    deprecation_obj = Deprecation("nofoobar")
    deprecation_msg = DeprecationMessage(deprecation_obj, None)
    deprecation_msg.process()
    assert (
        deprecation_msg.hint()
        == """Internal error occured: Unknown deprecation message
Please report at https://github.com/storyscript/storyscript/issues"""
    )
