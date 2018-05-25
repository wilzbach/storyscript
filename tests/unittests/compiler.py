# -*- coding: utf-8 -*-
import json
import re

from lark.lexer import Token

from pytest import fixture, mark

from storyscript.compiler import Compiler
from storyscript.parser import Tree
from storyscript.version import version


@fixture
def compiler():
    return Compiler()


@fixture
def tree(magic):
    return magic()


def test_compiler_init(compiler):
    assert compiler.lines == {}


def test_compiler_sorted_lines(compiler):
    compiler.lines = {'1': '1', '2': '2'}
    assert compiler.sorted_lines() == ['1', '2']


def test_compiler_last_line(patch, compiler):
    patch.object(Compiler, 'sorted_lines')
    compiler.lines = {'1': '1'}
    assert compiler.last_line() == compiler.sorted_lines()[-1]


def test_compiler_last_line_no_lines(compiler):
    assert compiler.last_line() is None


def test_compiler_set_next_line(patch, compiler):
    patch.object(Compiler, 'last_line', return_value='1')
    compiler.lines['1'] = {}
    compiler.set_next_line('2')
    assert compiler.lines['1']['next'] == '2'


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


def test_compiler_add_line(compiler):
    expected = {'1': {'method': 'method', 'ln': '1', 'output': None,
                      'container': None, 'enter': None, 'exit': None,
                      'args': None}}
    compiler.add_line('method', '1')
    assert compiler.lines == expected


@mark.parametrize('keywords', ['container', 'args', 'enter', 'exit'])
def test_compiler_add_line_keywords(compiler, keywords):
    compiler.add_line('method', '1', **{keywords: keywords})
    assert compiler.lines['1'][keywords] == keywords


def test_compiler_assignments(patch, compiler, tree):
    patch.many(Compiler, ['add_line', 'path', 'values', 'set_next_line'])
    compiler.assignments(tree)
    compiler.set_next_line.assert_called_with(tree.line())
    tree.node.assert_called_with('path')
    tree.child.assert_called_with(2)
    compiler.path.assert_called_with(tree.node('path'))
    compiler.values.assert_called_with(tree.child())
    args = [compiler.path(), compiler.values()]
    compiler.add_line.assert_called_with('set', tree.line(), args=args)


def test_compiler_next(patch, compiler, tree):
    patch.many(Compiler, ['file', 'base'])
    result = compiler.next(tree)
    tree.child.assert_called_with(1)
    compiler.file.assert_called_with(tree.child())
    args = [compiler.file()]
    compiler.base.assert_called_with('next', tree.line(), args=args)
    assert result == compiler.base()


def test_compiler_command(patch, compiler, tree):
    """
    Ensures that command trees can be compiled
    """
    patch.many(Compiler, ['base', 'set_next_line'])
    result = compiler.command(tree)
    compiler.set_next_line.assert_called_with(tree.line())
    container = tree.child().child().value
    compiler.base.assert_called_with('run', tree.line(), container=container)
    assert result == compiler.base()


