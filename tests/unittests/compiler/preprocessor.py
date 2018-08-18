# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from storyscript.compiler import Preprocessor
from storyscript.parser import Tree


def test_preprocessor_magic_line(patch, magic, tree):
    patch.object(uuid, 'uuid4', return_value=magic(int=123456789))
    result = Preprocessor.magic_line(tree)
    assert result == '0.12345678'


def test_preprocessor_magic_path(patch):
    patch.object(uuid, 'uuid4')
    result = Preprocessor.magic_path(1)
    name = '${}'.format(uuid.uuid4().hex[:8])
    assert result == Tree('path', [Token('NAME', name, line=1)])


def test_preprocessor_magic_assignment(patch, tree):
    patch.object(Preprocessor, 'magic_path')
    result = Preprocessor.magic_assignment('1', tree)
    Preprocessor.magic_path.assert_called_with('1')
    assert tree.child().child().line == '1'
    assert result.children[0] == Preprocessor.magic_path()
    assert result.children[1] == Tree('assignment_fragment',
                                      [Token('EQUALS', '='), tree])


def test_preprocessor_inline_arguments(patch, magic, tree):
    patch.many(Preprocessor, ['magic_line', 'magic_assignment'])
    block = magic()
    argument = magic()
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.inline_arguments(block, tree)
    tree.service_fragment.find_data.assert_called_with('arguments')
    Preprocessor.magic_line.assert_called_with(block)
    value = argument.inline_expression.service
    Preprocessor.magic_assignment.assert_called_with(Preprocessor.magic_line(),
                                                     value)
    block.insert.assert_called_with(Preprocessor.magic_assignment())
    path = Preprocessor.magic_assignment().path
    argument.replace.assert_called_with(1, path)


def test_preprocessor_inline_arguments_no_expression(patch, magic, tree):
    patch.many(Preprocessor, ['magic_line', 'magic_assignment'])
    argument = magic(inline_expression=None)
    tree.service_fragment.find_data.return_value = [argument]
    Preprocessor.inline_arguments('block', tree)
    assert Preprocessor.magic_line.call_count == 0


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
