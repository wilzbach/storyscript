# -*- coding: utf-8 -*-
from pytest import raises

from storyscript.compiler.visitors.ExpressionVisitor import ExpressionVisitor


def test_objects_primary_expression_entity(patch, tree):
    """
    Ensures ExpressionVisitor.primary_expression works with an entity node
    """
    patch.many(ExpressionVisitor, ['entity'])
    tree.child(0).data = 'entity'
    r = ExpressionVisitor().primary_expression(tree)
    ExpressionVisitor.entity.assert_called_with(tree.entity)
    assert r == ExpressionVisitor.entity()


def test_objects_primary_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.primary_expression works with a
    or_expression node.
    """
    patch.many(ExpressionVisitor, ['entity', 'or_expression'])
    tree.child(0).data = 'or_expression'
    r = ExpressionVisitor().primary_expression(tree)
    ExpressionVisitor.or_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.or_expression()


def test_objects_pow_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.pow_expression works with one node
    """
    patch.many(ExpressionVisitor, ['primary_expression'])
    tree.child(0).data = 'primary_expression'
    tree.children = [1]
    r = ExpressionVisitor().pow_expression(tree)
    ExpressionVisitor.primary_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.primary_expression()


def test_objects_pow_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.pow_expression works with two nodes
    """
    patch.many(ExpressionVisitor, ['nary_expression',
                                   'primary_expression',
                                   'unary_expression'])
    tree.child(1).type = 'POWER'
    tree.children = [1, '+', 2]
    r = ExpressionVisitor().pow_expression(tree)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree, tree.child(1), [
            ExpressionVisitor.primary_expression(tree.child(0)),
            ExpressionVisitor.unary_expression(tree.child(2))
        ])
    assert r == ExpressionVisitor.nary_expression()


def test_objects_unary_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.nary_expression works with one node
    """
    patch.many(ExpressionVisitor, ['pow_expression'])
    tree.child(0).data = 'pow_expression'
    tree.children = [1]
    r = ExpressionVisitor().unary_expression(tree)
    ExpressionVisitor.pow_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.pow_expression()


def test_objects_unary_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.nary_expression works with two nodes
    """
    patch.many(ExpressionVisitor, ['nary_expression'])
    tree.child(1).data = 'unary_operator'
    unary_expression = ExpressionVisitor().unary_expression
    patch.object(ExpressionVisitor, 'unary_expression')
    r = unary_expression(tree)
    op = tree.unary_operator.child(0)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree, op, [ExpressionVisitor.unary_expression(tree.child(1))])
    assert r == ExpressionVisitor.nary_expression()


def test_objects_mul_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.mul_expression works with one node
    """
    patch.many(ExpressionVisitor, ['unary_expression'])
    tree.child(0).data = 'unary_expression'
    tree.children = [1]
    r = ExpressionVisitor().mul_expression(tree)
    ExpressionVisitor.unary_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.unary_expression()


def test_objects_mul_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.mul_expression works with two nodes
    """
    patch.many(ExpressionVisitor, ['nary_expression',
                                   'unary_expression'])
    tree.child(1).data = 'mul_operator'
    tree.children = [1, '*', 2]
    mul_expression = ExpressionVisitor().mul_expression
    patch.object(ExpressionVisitor, 'mul_expression')
    r = mul_expression(tree)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree, tree.child(1).child(0), [
            ExpressionVisitor.mul_expression(tree.child(0)),
            ExpressionVisitor.unary_expression(tree.child(2))
        ])
    assert r == ExpressionVisitor.nary_expression()


def test_objects_arith_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.arith_expression works with one node
    """
    patch.many(ExpressionVisitor, ['mul_expression'])
    tree.child(0).data = 'mul_expression'
    tree.children = [1]
    r = ExpressionVisitor().arith_expression(tree)
    ExpressionVisitor.mul_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.mul_expression()


