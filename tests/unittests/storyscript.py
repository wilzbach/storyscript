# -*- coding: utf-8 -*-
from storyscript import load, loads
from storyscript.app import App


def test_storyscript_load():
    assert load == App.load


def test_storyscript_loads():
    assert loads == App.loads
