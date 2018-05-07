# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from pytest import fixture, mark

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


def test_tree_walk():
    inner_tree = Tree('inner', [])
    tree = Tree('rule', [inner_tree])
    result = Tree.walk(tree, 'inner')
    assert result == inner_tree


def test_tree_node():
    inner_tree = Tree('inner', [Token('WORD', 'word')])
    tree = Tree('rule', [inner_tree])
    assert tree.node('inner') == inner_tree


def test_tree_json(tree):
    assert tree.json() == {'version': version, 'script': {}}


@mark.parametrize('rule', ['command', 'if_statement'])
def test_tree_json_rule(patch, tree, rule):
    patch.object(Tree, rule)
    tree.children = [Tree(rule, [])]
    tree.json()
    assert getattr(Tree, rule).call_count == 1
