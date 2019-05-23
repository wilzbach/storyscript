# -*- coding: utf-8 -*-
from unittest.mock import call

from lark.lexer import Token
from lark.tree import Tree as LarkTree

from pytest import fixture, raises

from storyscript.exceptions.CompilerError import CompilerError
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


def test_tree_node_nested(patch):
    patch.object(Tree, 'walk')
    tree = Tree('rule', [])
    result = tree.node('inner.nested')
    assert len(Tree.walk.call_args_list) == 2
    assert Tree.walk.call_args_list[0] == call(tree, 'inner')
    assert Tree.walk.call_args_list[1] == call(Tree.walk(), 'nested')
    assert result == Tree.walk()


def test_tree_first_child():
    tree = Tree('rule', ['child'])
    assert tree.first_child() == 'child'


def test_tree_first_child_multiple():
    tree = Tree('rule', ['child', 'child2'])
    assert tree.first_child() == 'child'


def test_tree_first_child_empty():
    tree = Tree('rule', [])
    with raises(AssertionError):
        tree.first_child()


def test_tree_last_child():
    tree = Tree('rule', ['child'])
    assert tree.last_child() == 'child'


def test_tree_last_child_multiple():
    tree = Tree('rule', ['child', 'child2'])
    assert tree.last_child() == 'child2'


def test_tree_last_child_empty():
    tree = Tree('rule', [])
    with raises(AssertionError):
        tree.last_child()


def test_tree_child():
    tree = Tree('rule', ['child'])
    assert tree.child(0) == 'child'


def test_tree_child_overflow():
    tree = Tree('rule', ['child'])
    with raises(AssertionError):
        tree.child(1)


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


def test_tree_find_first_token():
    """
    Ensures Tree.find_first_token can find the correct Token
    """
    expected = Tree('assignment', ['x'])
    tree = Tree('start', [Tree('block', [Tree('line', [expected])])])
    assert tree.find('assignment') == [expected]


def test_tree_find_first_token_middle():
    """
    Ensures Tree.find_first_token can find the correct Token
    """
    t1 = Token('X1', 'x1')
    t2 = Token('X2', 'x2')
    e1 = Tree('assignment', [t1])
    e2 = Tree('assignment', [t2])
    tree = Tree('start', [Tree('block', [Tree('line', [e1])]), e2])
    assert tree.find_first_token() == t1


def test_tree_find_first_token_end():
    """
    Ensures Tree.find_first_token can find the correct Token
    """
    t2 = Token('X', 'x')
    e1 = Tree('assignment', [])
    e2 = Tree('assignment', [t2])
    tree = Tree('start', [Tree('block', [Tree('line', [e1])]), e2])
    assert tree.find_first_token() == t2


def test_tree_find_first_token_none():
    """
    Ensures Tree.find_first_token can find the correct Token
    """
    expected = Tree('assignment', [])
    tree = Tree('start', [Tree('block', [Tree('line', [expected])], expected)])
    assert tree.find_first_token() is None


def test_tree_extract():
    target = Tree('target', [])
    tree = Tree('tree', [target, Tree('more', [target])])
    assert tree.extract('target') == [target]


def test_tree_expect(tree):
    """
    Ensures expect throws an error
    """
    with raises(CompilerError) as e:
        tree.expect(0, 'error')

    assert e.value.message() == 'Unknown compiler error'


def test_tree_expect_kwargs(tree):
    """
    Ensures expect throws an error and forwards arguments
    """
    with raises(CompilerError) as e:
        tree.expect(0, 'error', a=0, b=1, c=2)

    assert e.value.format_args.a == 0
    assert e.value.format_args.b == 1
    assert e.value.format_args.c == 2


def test_follow_node_chain_no_children(tree):
    """
    Ensures we don't follow a node chain if there are no children
    """
    assert tree.follow_node_chain(['foo', 'bar']) is None
    tree.children = [1, 2]
    assert tree.follow_node_chain(['foo', 'bar']) is None


def test_follow_node_chain_children(patch, tree):
    """
    Ensures we follow a node chain if there are children
    """
    m = Tree('mock', [])
    tree.children = [0]
    patch.object(Tree, 'iter_subtrees')
    Tree.iter_subtrees.return_value = iter([m])
    assert tree.follow_node_chain(['foo', 'bar']) is None

    Tree.iter_subtrees.return_value = iter([m])
    assert tree.follow_node_chain(['mock']) is m

    arr = [m, Tree('m2', []), Tree('m3', [])]
    Tree.iter_subtrees.side_effect = lambda: iter(arr)
    assert tree.follow_node_chain(['mock']) is None
    assert tree.follow_node_chain(['mock', 'm2']) is None
    assert tree.follow_node_chain(['m2', 'mock']) is None
    assert tree.follow_node_chain(['m4', 'm2', 'mock']) is None
    assert tree.follow_node_chain(['m4', 'm3', 'm2', 'mock']) is None
    assert tree.follow_node_chain(['m3', 'm2', 'mock']) == m


def test_follow_empty(patch, tree):
    m = Tree('mock', [])
    assert m.follow(['foo']) is None


def test_follow_first(patch, tree):
    foo = Tree('foo', [])
    m = Tree('mock', [foo])
    assert m.follow(['foo']) is foo


def test_follow_multiple(patch, tree):
    foo = Tree('foo', [])
    bar = Tree('bar', [])
    m = Tree('mock', [foo, bar])
    assert m.follow(['foo']) is None


def test_follow_nested(patch, tree):
    bar = Tree('bar', [])
    foo = Tree('foo', [bar])
    m = Tree('mock', [foo])
    assert m.follow(['foo', 'bar']) is bar
