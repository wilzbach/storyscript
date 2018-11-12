# -*- coding: utf-8 -*-
from storyscript import load, loads, version
from storyscript.Api import Api
from storyscript.Version import version as real_version


def test_storyscript_load():
    assert load == Api.load


def test_storyscript_loads():
    assert loads == Api.loads


def test_storyscript_version():
    assert version == real_version
