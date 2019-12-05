# -*- coding: utf-8 -*-
from pytest import raises

from storyscript.compiler.visitors.ExpressionVisitor import ExpressionVisitor


def test_objects_expression_one(patch, tree):
    """
    Ensures ExpressionVisitor.expression works with one node
    """
    patch.many(ExpressionVisitor, ["entity"])
    tree.first_child().data = "entity"
    tree.children = [1]
    r = ExpressionVisitor().expression(tree)
    ExpressionVisitor.entity.assert_called_with(tree.first_child())
    assert r == ExpressionVisitor.entity()


def test_objects_expression_two(patch, tree):
    """
    Ensures ExpressionVisitor.expression works with two nodes
    """
    patch.many(ExpressionVisitor, ["nary_expression"])
    tree.first_child().data = "unary_operator"
    tree.children = ["!", 1]
    expression = ExpressionVisitor().expression
    patch.object(ExpressionVisitor, "expression")
    r = expression(tree)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree,
        tree.first_child().child(0),
        [ExpressionVisitor.expression(tree.child(1))],
    )
    assert r == ExpressionVisitor.nary_expression()


def test_objects_expression_two_as(patch, tree):
    """
    Ensures ExpressionVisitor.expression works with as
    """
    patch.many(ExpressionVisitor, ["to_expression"])
    tree.child(1).data = "to_operator"
    tree.children = ["!", 1]
    expression = ExpressionVisitor().expression
    patch.object(ExpressionVisitor, "expression")
    r = expression(tree)
    ExpressionVisitor.to_expression.assert_called_with(
        tree, ExpressionVisitor.expression(tree.first_child()),
    )
    assert r == ExpressionVisitor.to_expression()


def test_objects_expression_three(patch, tree):
    """
    Ensures ExpressionVisitor.expression works with three nodes
    """
    patch.many(ExpressionVisitor, ["nary_expression"])
    tree.child(1).data = "mul_operator"
    tree.children = [1, "*", 2]
    expression = ExpressionVisitor().expression
    patch.object(ExpressionVisitor, "expression")
    r = expression(tree)
    ExpressionVisitor.nary_expression.assert_called_with(
        tree,
        tree.child(1).child(0),
        [
            ExpressionVisitor.expression(tree.first_child()),
            ExpressionVisitor.expression(tree.child(2)),
        ],
    )
    assert r == ExpressionVisitor.nary_expression()


def test_objects_nary_expression(patch, tree):
    """
    Ensures that the ExpressionVisitor by default throws AssertionErrors
    for to-be-implemented methods.
    """
    with raises(NotImplementedError):
        ExpressionVisitor().nary_expression(0)


def test_objects_values(patch, tree):
    """
    Ensures that the ExpressionVisitor by default throws AssertionErrors
    for to-be-implemented methods.
    """
    with raises(NotImplementedError):
        ExpressionVisitor().values(0)


def test_objects_to_expression(patch, tree):
    """
    Ensures that the ExpressionVisitor by default throws AssertionErrors
    for to-be-implemented methods.
    """
    with raises(NotImplementedError):
        ExpressionVisitor().to_expression(None, 0)
