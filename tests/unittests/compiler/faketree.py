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
    assert fake_tree.new_lines == []


def test_faketree_line(patch, fake_tree):
    """
    Ensures FakeTree.line can create a fake line number
    """
    patch.object(random, 'uniform')
    result = fake_tree.line()
    random.uniform.assert_called_with(0, 1)
    assert fake_tree.new_lines == [random.uniform()]
    assert result == str(random.uniform())


def test_faketree_line_successive(patch, fake_tree):
    """
    Ensures FakeTree.line takes into account FakeTree.new_lines
    """
    patch.object(random, 'uniform')
    fake_tree.new_lines = [0.2]
    fake_tree.line()
    random.uniform.assert_called_with(0.2, 1)


def test_faketree_path(patch):
    patch.object(uuid, 'uuid4')
    result = FakeTree.path(1)
    name = '${}'.format(uuid.uuid4().hex[:8])
    assert result == Tree('path', [Token('NAME', name, line=1)])


def test_faketree_assignment(patch, tree, fake_tree):
    patch.many(FakeTree, ['path', 'line'])
    result = fake_tree.assignment(tree)
    FakeTree.path.assert_called_with(FakeTree.line())
    assert tree.child().child().line == FakeTree.line()
    assert result.children[0] == FakeTree.path()
    expected = Tree('assignment_fragment', [Token('EQUALS', '='), tree])
    assert result.children[1] == expected


def test_faketree_add_assignment(patch, fake_tree):
    patch.object(FakeTree, 'assignment')
    result = fake_tree.add_assignment('value')
    FakeTree.assignment.assert_called_with('value')
    fake_tree.block.insert.assert_called_with(FakeTree.assignment())
    assert result == FakeTree.assignment()
