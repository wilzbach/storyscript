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


def test_compiler_base():
    expected = {'1': {'method': 'method', 'ln': '1', 'output': None,
                      'container': None, 'enter': None, 'exit': None,
                      'args': None}}
    assert Compiler.base('method', '1') == expected


@mark.parametrize('keywords', ['container', 'args', 'enter', 'exit'])
def test_compiler_base_keywords(keywords):
    result = Compiler.base('method', '1', **{keywords: keywords})
    assert result['1'][keywords] == keywords


def test_compiler_enter(tree):
    result = Compiler.enter({}, tree)
    assert result == {'enter': tree.line()}


def test_compiler_assignments(patch, tree):
    patch.many(Compiler, ['base', 'path', 'values'])
    result = Compiler.assignments(tree)
    tree.node.assert_called_with('path')
    tree.child.assert_called_with(2)
    Compiler.path.assert_called_with(tree.node('path'))
    Compiler.values.assert_called_with(tree.child())
    args = [Compiler.path(), Compiler.values()]
    Compiler.base.assert_called_with('set', tree.line(), args=args)
    assert result == Compiler.base()


def test_compiler_next(patch, tree):
    patch.many(Compiler, ['file', 'base'])
    result = Compiler.next(tree)
    tree.child.assert_called_with(1)
    Compiler.file.assert_called_with(tree.child())
    args = [Compiler.file()]
    Compiler.base.assert_called_with('next', tree.line(), args=args)
    assert result == Compiler.base()


def test_compiler_command(patch, tree):
    """
    Ensures that command trees can be compiled
    """
    patch.object(Compiler, 'base')
    result = Compiler.command(tree)
    container = tree.child().child().value
    Compiler.base.assert_called_with('run', tree.line(), container=container)
    assert result == Compiler.base()


def test_compiler_if_block(patch):
    patch.many(Compiler, ['base', 'path', 'subtrees'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', [])])
    result = Compiler.if_block(tree)
    Compiler.path.assert_called_with(tree.node('if_statement'))
    nested_block = tree.node('nested_block')
    args = [Compiler.path()]
    Compiler.base.assert_called_with('if', tree.line(), args=args,
                                     enter=nested_block.line())
    Compiler.subtrees.assert_called_with(nested_block)
    assert result == {**Compiler.base(), **Compiler.subtrees()}


def test_compiler_if_block_with_elseif(patch):
    patch.many(Compiler, ['base', 'path', 'subtrees'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', []),
                             Tree('elseif_block', [])])
    Compiler.if_block(tree)
    Compiler.subtrees.assert_called_with(tree.node('nested_block'),
                                         tree.node('elseif_block'))


def test_compiler_elseif_block(patch, tree):
    patch.many(Compiler, ['base', 'path', 'subtree'])
    result = Compiler.elseif_block(tree)
    assert tree.node.call_count == 2
    Compiler.path.assert_called_with(tree.node())
    args = [Compiler.path()]
    Compiler.base.assert_called_with('elif', tree.line(), args=args,
                                     enter=tree.node().line())
    Compiler.subtree.assert_called_with(tree.node())
    assert result == {** Compiler.base(), **Compiler.subtree()}


def test_compiler_for_block(patch, magic):
    patch.many(Compiler, ['enter', 'path', 'subtree'])
    tree = magic()
    result = Compiler.for_block(tree)
    Compiler.path.assert_called_with(tree.node('for_statement'))
    line = {'method': 'for', 'ln': tree.line(), 'output': None,
            'container': None, 'args': [
                tree.node('for_statement').child(0).value, Compiler.path()]}
    Compiler.enter.assert_called_with(line, tree.node())
    Compiler.subtree.assert_called_with(tree.node())
    assert result == {**{tree.line(): Compiler.enter()}, **Compiler.subtree()}


def test_compiler_wait_block(patch, magic):
    patch.many(Compiler, ['subtree', 'path'])
    tree = magic()
    result = Compiler.wait_block(tree)
    Compiler.subtree.assert_called_with(tree.node('nested_block'))
    Compiler.path.assert_called_with(tree.node('wait_statement').child(1))
    expected = {'method': 'wait', 'ln': tree.line(), 'output': None,
                'container': None, 'args': [Compiler.path()]}
    assert result == {**{tree.line(): expected}, **Compiler.subtree()}


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
