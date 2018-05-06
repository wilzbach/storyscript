# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from pytest import fixture

from storyscript.parser import Tree
from storyscript.version import version


@fixture
def tree():
    return Tree('data', [])


@fixture
def dictionary():
    return {'script': {}}


def test_tree():
    assert issubclass(Tree, LarkTree)


def test_tree_command(dictionary):
    tree = Tree('command', [Token('RUN', 'run', line='1'),
                Token('WORD', 'container')])
    tree.command(dictionary)
    expected = {'method': 'run', 'ln': '1', 'container': 'container',
                'args': [], 'output': None, 'enter': None, 'exit': None}
    assert dictionary['script'] == {'1': expected}


def test_tree_if(dictionary):
    tree = Tree('if_statement', [Token('IF', 'if', line='1'),
                Token('WORD', 'word')])
    tree.if_statement(dictionary)
    expected = {'method': 'if', 'ln': '1', 'args': [], 'container': None,
                'output': None, 'enter': None, 'exit': None}
    assert dictionary['script'] == {'1': expected}


def test_tree_json(tree):
    assert tree.json() == {'version': version, 'script': {}}


def test_tree_json_child_tokens(magic, tree):
    tree.children = [Token('type', 'value')]
    assert tree.json() == {'type': 'value', 'script': {}, 'version': version}


def test_tree_json_command(patch, tree):
    patch.object(Tree, 'command')
    tree.children = [Tree('command', [])]
    tree.json()
    assert Tree.command.call_count == 1


def test_tree_json_command(patch, tree):
    patch.object(Tree, 'if_statement')
    tree.children = [Tree('if_statement', [])]
    tree.json()
    assert Tree.if_statement.call_count == 1
