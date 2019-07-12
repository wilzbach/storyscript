# -*- coding: utf-8 -*-


class ExpressionVisitor:
    """
    Visit an entire expression.
    """

    def nary_expression(self, tree):
        raise NotImplementedError()

    def values(self, tree):
        raise NotImplementedError()

    def as_expression(self, tree, expr):
        raise NotImplementedError()

    def entity(self, tree):
        """
        Compiles an entity expression with the given tree
        """
        return self.values(tree.child(0))

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        first_child = tree.first_child()
        if len(tree.children) == 1:
            assert first_child.data == 'entity'
            return self.entity(first_child)
        elif len(tree.children) == 2:
            second_child = tree.child(1)
            if second_child.data == 'as_operator':
                expr = self.expression(first_child)
                return self.as_expression(tree, expr)
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
