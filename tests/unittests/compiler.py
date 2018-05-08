# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import mark

from storyscript.compiler import Compiler
from storyscript.parser import Tree
from storyscript.version import version


def test_compiler_path():
    tree = Tree('path', [Token('WORD', 'var')])
    assert Compiler.path(tree) == {'$OBJECT': 'path', 'paths': ['var']}


def test_compiler_number():
    tree = Tree('number', [Token('INT', '1')])
    assert Compiler.number(tree) == 1


def test_compiler_string():
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"blue"')])
    assert Compiler.string(tree) == {'$OBJECT': 'string', 'string': 'blue'}


def test_compiler_boolean():
    tree = Tree('boolean', [Token('TRUE', 'true')])
    assert Compiler.boolean(tree) is True


def test_compiler_boolean_false():
    tree = Tree('boolean', [Token('FALSE', 'false')])
    assert Compiler.boolean(tree) is False


def test_compiler_file():
    token = Token('FILEPATH', '`path`')
    assert Compiler.file(token) == {'$OBJECT': 'file', 'string': 'path'}


def test_compiler_list(patch):
    patch.object(Compiler, 'string')
    value = Tree('string', [Token('DOUBLE_QUOTED', '"color"')])
    tree = Tree('list', [Tree('values', [value])])
    result = Compiler.list(tree)
    Compiler.string.assert_called_with(value)
    expected = {'$OBJECT': 'list', 'items': [Compiler.string()]}
    assert result == expected


def test_compiler_object(patch):
    patch.many(Compiler, ['string', 'number'])
    tree = Tree('objects', [Tree('key_value', [Tree('string', 'key'),
                Tree('values', [Tree('number', ['value'])])])])
    result = Compiler.objects(tree)
    Compiler.string.assert_called_with(Tree('string', 'key'))
    Compiler.number.assert_called_with(Tree('number', ['value']))
    expected = {'$OBJECT': 'dict', 'items': [[Compiler.string(),
                Compiler.number()]]}
    assert result == expected


def test_compiler_line():
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', line=1)])])
    assert Compiler.line(tree) == '1'


def test_compiler_assignments(patch):
    patch.many(Compiler, ['path', 'string', 'line'])
    tree = Tree('assignments', [Tree('path', ['path']), Token('EQUALS', '='),
                                Tree('values', [Tree('string', ['string'])])])
    result = Compiler.assignments(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.path.assert_called_with(Tree('path', ['path']))
    Compiler.string.assert_called_with(Tree('string', ['string']))
    expected = {'method': 'set', 'ln': Compiler.line(), 'output': None,
                'container': None, 'enter': None, 'exit': None,
                'args': [Compiler.path(), Compiler.string()]}
    assert result == expected


def test_compiler_next(patch):
    patch.many(Compiler, ['file', 'line'])
    tree = Tree('next_statement', [Token('NEXT', 'next', line=1),
                                   Token('FILEPATH', '`path`')])
    result = Compiler.next_statement(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.file.assert_called_with(tree.children[1])
    expected = {'method': 'next', 'ln': Compiler.line(), 'output': None,
                'args': [Compiler.file()], 'container': None, 'enter': None,
                'exit': None}
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


@mark.parametrize('method_name', ['command', 'next_statement', 'assignments'])
def test_parse_subtree(patch, method_name):
    patch.many(Compiler, ['line', method_name])
    tree = Tree(method_name, [])
    result = Compiler.parse_subtree(tree)
    Compiler.line.assert_called_with(tree)
    method = getattr(Compiler, method_name)
    method.assert_called_with(tree)
    assert result == {Compiler.line(): method()}


def test_compiler_parse_tree(patch):
    """
    Ensures that the parse_tree method can parse a complete tree
    """
    patch.object(Compiler, 'parse_subtree', return_value={'1': 'subtree'})
    subtree = Tree('command', ['token'])
    tree = Tree('start', [Tree('block', [Tree('line', [subtree])])])
    result = Compiler.parse_tree(tree)
    assert result == {'1': 'subtree'}
