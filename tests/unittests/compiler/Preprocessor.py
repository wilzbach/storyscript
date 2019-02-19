# -*- coding: utf-8 -*-
from unittest import mock

from pytest import fixture

from storyscript.compiler import FakeTree, Preprocessor
from storyscript.parser import Tree


@fixture
def preprocessor(patch):
    patch.init(FakeTree)
    patch.object(Preprocessor, 'fake_tree', return_value=FakeTree(None))
    return Preprocessor()


@fixture
def entity(magic):
    obj = magic()
    obj.data = 'entity'
    return obj


def test_preprocessor_fake_tree(patch):
    patch.init(FakeTree)
    result = Preprocessor.fake_tree('block')
    FakeTree.__init__.assert_called_with('block')
    assert isinstance(result, FakeTree)


def test_preprocessor_replace_expression(magic, preprocessor, entity):
    """
    Check that the new assignment is inserted above the tree
    """
    node = magic()
    entity.line = lambda: 42
    entity.path.line = lambda: 123
    fake_tree = magic()
    preprocessor.replace_expression(node, fake_tree, entity)
    fake_tree.add_assignment.assert_called_with(node.service)
    assignment = fake_tree.add_assignment().path.child()
    entity.path.replace.assert_called_with(0, assignment)
    assert entity.path.children[0].line == 42
    assert entity.path.line() == 123


def test_preprocessor_process(patch, magic, preprocessor):
    """
    Check that process initializes the visitor correctly
    """
    patch.object(Preprocessor, 'visit')
    tree = magic()
    result = preprocessor.process(tree)
    assert result == tree
    preprocessor.visit.assert_called_with(
        tree, None, None, preprocessor.is_inline_expression,
        preprocessor.replace_expression)


def test_preprocessor_is_inline_expression(magic):
    """
    Check that inline_expressions are correctly detected
    """
    n = magic()
    assert not Preprocessor.is_inline_expression(n)
    n.data = 'foo'
    assert not Preprocessor.is_inline_expression(n)
    n.data = 'inline_expression'
    assert Preprocessor.is_inline_expression(n)


def test_preprocessor_visit_empty(patch, magic, preprocessor):
    """
    Check that no inline_expression is found
    """
    patch.object(Preprocessor, 'replace_expression')
    tree = magic()
    preprocessor.process(tree)
    assert not preprocessor.replace_expression.called


def test_preprocessor_visit_no_children(patch, magic, preprocessor):
    """
    Check that no inline_expression is found
    """
    patch.object(Preprocessor, 'replace_expression')
    tree = magic()
    tree.children = []
    preprocessor.process(tree)
    assert not preprocessor.replace_expression.called


def test_preprocessor_visit_one_children(patch, magic, preprocessor, entity):
    """
    Check that a single inline_expression is found
    """
    tree = magic()
    c1 = magic()
    replace = magic()
    c1.children = [magic()]
    tree.children = [c1]

    def is_inline(n):
        return n == c1
    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    preprocessor.fake_tree.assert_called_with('.block.')
    replace.assert_called_with(c1, preprocessor.fake_tree(), entity)
    assert replace.call_count == 1


def test_preprocessor_visit_two_children(patch, magic, preprocessor, entity):
    """
    Check that all inline_expressions are found
    """
    tree = magic()
    tree.children = cs = [magic(), magic()]
    replace = magic()
    for c in cs:
        c.children = [magic()]

    def is_inline(n):
        return n == cs[0] or n == cs[1]

    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    replace.mock_calls = [
        mock.call(cs[0], preprocessor.fake_tree(), entity),
        mock.call(cs[1], preprocessor.fake_tree(), entity),
    ]


def test_preprocessor_visit_nested_multiple(patch, magic, preprocessor,
                                            entity):
    """
    Check that all inline_expressions are found (even if they are nested)
    """
    tree = magic()
    replace = magic()
    cs = [magic(), magic()]
    for c in cs:
        c.children = [magic()]

    tree.children = [cs[0]]
    cs[0].children = [cs[1]]

    def is_inline(n):
        return n == cs[0] or n == cs[1]

    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    replace.mock_calls = [
        mock.call(cs[1], preprocessor.fake_tree(), entity),
        mock.call(cs[0], preprocessor.fake_tree(), entity),
    ]


