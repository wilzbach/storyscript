# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from pytest import fixture

from storyscript.parser import Tree
from storyscript.version import version


@fixture
def tree():
    return Tree('data', [])


def test_tree():
    assert issubclass(Tree, LarkTree)


def test_tree_command():
    tree = Tree('command', [Token('RUN', 'run', line='1'),
           Token('WORD', 'container')])
    dictionary = {'script': {}}
    tree.command(dictionary)
    expected = {'method': 'run', 'ln': '1', 'container': 'container',
                'args': [], 'output': None, 'enter': None, 'exit': None}
    assert dictionary['script'] == {'1': expected}


def test_tree_json(tree):
    assert tree.json() == {'script': {}}


def test_tree_json_child_tokens(magic, tree):
    tree.children = [Token('type', 'value')]
    assert tree.json() == {'type': 'value', 'script': {}}


def test_tree_json_tree_start(magic, tree):
    tree.children = [Tree('start', [])]
    assert tree.json() == {'version': version, 'script': {}}


def test_tree_json_command(patch, tree):
    patch.object(Tree, 'command')
    tree.children = [Tree('command', [])]
    result = tree.json()
    assert Tree.command.call_count == 1
