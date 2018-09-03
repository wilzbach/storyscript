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
    def fake_tree(block):
        """
        Get a fake tree
        """
        return FakeTree(block)

    @staticmethod
    def replace_expression(fake_tree, argument):
        """
        Replaces an inline expression with a fake assignment
        """
        value = argument.values.inline_expression.service
        assignment = fake_tree.add_assignment(value)
        argument.replace(1, assignment.path)

    @classmethod
    def service_arguments(cls, block, service):
        """
        Processes the arguments of a service, replacing inline expressions
        """
        fake_tree = cls.fake_tree(block)
        for argument in service.find_data('arguments'):
            if argument.values.inline_expression:
                cls.replace_expression(fake_tree, argument)

    @classmethod
    def assignments(cls, block):
        """
        Process assignments, looking for inline expressions, for example:
        a = alpine echo text:(random value)
        """
        for assignment in block.find_data('assignment'):
            service = assignment.node('assignment_fragment.service')
            if service:
                cls.inline_expressions(block, service)

    @classmethod
    def service(cls, tree):
        """
        Processes services, looking for inline expressions, for example:
        alpine echo text:(random value)
        """
        service = tree.node('service_block.service')
        if service:
            cls.inline_expressions(tree, service)

    @classmethod
    def process(cls, tree):
        for block in tree.find_data('block'):
            cls.assignments(block)
            cls.service(block)
        return tree
