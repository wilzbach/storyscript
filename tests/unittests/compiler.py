# -*- coding: utf-8 -*-
import json
import re

from lark.lexer import Token

from pytest import fixture, mark

from storyscript.compiler import Compiler
from storyscript.parser import Tree
from storyscript.version import version


@fixture
def tree(magic):
    return magic()


def test_compiler_path():
    tree = Tree('path', [Token('WORD', 'var')])
    assert Compiler.path(tree) == {'$OBJECT': 'path', 'paths': ['var']}


def test_compiler_number():
    tree = Tree('number', [Token('INT', '1')])
    assert Compiler.number(tree) == 1


def test_compiler_string():
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"blue"')])
    assert Compiler.string(tree) == {'$OBJECT': 'string', 'string': 'blue'}


def test_compiler_string_templating(patch):
    patch.object(Compiler, 'path')
    patch.object(re, 'findall', return_value=['color'])
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"{{color}}"')])
    result = Compiler.string(tree)
    re.findall.assert_called_with(r'{{([^}]*)}}', '{{color}}')
    Compiler.path.assert_called_with(Tree('path', [Token('WORD', 'color')]))
    assert result['string'] == '{}'
    assert result['values'] == [Compiler.path()]


def test_compiler_boolean():
    tree = Tree('boolean', [Token('TRUE', 'true')])
    assert Compiler.boolean(tree) is True


def test_compiler_boolean_false():
    tree = Tree('boolean', [Token('FALSE', 'false')])
    assert Compiler.boolean(tree) is False


def test_compiler_file():
    token = Token('FILEPATH', '`path`')
    assert Compiler.file(token) == {'$OBJECT': 'file', 'string': 'path'}


def test_compiler_list(patch, tree):
    patch.object(Compiler, 'values')
    tree.children = ['value']
    result = Compiler.list(tree)
    Compiler.values.assert_called_with('value')
    assert result == {'$OBJECT': 'list', 'items': [Compiler.values()]}


def test_compiler_objects(patch, magic, tree):
    patch.many(Compiler, ['string', 'values'])
    subtree = magic()
    tree.children = [subtree]
    result = Compiler.objects(tree)
    subtree.node.assert_called_with('string')
    subtree.child.assert_called_with(1)
    Compiler.string.assert_called_with(subtree.node())
    Compiler.values.assert_called_with(subtree.child())
    expected = {'$OBJECT': 'dict', 'items': [[Compiler.string(),
                                              Compiler.values()]]}
    assert result == expected


@mark.parametrize('value_type', [
    'string', 'boolean', 'list', 'number', 'objects'
])
def test_compiler_values(patch, magic, value_type):
    patch.object(Compiler, value_type)
    item = magic(data=value_type)
    tree = magic(child=lambda x: item)
    result = Compiler.values(tree)
    getattr(Compiler, value_type).assert_called_with(item)
    assert result == getattr(Compiler, value_type)()


def test_compiler_values_filepath(patch, magic):
    patch.object(Compiler, 'file')
    item = magic(type='FILEPATH')
    tree = magic(child=lambda x: item)
    result = Compiler.values(tree)
    Compiler.file.assert_called_with(item)
    assert result == Compiler.file()


def test_compiler_enter(patch):
    patch.object(Compiler, 'line')
    result = Compiler.enter({}, 'nested_block')
    Compiler.line.assert_called_with('nested_block')
    assert result == {'enter': Compiler.line()}


