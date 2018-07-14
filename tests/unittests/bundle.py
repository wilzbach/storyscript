# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.bundle import Bundle


@fixture
def bundle():
    return Bundle('path')


def test_bundle_init(bundle):
    assert bundle.path == 'path'
