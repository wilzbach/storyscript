# -*- coding: utf-8 -*-
import random
import uuid

from lark.lexer import Token

from pytest import fixture

from storyscript.compiler import FakeTree
from storyscript.parser import Tree


@fixture
def fake_tree(block):
    return FakeTree(block)


def test_faketree_init(block, fake_tree):
    assert fake_tree.block == block
    assert fake_tree.original_line == block.line()


def test_faketree_line(patch, magic, tree):
    """
    Ensures line can create a fake line number
    """
    patch.object(random, 'uniform')
    result = FakeTree.line('1')
    random.uniform.assert_called_with(0, 1)
    assert result == str(random.uniform())


def test_faketree_path(patch):
    patch.object(uuid, 'uuid4')
    result = FakeTree.path(1)
    name = '${}'.format(uuid.uuid4().hex[:8])
    assert result == Tree('path', [Token('NAME', name, line=1)])


def test_faketree_assignment(patch, tree):
    patch.many(FakeTree, ['path', 'line'])
    result = FakeTree.assignment('1', tree)
    FakeTree.line.assert_called_with('1')
    FakeTree.path.assert_called_with(FakeTree.line())
    assert tree.child().child().line == FakeTree.line()
    assert result.children[0] == FakeTree.path()
    expected = Tree('assignment_fragment', [Token('EQUALS', '='), tree])
    assert result.children[1] == expected
