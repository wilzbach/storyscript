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


def test_tree_walk_token():
    """
    Ensures that encountered tokens are skipped
    """
    inner_tree = Tree('inner', [])
    tree = Tree('rule', [Token('test', 'test'), inner_tree])
    result = Tree.walk(tree, 'inner')
    assert result == inner_tree


def test_tree_from_name():
    result = Tree.from_name('tree.name', None)
    assert result == Tree('tree', [Tree('name', None)])


def test_tree_from_value(patch):
    """
    Ensures Tree.from_value can handle nested trees
    """
    patch.object(Tree, 'from_dict')
    result = Tree.from_value({'value': 'tree'})
    Tree.from_dict.assert_called_with({'value': 'tree'})
    assert result == [Tree.from_dict()]


def test_tree_from_value_list(patch):
    """
    Ensures Tree.from_value can handle lists
    """
    patch.object(Tree, 'from_dict')
    result = Tree.from_value([{'values': 0}, {'values': 1}])
    assert result == [Tree.from_dict(), Tree.from_dict()]


def test_tree_from_value_value(patch):
    """
    Ensures Tree.from_value return any other value
    """
    assert Tree.from_value('value') == ['value']


def test_tree_from_dict(patch):
    patch.many(Tree, ['from_value', 'from_name'])
    result = Tree.from_dict({'start': {'inner': Token('value', 'value')}})
    Tree.from_value.assert_called_with({'inner': Token('value', 'value')})
    Tree.from_name.assert_called_with('start', Tree.from_value())
    assert result == Tree.from_name()


def test_tree_from_dict_token():
    assert Tree.from_dict(Token('test', 'test')) is None


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


def test_tree_insert():
    tree = Tree('tree', [])
    tree.insert('child')
    assert tree.children == ['child']


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