def test_preprocessor_visit_nested_inner(patch, magic, preprocessor, entity):
    """
    Check that a nested inline_expression is called if it's deeper in the tree
    """
    tree = magic()
    replace = magic()
    cs = [magic(), magic()]
    for c in cs:
        c.children = [magic()]

    tree.children = [cs[0]]
    cs[0].children = [cs[1]]

    def is_inline(n):
        return n == cs[1]

    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    replace.mock_calls = [
        mock.call(cs[1], preprocessor.fake_tree(), entity),
    ]


def test_preprocessor_visit_nested_multiple_block(patch, magic, preprocessor,
                                                  entity):
    """
    Check that the fake tree is always generated from the nearest block
    """
    tree = magic()
    tree.data = 'block'
    replace = magic()
    cs = [magic(), magic()]
    for c in cs:
        c.children = [magic()]

    tree.children = [cs[0]]
    cs[0].children = [cs[1]]

    def is_inline(n):
        return n == cs[0] or n == cs[1]

    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    preprocessor.fake_tree.mock_calls = [
        mock.call(tree),
        mock.call(tree),
    ]
    replace.mock_calls = [
        mock.call(cs[1], preprocessor.fake_tree(), entity),
        mock.call(cs[0], preprocessor.fake_tree(), entity),
    ]


def test_preprocessor_visit_nested_multiple_block_nearest(patch,
                                                          magic, preprocessor,
                                                          entity):
    """
    Check that the fake tree is always generated from the nearest block
    """
    patch.object(Preprocessor, 'fake_tree')
    tree = magic()
    tree.data = 'block'
    replace = magic()
    cs = [magic(), magic()]
    for c in cs:
        c.children = [magic()]

    tree.children = [cs[0]]
    cs[0].children = [cs[1]]
    cs[0].data = 'block'

    def is_inline(n):
        return n == cs[0] or n == cs[1]

    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    replace.mock_calls = [
        mock.call(cs[1], preprocessor.fake_tree(cs[0]), entity),
        mock.call(cs[0], preprocessor.fake_tree(cs[1]), entity),
    ]


def test_preprocessor_visit_nested_parent(patch, magic, preprocessor, entity):
    """
    Check that the parent is always from the taken from the parent entity
    """
    tree = magic()
    tree.data = 'entity'
    replace = magic()
    cs = [magic(), magic()]
    for c in cs:
        c.children = [magic()]

    tree.children = [cs[0]]
    cs[0].children = [cs[1]]
    cs[0].data = 'entity'

    def is_inline(n):
        return n == cs[0] or n == cs[1]

    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    preprocessor.fake_tree.mock_calls = [
        mock.call(tree),
        mock.call(tree),
    ]
    replace.mock_calls = [
        mock.call(cs[1], preprocessor.fake_tree(), cs[0]),
        mock.call(cs[0], preprocessor.fake_tree(), tree),
    ]


def test_preprocessor_service_mut(patch, magic, preprocessor, entity):
    """
    Check that services are correctly converted into mutations
    """
    tree = magic()
    tree.data = 'service'
    replace = magic()
    cs = [magic(), magic()]
    for c in cs:
        c.children = [magic()]

    tree.children = [cs[0]]
    cs[0].children = [cs[1]]
    cs[0].data = 'path'
    tree.child(0).data = 'path'

    def is_inline(n):
        return n == cs[0]

    preprocessor.visit(tree, '.block.', entity, is_inline, replace)
    preprocessor.fake_tree.mock_calls = [
        mock.call(tree),
    ]
    replace.mock_calls = [
        mock.call(cs[0], preprocessor.fake_tree(), tree),
    ]
    assert tree.data == 'mutation'
    assert tree.entity == Tree('entity', [tree.path])
    assert tree.service_fragment.data == 'mutation_fragment'
