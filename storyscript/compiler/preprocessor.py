# -*- coding: utf-8 -*-
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
    def merge_operands(cls, block, lhs, rhs):
        """
        Replaces the right hand-side operand and the right part of the left
        one with a fake assignment to a simpler expression.
        """
        fake_tree = cls.fake_tree(block)
        left_value = lhs.values
        if left_value is None:
            left_value = lhs
        right_value = rhs.child(1)
        args = (left_value, rhs.operator, right_value)
        expression = fake_tree.expression(*args)
        assignment = fake_tree.add_assignment(expression)
        children = len(lhs.children)
        if children == 1:
            lhs.replace(0, assignment.path.child(0))
            lhs.rename('path')
            return
        lhs.replace(children - 1, assignment.path)

    @classmethod
    def expression_stack(cls, block, tree):
        """
        Rebuilds the expression tree, replacing fragments according to the
        order that needs to be followed.
        """
        stack = []
        for child in tree.children:
            if child.operator:
                if child.operator.child(0) in ['*', '/', '%', '^']:
                    cls.merge_operands(block, stack[-1], child)
                else:
                    stack.append(child)
            else:
                stack.append(child)
        tree.children = stack

    @classmethod
    def expression(cls, block):
        for expression in block.find_data('expression'):
            if len(expression.children) > 2:
                cls.expression_stack(block, expression)

    @classmethod
    def if_statement(cls, block):
        """
        Processes if statements, looking inline expressions.
        """
        for statement in block.find_data('if_statement'):
            if statement.node('path_value.values.inline_expression'):
                cls.replace_pathvalue(block, statement)

    @classmethod
    def process(cls, tree):
        for block in tree.find_data('block'):
            cls.assignments(block)
            cls.service(block)
            cls.expression(block)
            cls.if_statement(block)
        return tree
