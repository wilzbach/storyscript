# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.compiler import Compiler
from storyscript.parser import Tree
from storyscript.version import version


def test_compiler_path():
    tree = Tree('path', [Token('WORD', 'var')])
    assert Compiler.path(tree) == {'$OBJECT': 'path', 'paths': ['var']}


def test_compiler_string():
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"blue"')])
    assert Compiler.string(tree) == {'$OBJECT': 'string', 'string': 'blue'}


def test_compiler_line():
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', line=1)])])
    assert Compiler.line(tree) == '1'


def test_compiler_assignment(patch):
    patch.many(Compiler, ['path', 'string', 'line'])
    tree = Tree('assignments', [Tree('path', ['path']), Token('EQUALS', '='),
                                Tree('values', [Tree('string', ['string'])])])
    result = Compiler.assignment(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.path.assert_called_with(Tree('path', ['path']))
    Compiler.string.assert_called_with(Tree('string', ['string']))
    expected = {'method': 'set', 'ln': Compiler.line(), 'output': None,
                'container': None, 'enter': None, 'exit': None,
                'args': [Compiler.path(), Compiler.string()]}
    assert result == expected


def test_compiler_command(patch):
    """
    Ensures that command trees can be compiled
    """
    patch.object(Compiler, 'line')
    tree = Tree('command', [Token('WORD', 'alpine')])
    result = Compiler.command(tree)
    Compiler.line.assert_called_with(tree)
    expected = {'method': 'run', 'ln': Compiler.line(), 'container': 'alpine',
                'args': None, 'output': None, 'enter': None, 'exit': None}
    assert result == expected


def test_compiler_compile(patch):
    patch.object(Compiler, 'parse_tree')
    result = Compiler.compile('tree')
    Compiler.parse_tree.assert_called_with('tree')
    assert result == {'script': Compiler.parse_tree(), 'version': version}


def test_compiler_parse_tree():
    assert Compiler.parse_tree('tree') == {}
