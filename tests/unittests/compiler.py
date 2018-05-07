# -*- coding: utf-8 -*-
from storyscript.compiler import Compiler
from storyscript.version import version


def test_compiler_compiler():
    assert Compiler.compile('tree') == {'script': {}, 'version': version}
