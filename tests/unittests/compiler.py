# -*- coding: utf-8 -*-
from storyscript.compiler import Compiler
from storyscript.version import version


def test_compiler_compile(patch):
    patch.object(Compiler, 'parse_tree')
    result = Compiler.compile('tree')
    Compiler.parse_tree.assert_called_with('tree')
    assert result == {'script': Compiler.parse_tree(), 'version': version}


def test_compiler_parse_tree():
    assert Compiler.parse_tree('tree') == {}
