# -*- coding: utf-8 -*-
from contextlib import contextmanager


class ExpressionVisitor:
    """
    Visit an entire expression.
    """

    def nary_expression(self, tree):
        raise NotImplementedError()

    def values(self, tree):
        raise NotImplementedError()

    def to_expression(self, tree, expr):
        raise NotImplementedError()

    def entity(self, tree):
        """
        Compiles an entity expression with the given tree
        """
        return self.values(tree.child(0))

    @contextmanager
    def with_as_cast(self):
        """
        Context manager during as cast expression handling.
        """
        yield

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        first_child = tree.first_child()
        if len(tree.children) == 1:
            assert first_child.data == "entity"
            return self.entity(first_child)
        elif len(tree.children) == 2:
            second_child = tree.child(1)
            if second_child.data == "to_operator":
                with self.with_as_cast():
                    expr = self.expression(first_child)
                    return self.to_expression(tree, expr)
            # unary_expression
            op = first_child.child(0)  # unary_operator
            values = [self.expression(second_child)]
            return self.nary_expression(tree, op, values)
        else:
            assert len(tree.children) >= 3
            op = tree.child(1).child(0)
            values = [self.expression(first_child)]
            for child in tree.children[2:]:
                values.append(self.expression(child))
            return self.nary_expression(tree, op, values)