def test_objects_arith_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.arith_expression works with two nodes
    """
    patch.many(ExpressionVisitor, ['mul_expression', 'nary_expression'])
    tree.child(1).data = 'arith_operator'
    tree.children = [1, '+', 2]
    arith_expression = ExpressionVisitor().arith_expression
    patch.object(ExpressionVisitor, 'arith_expression')
    r = arith_expression(tree)
    op_type = tree.child(1).child(0)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree, op_type, values=[
            ExpressionVisitor.arith_expression(tree.child(0)),
            ExpressionVisitor.mul_expression(tree.children[2])
        ])
    assert r == ExpressionVisitor.nary_expression()


def test_objects_or_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.or_expression works with one node
    """
    patch.many(ExpressionVisitor, ['and_expression'])
    tree.child(0).data = 'and_expression'
    tree.children = [1]
    r = ExpressionVisitor().or_expression(tree)
    ExpressionVisitor.and_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.and_expression()


def test_objects_or_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.or_expression works with two nodes
    """
    patch.many(ExpressionVisitor, ['nary_expression',
                                   'and_expression'])
    tree.child(1).type = 'OR'
    tree.children = [1, 'or', 2]
    or_expression = ExpressionVisitor().or_expression
    patch.object(ExpressionVisitor, 'or_expression')
    r = or_expression(tree)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree, tree.child(1), [
            ExpressionVisitor.or_expression(tree.child(0)),
            ExpressionVisitor.and_expression(tree.child(2))
        ])
    assert r == ExpressionVisitor.nary_expression()


def test_objects_and_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.and_expression works with one node
    """
    patch.many(ExpressionVisitor, ['cmp_expression'])
    tree.child(0).data = 'cmp_expression'
    tree.children = [1]
    r = ExpressionVisitor().and_expression(tree)
    ExpressionVisitor.cmp_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.cmp_expression()


def test_objects_and_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.and_expression works with two nodes
    """
    patch.many(ExpressionVisitor, ['nary_expression',
                                   'cmp_expression'])
    tree.child(1).type = 'AND'
    tree.children = [1, 'and', 2]
    and_expression = ExpressionVisitor().and_expression
    patch.object(ExpressionVisitor, 'and_expression')
    r = and_expression(tree)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree, tree.child(1), [
            ExpressionVisitor.and_expression(tree.child(0)),
            ExpressionVisitor.cmp_expression(tree.child(2)),
        ])
    assert r == ExpressionVisitor.nary_expression()


def test_objects_cmp_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.and_expression works with one node
    """
    patch.many(ExpressionVisitor, ['arith_expression'])
    tree.child(0).data = 'arith_expression'
    tree.children = [1]
    r = ExpressionVisitor().cmp_expression(tree)
    ExpressionVisitor.arith_expression.assert_called_with(tree.child(0))
    assert r == ExpressionVisitor.arith_expression()


def test_objects_cmp_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.and_expression works with two nodes
    """
    patch.many(ExpressionVisitor, ['nary_expression',
                                   'arith_expression'])
    tree.child(1).data = 'cmp_operator'
    tree.children = [1, '==', 2]
    cmp_expression = ExpressionVisitor().cmp_expression
    patch.object(ExpressionVisitor, 'cmp_expression')
    r = cmp_expression(tree)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree, tree.child(1).child(0), [
            ExpressionVisitor.cmp_expression(tree.child(0)),
            ExpressionVisitor.arith_expression(tree.child(2)),
        ])
    assert r == ExpressionVisitor.nary_expression()


def test_objects_nary_expression(patch, tree):
    """
    Ensures that the ExpressionVisitor by default throws AssertionErrors
    for to-be-implemented methods.
    """
    with raises(AssertionError):
        ExpressionVisitor().nary_expression(0)


def test_objects_values(patch, tree):
    """
    Ensures that the ExpressionVisitor by default throws AssertionErrors
    for to-be-implemented methods.
    """
    with raises(AssertionError):
        ExpressionVisitor().values(0)
