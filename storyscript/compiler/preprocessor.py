# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from .faketree import FakeTree
from ..parser import Tree


class Preprocessor:
    """
    Performs additional transformations that can't be performed, or would be
    too complicated for the Transformer, before the tree is compiled.
    """

    @staticmethod
    def inline_arguments(block, service):
        """
        Processes an inline expression in a service call, for example:
        alpine echo text:(random value)
        """
        block_line = block.line()
        for argument in service.find_data('arguments'):
            if argument.inline_expression:
                line = FakeTree.line(block_line)
                value = argument.inline_expression.service
                assignment = FakeTree.assignment(line, value)
                block.insert(assignment)
                argument.replace(1, assignment.path)

    @classmethod
    def process_assignments(cls, block):
        """
        Process assignments, looking for inline expressions to replace,
        for example: a = alpine echo text:(random value)
        """
        for assignment in block.find_data('assignment'):
            service = assignment.node('assignment_fragment.service')
            if service:
                cls.inline_arguments(block, service)

    @classmethod
    def process_blocks(cls, tree):
        """
        Processes blocks, looking for trees that must be preprocessed.
        """
        for block in tree.find_data('block'):
            cls.process_assignments(block)
            service = block.node('service_block.service')
            if service:
                cls.inline_arguments(block, service)

    @classmethod
    def process(cls, tree):
        cls.process_blocks(tree)
        return tree
