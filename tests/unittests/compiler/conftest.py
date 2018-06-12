# -*- coding: utf-8 -*-
from pytest import fixture


@fixture
def tree(magic):
    return magic()
