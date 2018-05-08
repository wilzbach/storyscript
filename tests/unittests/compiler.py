# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.compiler import Compiler
from storyscript.parser import Tree
from storyscript.version import version


def test_compiler_path():
    tree = Tree('path', [Token('WORD', 'var')])
    assert Compiler.path(tree) == {'$OBJECT': 'path', 'paths': ['var']}


def test_compiler_assignment():
def test_compiler_string():
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"blue"')])
    assert Compiler.string(tree) == {'$OBJECT': 'string', 'string': 'blue'}


def test_compiler_line():
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', line=1)])])
    assert Compiler.line(tree) == '1'


    tree = Tree('assignments', [Tree('path', [Token('WORD', 'color', line=1)]),
                Token('EQUALS', '='), Tree('values', [Tree('string',
                [Token('DOUBLE_QUOTED', '"blue"')])])])
    expected = {'method': 'set', 'ln': '1', 'output': None, 'container': None,
                'enter': None, 'exit': None, 'args': [{'$OBJECT': 'path',
                'paths': ['color']}, {'$OBJECT': 'string', 'string': 'blue'}]}
    assert Compiler.assignment(tree) == expected


def test_compiler_command():
    """
    Ensures that command trees can be compiled
    """
    tree = Tree('command', [Token('WORD', 'alpine', line=1)])
    expected = {'method': 'run', 'ln': 1, 'container': 'alpine', 'args': None,
                'output': None, 'enter': None, 'exit': None}
    assert Compiler.command(tree) == expected


def test_compiler_compile(patch):
    patch.object(Compiler, 'parse_tree')
    result = Compiler.compile('tree')
    Compiler.parse_tree.assert_called_with('tree')
    assert result == {'script': Compiler.parse_tree(), 'version': version}


def test_compiler_parse_tree():
    assert Compiler.parse_tree('tree') == {}
