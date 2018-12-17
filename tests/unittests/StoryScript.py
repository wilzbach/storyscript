# -*- coding: utf-8 -*-
from storyscript import load, load_map, loads, version
from storyscript.Api import Api
from storyscript.Version import version as real_version


def test_storyscript_load():
    assert load == Api.load


def test_storyscript_loads():
    assert loads == Api.loads


def test_storyscript_load_map():
    assert load_map == Api.load_map


def test_storyscript_version():
    assert version == real_version
