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


def test_tree_walk():
    inner_tree = Tree('inner', [])
    tree = Tree('rule', [inner_tree])
    result = Tree.walk(tree, 'inner')
    assert result == inner_tree


def test_tree_node(patch):
    patch.object(Tree, 'walk')
    tree = Tree('rule', [])
    result = tree.node('inner')
    Tree.walk.assert_called_with(tree, 'inner')
    assert result == Tree.walk()


def test_tree_child():
    tree = Tree('rule', ['child'])
    assert tree.child(0) == 'child'


def test_tree_line():
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', line=1)])])
    assert tree.line() == '1'
