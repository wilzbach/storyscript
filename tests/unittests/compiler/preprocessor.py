# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from storyscript.compiler import FakeTree, Preprocessor
from storyscript.parser import Tree


def test_preprocessor_inline_expressions(patch, magic, tree):
    patch.init(FakeTree)
    patch.object(FakeTree, 'add_assignment')
    argument = magic()
    tree.find_data.return_value = [argument]
    Preprocessor.inline_expressions('block', tree)
    FakeTree.__init__.assert_called_with('block')
    tree.find_data.assert_called_with('arguments')
    value = argument.values.inline_expression.service
    FakeTree.add_assignment.assert_called_with(value)
    argument.replace.assert_called_with(1, FakeTree.add_assignment().path)


def test_preprocessor_inline_expressions_no_expression(patch, magic, tree):
    patch.init(FakeTree)
    patch.object(FakeTree, 'add_assignment')
    argument = magic(inline_expression=None)
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.inline_expressions(magic(), tree)
    assert FakeTree.add_assignment.call_count == 0


def test_preprocessor_assignments(patch, magic, tree):
    patch.object(Preprocessor, 'inline_expressions')
    assignment = magic()
    tree.find_data.return_value = [assignment]
    Preprocessor.assignments(tree)
    assignment.node.assert_called_with('assignment_fragment.service')
    Preprocessor.inline_expressions.assert_called_with(tree, assignment.node())


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


def test_preprocessor_blocks(patch, magic, tree):
    patch.many(Preprocessor, ['inline_expressions', 'assignments'])
    block = magic()
    tree.find_data.return_value = [block]
    Preprocessor.blocks(tree)
    Preprocessor.assignments.assert_called_with(block)
    block.node.assert_called_with('service_block.service')
    Preprocessor.inline_expressions.assert_called_with(block, block.node())


def test_preprocessor_blocks_no_target(patch, magic, tree):
    patch.many(Preprocessor, ['inline_expressions', 'assignments'])
    block = magic()
    block.node.return_value = None
    tree.find_data.return_value = [block]
    Preprocessor.blocks(tree)
    assert Preprocessor.inline_expressions.call_count == 0


def test_preprocessor_process(patch):
    patch.object(Preprocessor, 'blocks')
    result = Preprocessor.process('tree')
    Preprocessor.blocks.assert_called_with('tree')
    assert result == 'tree'
