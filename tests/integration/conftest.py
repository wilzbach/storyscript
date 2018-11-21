# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.parser import Parser


@fixture
def parser():
    return Parser()
