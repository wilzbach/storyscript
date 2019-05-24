# -*- coding: utf-8 -*-
from unittest import mock

from pytest import fixture

from storyscript.compiler.lowering import FakeTree, Lowering
from storyscript.parser import Tree


@fixture
def preprocessor(patch):
    patch.init(FakeTree)
    patch.object(Lowering, 'fake_tree', return_value=FakeTree(None))
    return Lowering(parser=None, features=None)


@fixture
def entity(magic):
    obj = magic()
    obj.data = 'entity'
    return obj


def test_preprocessor_fake_tree(patch):
    patch.init(FakeTree)
    result = Lowering.fake_tree('block')
    FakeTree.__init__.assert_called_with('block')
    assert isinstance(result, FakeTree)


def test_preprocessor_replace_expression(magic, preprocessor, entity):
    """
    Check that the new assignment is inserted above the tree
    """
    node = magic()
    entity.line = lambda: 42
    entity.path.line = magic()
    fake_tree = magic()
    preprocessor.replace_expression(node, fake_tree, entity)
    fake_tree.add_assignment.assert_called_with(node.service,
                                                original_line=42)
    assignment = fake_tree.add_assignment()
    entity.replace.assert_called_with(0, assignment.child(0))


def test_preprocessor_replace_expression_function_call(magic, preprocessor,
                                                       entity):
    """
    Check that the new function call is inserted above the tree
    """
    node = magic()
    node.service = None
    entity.line = lambda: 42
    fake_tree = magic()
    preprocessor.replace_expression(node, fake_tree, entity)
    fake_tree.add_assignment.assert_called_with(node.call_expression,
                                                original_line=42)
    assignment = fake_tree.add_assignment()
    entity.replace.assert_called_with(0, assignment.child(0))


def test_preprocessor_process(patch, magic, preprocessor):
    """
    Check that process initializes the visitor correctly
    """
    patch.object(Lowering, 'visit')
    tree = magic()
    result = preprocessor.process(tree)
    assert result == tree
    preprocessor.visit.assert_called_with(
        tree, None, None, preprocessor.is_inline_expression,
        preprocessor.replace_expression, parent=None)


def test_preprocessor_is_inline_expression(magic):
    """
    Check that inline_expressions are correctly detected
    """
    n = magic()
    assert not Lowering.is_inline_expression(n)
    n.data = 'foo'
    assert not Lowering.is_inline_expression(n)
    n.data = 'inline_expression'
    assert Lowering.is_inline_expression(n)


def test_preprocessor_visit_empty(patch, magic, preprocessor):
    """
    Check that no inline_expression is found
    """
    patch.object(Lowering, 'replace_expression')
    tree = magic()
    preprocessor.process(tree)
    assert not preprocessor.replace_expression.called


def test_preprocessor_visit_no_children(patch, magic, preprocessor):
    """
    Check that no inline_expression is found
    """
    patch.object(Lowering, 'replace_expression')
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
    preprocessor.fake_tree.assert_called_with('.block.')
    replace.assert_called_with(c1, preprocessor.fake_tree(), entity.path)
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
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
    patch.object(Lowering, 'fake_tree')
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
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

    preprocessor.visit(tree, '.block.', entity, is_inline,
                       replace, parent=None)
    preprocessor.fake_tree.mock_calls = [
        mock.call(tree),
    ]
    replace.mock_calls = [
        mock.call(cs[0], preprocessor.fake_tree(), tree),
    ]
    assert tree.data == 'mutation'
    assert tree.entity == Tree('entity', [tree.path])
    assert tree.service_fragment.data == 'mutation_fragment'


