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
    def inline_expressions(block, service):
        """
        Processes an inline expression in a service call, for example:
        alpine echo text:(random value)
        """
        fake_tree = FakeTree(block)
        for argument in service.find_data('arguments'):
            if argument.values.inline_expression:
                value = argument.values.inline_expression.service
                assignment = fake_tree.add_assignment(value)
                argument.replace(1, assignment.path)

    @classmethod
    def assignments(cls, block):
        """
        Process assignments, looking for inline expressions to replace,
        for example: a = alpine echo text:(random value)
        """
        for assignment in block.find_data('assignment'):
            service = assignment.node('assignment_fragment.service')
            if service:
                cls.inline_expressions(block, service)

    @classmethod
    def blocks(cls, tree):
        """
        Processes blocks, looking for trees that must be preprocessed.
        """
        for block in tree.find_data('block'):
            cls.assignments(block)
            service = block.node('service_block.service')
            if service:
                cls.inline_expressions(block, service)

    @classmethod
    def process(cls, tree):
        cls.blocks(tree)
        return tree
