# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from storyscript.compiler import FakeTree, Preprocessor
from storyscript.parser import Tree


def test_preprocessor_fake_tree(patch):
    patch.init(FakeTree)
    result = Preprocessor.fake_tree('block')
    FakeTree.__init__.assert_called_with('block')
    assert isinstance(result, FakeTree)


def test_preprocessor_replace_expression(magic, tree):
    parent = magic()
    expression = magic()
    Preprocessor.replace_expression(tree, parent, expression)
    tree.add_assignment.assert_called_with(expression.service)
    parent.replace.assert_called_with(1, tree.add_assignment().path)


def test_preprocessor_service_arguments(patch, magic, tree):
    patch.many(Preprocessor, ['fake_tree', 'replace_expression'])
    argument = magic()
    tree.find_data.return_value = [argument]
    Preprocessor.service_arguments('block', tree)
    Preprocessor.fake_tree.assert_called_with('block')
    tree.find_data.assert_called_with('arguments')
    argument.node.assert_called_with('values.inline_expression')
    args = (Preprocessor.fake_tree(), argument, argument.node())
    Preprocessor.replace_expression.assert_called_with(*args)


def test_preprocessor_service_arguments_no_expression(patch, magic, tree):
    patch.many(Preprocessor, ['fake_tree', 'replace_expression'])
    argument = magic(inline_expression=None)
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.service_arguments(magic(), tree)
    assert Preprocessor.replace_expression.call_count == 0


def test_preprocessor_assignment_expression(patch, magic, tree):
    patch.many(Preprocessor, ['fake_tree', 'replace_expression'])
    block = magic()
    Preprocessor.assignment_expression(block, tree)
    Preprocessor.fake_tree.assert_called_with(block)
    parent = block.rules.assignment.assignment_fragment
    args = (Preprocessor.fake_tree(), parent, tree.inline_expression)
    Preprocessor.replace_expression.assert_called_with(*args)


def test_preprocessor_assignments(patch, magic, tree):
    """
    Ensures Preprocessor.assignments can process lines like
    a = alpine echo text:(random value)
    """
    patch.object(Preprocessor, 'service_arguments')
    assignment = magic()
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    args = (tree, assignment.assignment_fragment.service)
    Preprocessor.service_arguments.assert_called_with(*args)


def test_preprocessor_assignments_to_expression(patch, magic, tree):
    """
    Ensures Preprocessor.assignments can processs lines like
    a = (alpine echo message:'text')
    """
    patch.object(Preprocessor, 'assignment_expression')
    assignment = magic()
    assignment.assignment_fragment.service = None
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    args = (tree, assignment.assignment_fragment.values)
    Preprocessor.assignment_expression.assert_called_with(*args)


def test_preprocessor_assignments_no_expression(patch, magic, tree):
    patch.object(Preprocessor, 'assignment_expression')
    assignment = magic()
    assignment.assignment_fragment.service = None
    assignment.assignment_fragment.values.inline_expression = None
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    assert Preprocessor.assignment_expression.call_count == 0


def test_preprocessor_service(patch, magic, tree):
    patch.object(Preprocessor, 'service_arguments')
    Preprocessor.service(tree)
    tree.node.assert_called_with('service_block.service')
    Preprocessor.service_arguments.assert_called_with(tree, tree.node())


def test_preprocessor_service_no_service(patch, magic, tree):
    patch.object(Preprocessor, 'service_arguments')
    tree.node.return_value = None
    Preprocessor.service(tree)
    assert Preprocessor.service_arguments.call_count == 0


def test_preprocessor_expression(tree):
    assert Preprocessor.expression(tree) is None


def test_preprocessor_process(patch, magic, tree):
    patch.many(Preprocessor, ['assignments', 'service', 'expression'])
    block = magic()
    tree.find_data.return_value = [block]
    result = Preprocessor.process(tree)
    Preprocessor.assignments.assert_called_with(block)
    Preprocessor.service.assert_called_with(block)
    Preprocessor.expression.assert_called_with(block)
    assert result == tree
