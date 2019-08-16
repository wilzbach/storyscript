# -*- coding: utf-8 -*-

from .FunctionResolver import FunctionResolver
from .Module import Module
from .SymbolResolver import SymbolResolver
from .TypeResolver import TypeResolver
from .functions.FunctionTable import FunctionTable
from .functions.MutationTable import MutationTable
from .symbols.Scope import Scope


class Semantics:
    """
    Performs semantic analysis on the AST
    """

    def __init__(self, features):
        root_scope = Scope.root()
        self.module = Module(
            symbol_resolver=SymbolResolver(scope=root_scope),
            function_table=FunctionTable(),
            mutation_table=MutationTable.init(),
            root_scope=root_scope,
            features=features
        )

    visitors = [FunctionResolver, TypeResolver]

    def process(self, tree):
        for visitor in self.visitors:
            v = visitor(module=self.module)
            v.visit(tree)
        return self.module
