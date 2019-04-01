# -*- coding: utf-8 -*-

from .ReturnVisitor import ReturnVisitor


class Semantics:
    """
    Performs semantic analysis on the AST
    """

    visitors = [ReturnVisitor]

    def process(self, tree):
        for visitor in self.visitors:
            visitor().visit(tree)
        return tree
