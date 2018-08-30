# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from storyscript.compiler import FakeTree, Preprocessor
from storyscript.parser import Tree


def test_preprocessor_inline_arguments(patch, magic, tree):
    patch.init(FakeTree)
    patch.object(FakeTree, 'add_assignment')
    argument = magic()
    tree.find_data.return_value = [argument]
    Preprocessor.inline_arguments('block', tree)
    FakeTree.__init__.assert_called_with('block')
    tree.find_data.assert_called_with('arguments')
    value = argument.values.inline_expression.service
    FakeTree.add_assignment.assert_called_with(value)
    argument.replace.assert_called_with(1, FakeTree.add_assignment().path)


def test_preprocessor_inline_arguments_no_expression(patch, magic, tree):
    patch.init(FakeTree)
    patch.object(FakeTree, 'add_assignment')
    argument = magic(inline_expression=None)
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.inline_arguments(magic(), tree)
    assert FakeTree.add_assignment.call_count == 0


def test_preprocessor_process_assignments(patch, magic, tree):
    patch.object(Preprocessor, 'inline_arguments')
    assignment = magic()
    tree.find_data.return_value = [assignment]
    Preprocessor.process_assignments(tree)
    assignment.node.assert_called_with('assignment_fragment.service')
    Preprocessor.inline_arguments.assert_called_with(tree, assignment.node())


def test_preprocessor_process_blocks(patch, magic, tree):
    patch.many(Preprocessor, ['inline_arguments', 'process_assignments'])
    block = magic()
    tree.find_data.return_value = [block]
    Preprocessor.process_blocks(tree)
    Preprocessor.process_assignments.assert_called_with(block)
    block.node.assert_called_with('service_block.service')
    Preprocessor.inline_arguments.assert_called_with(block, block.node())


def test_preprocessor_process_blocks_no_target(patch, magic, tree):
    patch.many(Preprocessor, ['inline_arguments', 'process_assignments'])
    block = magic()
    block.node.return_value = None
    tree.find_data.return_value = [block]
    Preprocessor.process_blocks(tree)
    assert Preprocessor.inline_arguments.call_count == 0


def test_preprocessor_process(patch):
    patch.object(Preprocessor, 'process_blocks')
    result = Preprocessor.process('tree')
    Preprocessor.process_blocks.assert_called_with('tree')
    assert result == 'tree'
