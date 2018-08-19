# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from storyscript.compiler import FakeTree, Preprocessor
from storyscript.parser import Tree


def test_preprocessor_inline_arguments(patch, magic, tree):
    patch.many(FakeTree, ['line', 'assignment'])
    block = magic()
    argument = magic()
    tree.find_data.return_value = [argument]
    Preprocessor.inline_arguments(block, tree)
    tree.find_data.assert_called_with('arguments')
    FakeTree.line.assert_called_with(block.line())
    value = argument.inline_expression.service
    FakeTree.assignment.assert_called_with(FakeTree.line(), value)
    block.insert.assert_called_with(FakeTree.assignment())
    path = FakeTree.assignment().path
    argument.replace.assert_called_with(1, path)


def test_preprocessor_inline_arguments_no_expression(patch, magic, tree):
    patch.many(FakeTree, ['line', 'assignment'])
    argument = magic(inline_expression=None)
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.inline_arguments(magic(), tree)
    assert FakeTree.line.call_count == 0


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