def test_compiler_assignments(patch, tree):
    patch.many(Compiler, ['path', 'values', 'line'])
    result = Compiler.assignments(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.path.assert_called_with(tree.node('path'))
    tree.child.assert_called_with(2)
    Compiler.values.assert_called_with(tree.child())
    expected = {'method': 'set', 'ln': Compiler.line(), 'output': None,
                'container': None, 'enter': None, 'exit': None,
                'args': [Compiler.path(), Compiler.values()]}
    assert result == {Compiler.line(): expected}


def test_compiler_next(patch):
    patch.many(Compiler, ['file', 'line'])
    tree = Tree('next', [Token('NEXT', 'next'), Token('FILEPATH', '`path`')])
    result = Compiler.next(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.file.assert_called_with(tree.children[1])
    expected = {'method': 'next', 'ln': Compiler.line(), 'output': None,
                'args': [Compiler.file()], 'container': None, 'enter': None,
                'exit': None}
    assert result == {Compiler.line(): expected}


def test_compiler_command(magic, patch):
    """
    Ensures that command trees can be compiled
    """
    patch.object(Compiler, 'line')
    tree = magic()
    result = Compiler.command(tree)
    Compiler.line.assert_called_with(tree)
    expected = {'method': 'run', 'ln': Compiler.line(), 'args': None,
                'container': tree.child(0).child(0).value, 'output': None,
                'enter': None, 'exit': None}
    assert result == {Compiler.line(): expected}


def test_compiler_if_block(magic, patch):
    patch.many(Compiler, ['line', 'path', 'subtrees'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', [])])
    result = Compiler.if_block(tree)
    assert Compiler.line.call_count == 2
    Compiler.path.assert_called_with(tree.node('if_statement'))
    Compiler.subtrees.assert_called_with(tree.node('nested_block'))
    expected = {'method': 'if', 'ln': Compiler.line(), 'container': None,
                'output': None, 'args': [Compiler.path()], 'enter': Compiler.line()}
    assert result == {**{Compiler.line(): expected}, **Compiler.subtrees()}


def test_compiler_if_block_with_elseif(magic, patch):
    patch.many(Compiler, ['line', 'path', 'subtrees'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', []),
                             Tree('elseif_block', [])])
    Compiler.if_block(tree)
    Compiler.subtrees.assert_called_with(tree.node('nested_block'),
                                         tree.node('elseif_block'))


def test_compiler_elseif_block(patch, tree):
    patch.many(Compiler, ['line', 'path', 'subtree'])
    result = Compiler.elseif_block(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.path.assert_called_with(tree.node('elseif_statement'))
    Compiler.subtree.assert_called_with(tree.node('nested_block'))
    expected = {'method': 'elif', 'ln': Compiler.line(), 'output': None,
                'container': None, 'args': [Compiler.path()]}
    assert result == {**{Compiler.line(): expected}, **Compiler.subtree()}


def test_compiler_for_block(patch, magic):
    patch.many(Compiler, ['line', 'enter', 'path', 'subtree'])
    tree = magic()
    result = Compiler.for_block(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.path.assert_called_with(tree.node('for_statement'))
    line = {'method': 'for', 'ln': Compiler.line(), 'output': None,
            'container': None, 'args': [
                tree.node('for_statement').child(0).value, Compiler.path()]}
    Compiler.enter.assert_called_with(line, tree.node())
    Compiler.subtree.assert_called_with(tree.node())
    assert result == {**{Compiler.line(): Compiler.enter()},
                      **Compiler.subtree()}


def test_compiler_wait_block(patch, magic):
    patch.many(Compiler, ['line', 'subtree', 'path'])
    tree = magic()
    result = Compiler.wait_block(tree)
    Compiler.line.assert_called_with(tree)
    Compiler.subtree.assert_called_with(tree.node('nested_block'))
    Compiler.path.assert_called_with(tree.node('wait_statement').child(1))
    expected = {'method': 'wait', 'ln': Compiler.line(), 'output': None,
                'container': None, 'args': [Compiler.path()]}
    assert result == {**{Compiler.line(): expected}, **Compiler.subtree()}


@mark.parametrize('method_name', [
    'command', 'next', 'assignments', 'if_block', 'elseif_block', 'for_block',
    'wait_block'
])
def test_subtree(patch, method_name):
    patch.object(Compiler, method_name)
    tree = Tree(method_name, [])
    result = Compiler.subtree(tree)
    method = getattr(Compiler, method_name)
    method.assert_called_with(tree)
    assert result == method()


def test_compiler_subtrees(patch, tree):
    patch.object(Compiler, 'subtree', return_value={'tree': 'sub'})
    result = Compiler.subtrees(tree, tree)
    Compiler.subtree.assert_called_with(tree)
    assert result == {**Compiler.subtree()}


def test_compiler_parse_tree(patch):
    """
    Ensures that the parse_tree method can parse a complete tree
    """
    patch.object(Compiler, 'subtree', return_value={'1': 'subtree'})
    subtree = Tree('command', ['token'])
    tree = Tree('start', [Tree('block', [Tree('line', [subtree])])])
    result = Compiler.parse_tree(tree)
    assert result == {'1': 'subtree'}


def test_compiler_compile(patch):
    patch.object(json, 'dumps')
    patch.object(Compiler, 'parse_tree')
    result = Compiler.compile('tree')
    Compiler.parse_tree.assert_called_with('tree')
    dictionary = {'script': Compiler.parse_tree(), 'version': version}
    json.dumps.assert_called_with(dictionary)
    assert result == json.dumps()
