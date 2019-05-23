# -*- coding: utf-8 -*-

from .FunctionResolver import FunctionResolver
from .TypeResolver import TypeResolver
from .functions.FunctionTable import FunctionTable
from .functions.MutationTable import MutationTable


class Semantics:
    """
    Performs semantic analysis on the AST
    """

    visitors = [FunctionResolver, TypeResolver]

    def process(self, tree):
        self.function_table = FunctionTable()
        self.mutation_table = MutationTable.init()
        for visitor in self.visitors:
            v = visitor(function_table=self.function_table,
                        mutation_table=self.mutation_table)
            v.visit(tree)
        return tree
