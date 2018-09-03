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
    argument = magic()
    Preprocessor.replace_expression(tree, argument)
    service = argument.values.inline_expression.service
    tree.add_assignment.assert_called_with(service)
    argument.replace.assert_called_with(1, tree.add_assignment().path)


def test_preprocessor_service_arguments(patch, magic, tree):
    patch.many(Preprocessor, ['replace_expression', 'fake_tree'])
    argument = magic()
    tree.find_data.return_value = [argument]
    Preprocessor.service_arguments('block', tree)
    Preprocessor.fake_tree.assert_called_with('block')
    tree.find_data.assert_called_with('arguments')
    args = (Preprocessor.fake_tree(), argument)
    Preprocessor.replace_expression.assert_called_with(*args)


def test_preprocessor_service_arguments_no_expression(patch, magic, tree):
    patch.many(Preprocessor, ['replace_expression', 'fake_tree'])
    argument = magic(inline_expression=None)
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.service_arguments(magic(), tree)
    assert Preprocessor.replace_expression.call_count == 0


def test_preprocessor_assignments(patch, magic, tree):
    """
    Ensures Preprocessor.assignments can process lines like
    a = alpine echo text:(random value)
    """
    patch.object(Preprocessor, 'service_arguments')
    assignment = magic()
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    assignment.node.assert_called_with('assignment_fragment.service')
    Preprocessor.service_arguments.assert_called_with(tree, assignment.node())


def test_preprocessor_service(patch, magic, tree):
    patch.object(Preprocessor, 'inline_expressions')
    Preprocessor.service(tree)
    tree.node.assert_called_with('service_block.service')
    Preprocessor.inline_expressions.assert_called_with(tree, tree.node())


def test_preprocessor_service_no_service(patch, magic, tree):
    patch.object(Preprocessor, 'inline_expressions')
    tree.node.return_value = None
    Preprocessor.service(tree)
    assert Preprocessor.inline_expressions.call_count == 0


def test_preprocessor_process(patch, magic, tree):
    patch.many(Preprocessor, ['assignments', 'service'])
    block = magic()
    tree.find_data.return_value = [block]
    result = Preprocessor.process(tree)
    Preprocessor.assignments.assert_called_with(block)
    Preprocessor.service.assert_called_with(block)
    assert result == tree
