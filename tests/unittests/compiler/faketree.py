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
    random.uniform.assert_called_with(0, 0.2)


def test_faketree_get_line(patch, tree, fake_tree):
    """
    Ensures FakeTree.get_line can get a new line
    """
    patch.object(FakeTree, 'line')
    result = fake_tree.get_line(tree)
    assert result == FakeTree.line()


def test_faketree_get_line_existing(tree, fake_tree):
    """
    Ensures FakeTree.get_line gets the existing line when appropriate.
    """
    fake_tree.new_lines = [0.1]
    tree.line.return_value = '0.1'
    assert fake_tree.get_line(tree) == tree.line()


def test_faketree_path(patch, fake_tree):
    patch.object(uuid, 'uuid4')
    patch.object(FakeTree, 'line')
    result = fake_tree.path()
    name = '${}'.format(uuid.uuid4().hex[:8])
    assert result == Tree('path', [Token('NAME', name, line=FakeTree.line())])


def test_faketree_path_name(patch, fake_tree):
    patch.object(FakeTree, 'line')
    result = fake_tree.path(name='x')
    assert result.child(0).value == 'x'


def test_faketree_path_line(fake_tree):
    assert fake_tree.path(line=1).child(0).line == 1


def test_faketree_number(patch, fake_tree):
    """
    Ensures FakeTree.number can create a number
    """
    patch.object(FakeTree, 'line')
    result = fake_tree.number(1)
    assert result == Tree('values', [Tree('number', [Token('INT', 1)])])
    assert result.number.child(0).line == FakeTree.line()


def test_faketree_expression(patch, tree, fake_tree):
    """
    Ensures FakeTree.expression can create an expression
    """
    patch.object(FakeTree, 'number')
    result = fake_tree.expression(tree, '+', 'rhs')
    FakeTree.number.assert_called_with(tree.number.child())
    assert result.data == 'expression'
    fragment = Tree('expression_fragment', ['+', 'rhs'])
    assert result.children == [FakeTree.number(), fragment]


def test_faketree_expression_path(patch, tree, fake_tree):
    """
    Ensures FakeTree.expression can create an expression with a path as left
    value
    """
    patch.object(FakeTree, 'path')
    tree.number = None
    result = fake_tree.expression(tree, '+', 'rhs')
    FakeTree.path.assert_called_with(name=tree.child())
    assert result.children[0] == FakeTree.path()


def test_faketree_assignment(patch, tree, fake_tree):
    patch.many(FakeTree, ['path', 'get_line'])
    result = fake_tree.assignment(tree)
    FakeTree.get_line.assert_called_with(tree)
    line = FakeTree.get_line()
    FakeTree.path.assert_called_with(line=line)
    assert tree.child().child().line == line
    assert result.children[0] == FakeTree.path()
    subtree = [Token('EQUALS', '=', line=line), tree]
    expected = Tree('assignment_fragment', subtree)
    assert result.children[1] == expected


def test_faketree_add_assignment(patch, fake_tree):
    patch.object(FakeTree, 'assignment')
    result = fake_tree.add_assignment('value')
    FakeTree.assignment.assert_called_with('value')
    fake_tree.block.insert.assert_called_with(FakeTree.assignment())
    assert result == FakeTree.assignment()
