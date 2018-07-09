# -*- coding: utf-8 -*-
from storyscript.compiler import Preprocessor


def test_preprocessor_process():
    assert Preprocessor.process('tree') == 'tree'