def test_preprocessor_visit_base_expression(patch, magic, preprocessor,
                                            entity):
    """
    Check that a base_expression is found and replaced
    """
    patch.object(Lowering, 'fake_tree')
    tree = magic()
    c1 = magic()
    base_expression = magic()
    base_expression.data = 'base_expression'
    base_expression.child(0).data = 'service'
    base_expression.children = ['42']
    c1.data = 'block'
    replace = magic()
    c1.children = [base_expression]
    tree.children = [c1]

    preprocessor.visit(tree, '.block.', entity, lambda x: False,
                       replace, parent=None)
    preprocessor.fake_tree.assert_called_with(c1)
    replace.assert_called_with(base_expression, preprocessor.fake_tree(),
                               base_expression)
    assert base_expression.children == [Tree('path', ['42'])]
    assert replace.call_count == 1


def test_preprocessor_visit_base_expression_ignore(patch, magic, preprocessor,
                                                   entity):
    """
    Check that a base_expression is not replaced for assignments
    """
    patch.object(Lowering, 'fake_tree')
    tree = magic()
    c1 = magic()
    base_expression = magic()
    base_expression.data = 'base_expression'
    base_expression.child(0).data = 'service'
    base_expression.children = ['42']
    c1.data = 'assignment_fragment'
    replace = magic()
    c1.children = [base_expression]
    tree.children = [c1]

    preprocessor.visit(tree, '.block.', entity, lambda x: False,
                       replace, parent=None)
    preprocessor.fake_tree.assert_not_called()
    replace.assert_not_called()


def flatten_to_string(s):
    return {'$OBJECT': 'string', 'string': s}


def test_objects_flatten_template_no_templates(patch, tree):
    result = list(Lowering.flatten_template(tree, '.s.'))
    assert result == [flatten_to_string('.s.')]


def test_objects_flatten_template_only_templates(patch, tree):
    result = list(Lowering.flatten_template(tree, '{hello}'))
    assert result == [{'$OBJECT': 'code', 'code': 'hello'}]


def test_objects_flatten_template_mixed(patch, tree):
    result = list(Lowering.flatten_template(tree, 'a{hello}b'))
    assert result == [
        flatten_to_string('a'),
        {'$OBJECT': 'code', 'code': 'hello'},
        flatten_to_string('b')
    ]


def test_objects_flatten_template_escapes(patch, tree):
    result = list(Lowering.flatten_template(tree, r'\{\}'))
    assert result == [
        flatten_to_string('{}'),
    ]


def test_objects_flatten_template_escapes2(patch, tree):
    result = list(Lowering.flatten_template(tree, r'\\.\'.\".\\'))
    assert result == [
        flatten_to_string(r"""\\.'.".\\"""),
    ]


def test_objects_flatten_template_escapes3(patch, tree):
    result = list(Lowering.flatten_template(tree, r'\\\\\\'))
    assert result == [
        flatten_to_string(r'\\\\\\'),
    ]


def test_objects_flatten_template_escapes4(patch, tree):
    result = list(Lowering.flatten_template(tree, r'\\{\\}\\'))
    assert result == [
        flatten_to_string(r'\\'),
        {'$OBJECT': 'code', 'code': '\\'},
        flatten_to_string(r'\\')
    ]


def test_objects_flatten_template_escapes_newlines(patch, tree):
    result = list(Lowering.flatten_template(tree, r'\n\n'))
    assert result == [
        flatten_to_string(r'\n\n'),
    ]


def test_objects_flatten_template_escapes_uni(patch, tree):
    result = list(Lowering.flatten_template(tree, r'\x42\t\u1212'))
    assert result == [
        flatten_to_string(r'\x42\t\u1212'),
    ]


def test_objects_flatten_template_escapes_uni2(patch, tree):
    result = list(Lowering.flatten_template(tree, r'\U0001F600'))
    assert result == [
        flatten_to_string(r'\U0001F600'),
    ]


def test_objects_flatten_template_escapes_uni3(patch, tree):
    result = list(Lowering.flatten_template(tree,
                                            r'\N{LATIN CAPITAL LETTER A}'))
    assert result == [
        flatten_to_string(r'\N{LATIN CAPITAL LETTER A}'),
    ]
