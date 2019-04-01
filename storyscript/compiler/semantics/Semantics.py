# -*- coding: utf-8 -*-

from .TypeResolver import TypeResolver


class Semantics:
    """
    Performs semantic analysis on the AST
    """

    visitors = [TypeResolver]

    def process(self, tree):
        for visitor in self.visitors:
            visitor().visit(tree)
        return tree
