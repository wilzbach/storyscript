# -*- coding: utf-8 -*-

from .FlowAnalyzer import FlowAnalyzer
from .FunctionResolver import FunctionResolver
from .Module import Module
from .ServiceTyping import ServiceTyping
from .SymbolResolver import SymbolResolver
from .TypeResolver import TypeResolver
from .functions.FunctionTable import FunctionTable
from .functions.MutationTable import MutationTable
from .symbols.Scope import Scope


class Semantics:
    """
    Performs semantic analysis on the AST
    """

    def __init__(self, storycontext, root_scope=None):
        if root_scope is None:
            root_scope = Scope.root()
        service_typing = ServiceTyping()

        self.module = Module(
            symbol_resolver=SymbolResolver(scope=root_scope),
            function_table=FunctionTable(),
            mutation_table=MutationTable.instance(),
            root_scope=root_scope,
            storycontext=storycontext,
            service_typing=service_typing,
        )

    visitors = [FunctionResolver, TypeResolver, FlowAnalyzer]

    def process(self, tree):
        for visitor in self.visitors:
            v = visitor(module=self.module)
            v.visit(tree, self.module.root_scope)
        return self.module
