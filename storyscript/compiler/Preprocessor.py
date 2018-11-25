# -*- coding: utf-8 -*-
from .Faketree import FakeTree


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
    def replace_pathvalue(cls, block, statement, path_value):
        """
        Replaces an inline expression inside a path_value branch.
        """
        fake_tree = cls.fake_tree(block)
        line = statement.line()
        service = path_value.path.inline_expression.service
        assignment = fake_tree.add_assignment(service)
        path_value.replace(0, assignment.path)
        path_value.path.children[0].line = line

    @classmethod
    def service_arguments(cls, block, service):
        """
        Processes the arguments of a service, replacing inline expressions
        """
        fake_tree = cls.fake_tree(block)
        for argument in service.find_data('arguments'):
            expression = argument.node('path.inline_expression')
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
            elif fragment.path:
                if fragment.path.inline_expression:
                    cls.assignment_expression(block, fragment.path)

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
    def flow_statement(cls, name, block):
        """
        Processes if statements, looking inline expressions.
        """
        for statement in block.find_data(name):
            print(statement.pretty())
            if statement.node('path_value.path.inline_expression'):
                cls.replace_pathvalue(block, statement, statement.path_value)

            if statement.child(2):
                if statement.child(2).node('path.inline_expression'):
                    cls.replace_pathvalue(block, statement, statement.child(2))

    @classmethod
    def process(cls, tree):
        for block in tree.find_data('block'):
            cls.assignments(block)
            cls.service(block)
            cls.expression(block)
            cls.flow_statement('if_statement', block)
            cls.flow_statement('elseif_statement', block)
        return tree
