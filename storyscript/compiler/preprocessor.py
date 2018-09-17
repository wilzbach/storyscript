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
    def replace_expression(fake_tree, parent, inline_expression):
        """
        Replaces an inline expression with a fake assignment
        """
        assignment = fake_tree.add_assignment(inline_expression.service)
        parent.replace(1, assignment.path)

    @classmethod
    def service_arguments(cls, block, service):
        """
        Processes the arguments of a service, replacing inline expressions
        """
        fake_tree = cls.fake_tree(block)
        for argument in service.find_data('arguments'):
            expression = argument.node('values.inline_expression')
            if expression:
                cls.replace_expression(fake_tree, argument, expression)

    @classmethod
    def assignment_expression(cls, block, tree):
        """
        Processess an assignment to an expression, replacing it
        """
        fake_tree = cls.fake_tree(block)
        parent = block.rules.assignment.assignment_fragment
        cls.replace_expression(fake_tree, parent, tree.inline_expression)

    @classmethod
    def assignments(cls, block):
        """
        Process assignments, looking for inline expressions, for example:
        a = alpine echo text:(random value) or a = (alpine echo message:'text')
        """
        for assignment in block.find_data('assignment'):
            fragment = assignment.assignment_fragment
            if fragment.service:
                cls.service_arguments(block, fragment.service)
            elif fragment.values:
                if fragment.values.inline_expression:
                    cls.assignment_expression(block, fragment.values)

    @classmethod
    def service(cls, tree):
        """
        Processes services, looking for inline expressions, for example:
        alpine echo text:(random value)
        """
        service = tree.node('service_block.service')
        if service:
            cls.service_arguments(tree, service)

    @classmethod
    def process(cls, tree):
        for block in tree.find_data('block'):
            cls.assignments(block)
            cls.service(block)
        return tree
