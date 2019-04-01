# -*- coding: utf-8 -*-


class ExpressionVisitor:
    """
    Visit an entire expression.
    """

    def nary_expression(self, tree):
        assert 0, 'Not implemented'

    def values(self, tree):
        assert 0, 'Not implemented'

    def entity(self, tree):
        """
        Compiles an entity expression with the given tree
        """
        return self.values(tree.child(0))

    def primary_expression(self, tree):
        """
        Compiles a primary expression object with the given tree.
        """
        if tree.child(0).data == 'entity':
            return self.entity(tree.entity)
        else:
            assert tree.child(0).data == 'or_expression'
            return self.or_expression(tree.child(0))

    def pow_expression(self, tree):
        """
        Compiles a pow expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'primary_expression'
            return self.primary_expression(tree.child(0))

        assert tree.child(1).type == 'POWER'
        values = [self.primary_expression(tree.child(0)),
                  self.unary_expression(tree.child(2))]
        return self.nary_expression(tree, tree.child(1), values)

    def unary_expression(self, tree):
        """
        Compiles an unary expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'pow_expression'
            return self.pow_expression(tree.child(0))

        assert tree.child(0).data == 'unary_operator'
        op = tree.unary_operator.child(0)
        return self.nary_expression(
                    tree, op,
                    [self.unary_expression(tree.child(1))])

    def mul_expression(self, tree):
        """
        Compiles a mul_expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'unary_expression'
            return self.unary_expression(tree.child(0))

        assert tree.child(1).data == 'mul_operator'
        op = tree.child(1).child(0)
        values = [self.mul_expression(tree.child(0)),
                  self.unary_expression(tree.child(2))]
        return self.nary_expression(tree, op, values)

    def arith_expression(self, tree):
        """
        Compiles a binary expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'mul_expression'
            return self.mul_expression(tree.child(0))

        assert len(tree.children) >= 3
        assert tree.child(1).data == 'arith_operator'
        op = tree.child(1).child(0)

        c0 = self.arith_expression(tree.child(0))
        cs = [self.mul_expression(n) for n in tree.children[2:]]
        return self.nary_expression(
            tree, op, values=[c0, *cs]
        )

    def cmp_expression(self, tree):
        """
        Compiles a comparison expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'arith_expression'
            return self.arith_expression(tree.child(0))

        assert tree.child(1).data == 'cmp_operator'
        op = tree.child(1).child(0)
        values = [self.cmp_expression(tree.child(0)),
                  self.arith_expression(tree.child(2))]
        return self.nary_expression(tree, op, values)

    def and_expression(self, tree):
        """
        Compiles an AND expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'cmp_expression'
            return self.cmp_expression(tree.child(0))

        assert tree.child(1).type == 'AND'
        op = tree.child(1)
        values = [self.and_expression(tree.child(0)),
                  self.cmp_expression(tree.child(2))]
        return self.nary_expression(tree, op, values)

    def or_expression(self, tree):
        """
        Compiles an OR expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'and_expression'
            return self.and_expression(tree.child(0))

        assert tree.child(1).type == 'OR'
        op = tree.child(1)
        values = [self.or_expression(tree.child(0)),
                  self.and_expression(tree.child(2))]
        return self.nary_expression(tree, op, values)

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.child(0).data == 'or_expression'
        return self.or_expression(tree.child(0))
