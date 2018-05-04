# -*- coding: utf-8 -*-
from lark.tree import Tree as LarkTree

from pytest import fixture

from storyscript.parser import Tree


@fixture
def tree():
    return Tree('data', [])


def test_tree():
    assert issubclass(Tree, LarkTree)


def test_tree_json(tree):
    assert tree.json() == 'json'
