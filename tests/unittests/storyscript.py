# -*- coding: utf-8 -*-
from storyscript import load, loads, version
from storyscript.api import Api


def test_storyscript_load():
    assert load == Api.load


def test_storyscript_loads():
    assert loads == Api.loads


def test_storyscript_version():
    assert version == '0.4.1'
