# -*- coding: utf-8 -*-
from storyscript.compiler.semantics.types.Types import NoneType
from storyscript.parser import Tree

from .ExpressionResolver import ExpressionResolver
from .Visitors import ScopeSelectiveVisitor
from .symbols.Scope import Scope
from .symbols.Symbols import Symbol


class FunctionResolver(ScopeSelectiveVisitor):
    """
    Populate the table of all function symbols before checking their calls
    in the next semantic run.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resolver = ExpressionResolver(
            symbol_resolver=None,
            function_table=self.function_table,
            mutation_table=self.mutation_table,
        )

    def block(self, tree, scope):
        self.visit_children(tree, scope)

    def function_block(self, tree, scope):
        tree.scope, return_type = self.function_statement(
            tree.function_statement, scope
        )

    def function_statement(self, tree, scope):
        """
        Create a new scope _without_ a parent scope for this function.
        Prepopulate the scope with symbols from the function arguments.
        """
        scope = Scope.root()
        return_type = NoneType.instance()
        args = {}
        for c in tree.children[2:]:
            if isinstance(c, Tree) and c.data == 'typed_argument':
                name = c.child(0)
                e_sym = self.resolver.types(c.types)
                sym = Symbol.from_path(name, e_sym.type())
                scope.insert(sym)
                args[sym.name()] = sym
        # add function to the function table
        function_name = tree.child(1).value
        tree.expect(self.function_table.resolve(function_name) is None,
                    'function_redeclaration', name=function_name)
        output = tree.function_output
        if output is not None:
            return_type = self.resolver.types(output.types).type()
        self.function_table.insert(function_name, args, return_type)
        return scope, return_type

    def start(self, tree, scope=None):
        self.visit_children(tree, scope=tree.scope)
