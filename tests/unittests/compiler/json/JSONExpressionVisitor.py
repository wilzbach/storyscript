# -*- coding: utf-8 -*-

from pytest import fixture, mark

from storyscript.compiler.json.JSONExpressionVisitor import \
        JSONExpressionVisitor


@fixture
def visitor(patch):
    patch.init(JSONExpressionVisitor)
    return JSONExpressionVisitor()


def test_objects_build_unary_expression(patch, visitor, tree, magic):
    """
    Ensures JSONExpressionVisitor.build_unary_expression builds
    an expression properly.
    """
    patch.many(JSONExpressionVisitor, ['expression_type'])
    op = magic()
    left = magic()
    result = visitor.nary_expression(tree, op, [left])
    JSONExpressionVisitor.expression_type.assert_called_with(op.type, tree)
    assert result == {
        '$OBJECT': 'expression',
        'expression': JSONExpressionVisitor.expression_type(),
        'values':  [left],
    }


def test_objects_build_binary_expression(patch, visitor, tree, magic):
    """
    Ensures JSONExpressionVisitor.build_binary_expression builds an
    expression properly.
    """
    patch.many(JSONExpressionVisitor, ['expression_type'])
    op = magic()
    left = magic()
    right = magic()
    result = visitor.nary_expression(
        tree, op, [left, right],
    )
    JSONExpressionVisitor.expression_type.assert_called_with(op.type, tree)
    assert result == {
        '$OBJECT': 'expression',
        'expression': JSONExpressionVisitor.expression_type(),
        'values':  [left, right],
    }


def test_objects_build_nary_expression(patch, visitor, tree, magic):
    """
    Ensures JSONExpressionVisitor.build_binary_expression builds an
    expression properly.
    """
    patch.many(JSONExpressionVisitor, ['expression_type'])
    op = magic()
    values = [1, 2, 3]
    result = visitor.nary_expression(
        tree, op, values
    )
    JSONExpressionVisitor.expression_type.assert_called_with(op.type, tree)
    assert result == {
        '$OBJECT': 'expression',
        'expression': JSONExpressionVisitor.expression_type(),
        'values':  [1, 2, 3],
    }


@mark.parametrize('operator, expression', [
    ('PLUS', 'sum'), ('MULTIPLIER', 'multiplication'),
    ('BSLASH', 'division'), ('MODULUS', 'modulus'),
    ('POWER', 'exponential'), ('DASH', 'subtraction'), ('AND', 'and'),
    ('OR', 'or'), ('NOT', 'not'),
    ('EQUAL', 'equal'),
    ('LESSER', 'less'),
    ('LESSER_EQUAL', 'less_equal'),
])
def test_objects_expression_type(operator, expression, visitor, tree):
    result = visitor.expression_type(operator, tree)
    assert result == expression