def test_compiler_if_block(patch, compiler):
    patch.many(Compiler, ['base', 'path', 'subtrees', 'set_next_line'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', [])])
    result = compiler.if_block(tree)
    compiler.set_next_line.assert_called_with(tree.line())
    compiler.path.assert_called_with(tree.node('if_statement'))
    nested_block = tree.node('nested_block')
    args = [compiler.path()]
    compiler.base.assert_called_with('if', tree.line(), args=args,
                                     enter=nested_block.line())
    compiler.subtrees.assert_called_with(nested_block)
    assert result == {**compiler.base(), **compiler.subtrees()}


def test_compiler_if_block_with_elseif(patch, compiler):
    patch.many(Compiler, ['base', 'path', 'subtrees', 'set_next_line'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', []),
                             Tree('elseif_block', [])])
    compiler.if_block(tree)
    compiler.subtrees.assert_called_with(tree.node('nested_block'),
                                         tree.node('elseif_block'))


def test_compiler_if_block_with_else(patch, compiler):
    patch.many(Compiler, ['base', 'path', 'subtrees', 'set_next_line'])
    tree = Tree('if_block', [Tree('if_statement', []),
                             Tree('nested_block', []),
                             Tree('else_block', [])])
    compiler.if_block(tree)
    compiler.subtrees.assert_called_with(tree.node('nested_block'),
                                         tree.node('else_block'))


def test_compiler_elseif_block(patch, compiler, tree):
    patch.many(Compiler, ['base', 'path', 'subtree', 'set_next_line'])
    result = compiler.elseif_block(tree)
    compiler.set_next_line.assert_called_with(tree.line())
    assert tree.node.call_count == 2
    compiler.path.assert_called_with(tree.node())
    args = [compiler.path()]
    compiler.base.assert_called_with('elif', tree.line(), args=args,
                                     enter=tree.node().line())
    compiler.subtree.assert_called_with(tree.node())
    assert result == {**compiler.base(), **compiler.subtree()}


def test_compiler_else_block(patch, compiler, tree):
    patch.many(Compiler, ['base', 'path', 'subtree', 'set_next_line'])
    result = compiler.else_block(tree)
    compiler.set_next_line.assert_called_with(tree.line())
    compiler.base.assert_called_with('else', tree.line(),
                                     enter=tree.node().line())
    compiler.subtree.assert_called_with(tree.node())
    assert result == {**compiler.base(), **compiler.subtree()}


def test_compiler_for_block(patch, compiler, tree):
    patch.many(Compiler, ['base', 'path', 'subtree', 'set_next_line'])
    result = compiler.for_block(tree)
    compiler.path.assert_called_with(tree.node())
    args = [tree.node().child(0).value, Compiler.path()]
    compiler.set_next_line.assert_called_with(tree.line())
    compiler.base.assert_called_with('for', tree.line(), args=args,
                                     enter=tree.node().line())
    compiler.subtree.assert_called_with(tree.node())
    assert result == {**compiler.base(), **compiler.subtree()}


def test_compiler_wait_block(patch, compiler, tree):
    patch.many(Compiler, ['base', 'subtree', 'path', 'set_next_line'])
    result = compiler.wait_block(tree)
    compiler.path.assert_called_with(tree.node().child(1))
    args = [Compiler.path()]
    compiler.base.assert_called_with('wait', tree.line(), args=args,
                                     enter=tree.node().line())
    compiler.set_next_line.assert_called_with(tree.line())
    compiler.subtree.assert_called_with(tree.node())
    assert result == {**compiler.base(), **compiler.subtree()}


@mark.parametrize('method_name', [
    'command', 'next', 'assignments', 'if_block', 'elseif_block', 'else_block',
    'for_block', 'wait_block'
])
def test_compiler_subtree(patch, compiler, method_name):
    patch.object(Compiler, method_name)
    tree = Tree(method_name, [])
    result = compiler.subtree(tree)
    method = getattr(compiler, method_name)
    method.assert_called_with(tree)
    assert result == method()


def test_compiler_subtrees(patch, compiler, tree):
    patch.object(Compiler, 'subtree', return_value={'tree': 'sub'})
    result = compiler.subtrees(tree, tree)
    compiler.subtree.assert_called_with(tree)
    assert result == {**compiler.subtree()}


def test_compiler_parse_tree(compiler, patch):
    """
    Ensures that the parse_tree method can parse a complete tree
    """
    patch.object(Compiler, 'subtree', return_value={'1': 'subtree'})
    tree = Tree('start', [Tree('command', ['token'])])
    result = compiler.parse_tree(tree)
    assert compiler.lines == {'1': 'subtree'}
    assert result == compiler.lines


def test_compiler_compile(patch):
    patch.object(json, 'dumps')
    patch.object(Compiler, 'parse_tree')
    patch.init(Compiler)
    result = Compiler.compile('tree')
    assert Compiler.__init__.call_count == 1
    Compiler.parse_tree.assert_called_with('tree')
    dictionary = {'script': Compiler.parse_tree(), 'version': version}
    json.dumps.assert_called_with(dictionary)
    assert result == json.dumps()
