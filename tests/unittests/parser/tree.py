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


def test_tree_json(tree):
    assert tree.json() == {}


def test_tree_json_child_tokens(magic, tree):
    tree.children = [Token('type', 'value')]
    assert tree.json() == {'type': 'value'}


def test_tree_json_child_tree(magic, tree):
    tree.children = [Tree('name', [Token('type', 'value')])]
    assert tree.json() == {'name': {'type': 'value'}}


def test_tree_json_child_tree_start(magic, tree):
    tree.children = [Tree('start', [])]
    assert tree.json() == {'version': version, 'script': {}}
