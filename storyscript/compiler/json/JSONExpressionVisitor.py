# -*- coding: utf-8 -*-
from storyscript.compiler.visitors.ExpressionVisitor import ExpressionVisitor


class JSONExpressionVisitor(ExpressionVisitor):
    """
    Serializes an expression as JSON
    """

    def __init__(self, visitor):
        self.visitor = visitor

    def expression_type(self, operator, tree):
        types = {'PLUS': 'sum', 'DASH': 'subtraction', 'POWER': 'exponential',
                 'MULTIPLIER': 'multiplication', 'BSLASH': 'division',
                 'MODULUS': 'modulus',
                 'AND': 'and', 'OR': 'or', 'NOT': 'not', 'EQUAL': 'equals',
                 'GREATER': 'greater', 'LESSER': 'less',
                 'NOT_EQUAL': 'not_equal',
                 'GREATER_EQUAL': 'greater_equal',
                 'LESSER_EQUAL': 'less_equal'}
        tree.expect(operator in types, 'compiler_error_no_operator',
                    operator=operator)
        return types[operator]

    def values(self, tree):
        return self.visitor.values(tree)

    def nary_expression(self, tree, op, values):
        expression = self.expression_type(op.type, tree)
        return {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': values,
        }
