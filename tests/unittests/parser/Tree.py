# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from pytest import fixture, mark

from storyscript.parser import Tree


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


def test_tree_walk_token():
    """
    Ensures that encountered tokens are skipped
    """
    inner_tree = Tree('inner', [])
    tree = Tree('rule', [Token('test', 'test'), inner_tree])
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


def test_tree_child_overflow():
    tree = Tree('rule', ['child'])
    assert tree.child(1) is None


def test_tree_line():
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', line=1)])])
    assert tree.line() == '1'


def test_tree_column():
    """
    Ensures Tree.column can find the column of a tree
    """
    tree = Tree('outer', [Tree('path', [Token('WORD', 'word', column=1)])])
    assert tree.column() == '1'


def test_tree_end_column():
    """
    Ensures Tree.end_column can find the end column of a tree.
    """
    token = Token('WORD', 'word')
    token.end_column = 1
    tree = Tree('outer', [Tree('path', [token])])
    assert tree.end_column() == '1'


def test_tree_insert():
    tree = Tree('tree', [])
    tree.insert('child')
    assert tree.children == ['child']


def test_tree_rename():
    """
    Ensures Tree.rename can rename the current tree
    """
    tree = Tree('tree', [])
    tree.rename('new')
    assert tree.data == 'new'


def test_tree_replace():
    tree = Tree('tree', ['old'])
    tree.replace(0, 'new')
    assert tree.children == ['new']


def test_tree_extract_path():
    tree = Tree('path', [Token('NAME', 'one')])
    assert tree.extract_path() == 'one'


def test_tree_extract_path_fragments():
    subtree = Tree('fragment', [Token('NAME', 'two')])
    tree = Tree('path', [Token('NAME', 'one'), subtree, subtree])
    assert tree.extract_path() == 'one.two.two'


def test_tree_attributes(patch):
    patch.object(Tree, 'node')
    tree = Tree('master', [])
    result = tree.branch
    Tree.node.assert_called_with('branch')
    assert result == Tree.node()


def test_tree_find():
    """
    Ensures Tree.find can find the correct subtree.
    """
    expected = Tree('assignment', ['x'])
    tree = Tree('start', [Tree('block', [Tree('line', [expected])])])
    assert tree.find('assignment') == [expected]


def test_tree_is_unary():
    """
    Ensures is_unary can find out whether an expression is unary
    """
    tree = Tree('expression', [Tree('any', [Tree('any', [1])])])
    assert tree.is_unary() is True


@mark.parametrize('tree', [
    Tree('any', []),
    Tree('expression', [1, 2]),
    Tree('expression', [Tree('any', [1, 2])]),
    Tree('expression', [Tree('any', [Tree('any', [1, 2])])])
])
def test_tree_is_unary_false(tree):
    """
    Ensures is_unary returns False when the tree is not an unary
    """
    assert tree.is_unary() is False


def test_tree_find_operator(magic):
    """
    Ensures find_operator can find the operator.
    """
    tree = Tree('any', [])
    tree.multiplication = magic()
    result = tree.find_operator()
    assert result == tree.multiplication.exponential.factor.child()


@mark.parametrize('tree', [
    Tree('any', [0, Token('t', 't')]),
    Tree('any', [Tree('multiplication', [0, Token('t', 't')])]),
    Tree('any', [Tree('multiplication', [
        Tree('exponential', [0, Token('t', 't')])
    ])])
])
def test_tree_find_operator_depths(tree):
    """
    Ensures find_operator can find operators at various depths
    """
    assert tree.find_operator() == Token('t', 't')
