# -*- coding: utf-8 -*-
from storyscript.compiler import Compiler


def test_compiler_compiler():
    assert Compiler.compile('tree') == {}
