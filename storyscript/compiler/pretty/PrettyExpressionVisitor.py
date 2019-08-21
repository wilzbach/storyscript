# -*- coding: utf-8 -*-
from storyscript.compiler.visitors.ExpressionVisitor import ExpressionVisitor


class PrettyExpressionVisitor(ExpressionVisitor):
    """
    Serializes an expression as JSON
    """

    def __init__(self, visitor):
        self.visitor = visitor
        self.level = 0

    _types = {
        'PLUS': '+', 'DASH': '-', 'POWER': '^',
        'MULTIPLIER': '*', 'BSLASH': '/', 'MODULUS': '%',
        'AND': 'and', 'OR': 'or', 'NOT': 'not', 'EQUAL': '==',
        'GREATER': '>', 'LESSER': '<',
        'NOT_EQUAL': '!=',
        'GREATER_EQUAL': '>=',
        'LESSER_EQUAL': '<='
    }

    def expression_type(self, operator, tree):
        ret = self._types.get(operator, None)
        assert ret is not None
        return ret

    def values(self, tree):
        return self.visitor.values(tree)

    def nary_expression(self, tree, op, values):
        expr = self.expression_type(op.type, tree)
        if len(values) == 1:
            return f'{expr} {values[0]}'
        else:
            assert len(values) == 2
            return f'{values[0]} {expr} {values[1]}'

    def as_expression(self, tree, expr):
        assert tree.child(1).data == 'as_operator'
        expr = self.visitor.expression(tree.child(0))

        t = tree.child(1).child(0)
        if t.data == 'output_names':
            outputs = [c.value for c in t.children]
            output = ', '.join(outputs)
        else:
            assert t.data == 'types'
            output = self.visitor.types(t)

        return f'{expr} as {output}'

    def expression(self, tree):
        v = super().expression(tree)
        if getattr(tree, 'needs_parentheses', False):
            return f'({v})'
        else:
            return v
