# -*- coding: utf-8 -*-

from storyscript.parser import Tree

from .ExpressionResolver import ExpressionResolver
from .FunctionTable import FunctionTable
from .PathResolver import PathResolver
from .ReturnVisitor import ReturnVisitor
from .SymbolResolver import SymbolResolver
from .symbols.Scope import Scope
from .symbols.SymbolTypes import AnyType, NoneType
from .symbols.Symbols import Symbol


class ScopeSelectiveVisitor:
    """
    A selective visitor which only visits defined nodes.
    visit_children must be called explicitly.
    """
    def visit(self, tree, scope=None):
        if hasattr(self, tree.data):
            return getattr(self, tree.data)(tree, scope)

    def visit_children(self, tree, scope):
        for c in tree.children:
            if isinstance(c, Tree):
                self.visit(c, scope)


class TypeResolver(ScopeSelectiveVisitor):
    """
    Tries to resolve the type of a variable or function call.
    """
    def __init__(self):
        self.symbol_resolver = SymbolResolver(scope=None)
        self.function_table = FunctionTable()
        self.resolver = ExpressionResolver(
            symbol_resolver=self.symbol_resolver,
            function_table=self.function_table,
        )
        self.path_symbol_resolver = SymbolResolver(
            scope=None, check_variable_existence=False)
        self.path_resolver = PathResolver(self.path_symbol_resolver)
        self.in_service_block = False
        self.in_when_block = False

    def assignment(self, tree, scope):
        self.symbol_resolver.update_scope(scope)
        self.path_symbol_resolver.update_scope(scope)

        target_symbol = self.path_resolver.path(tree.path)

        frag = tree.assignment_fragment
        expr_type = self.resolver.base_expression(frag.base_expression)

        if target_symbol.type() == NoneType.instance():
            if not target_symbol.is_internal():
                frag.base_expression.expect(expr_type != NoneType.instance(),
                                            'assignment_type_none')
            sym = Symbol(target_symbol.name(), expr_type)
            scope.symbols().insert(sym)
        else:
            tree.expect(target_symbol.type().can_be_assigned(expr_type),
                        'type_assignment_different',
                        target=target_symbol._type,
                        source=expr_type)

        self.visit_children(tree, scope)

    def rules(self, tree, scope):
        self.visit_children(tree, scope)

    def block(self, tree, scope):
        self.visit_children(tree, scope)

    def nested_block(self, tree, scope):
        tree.scope = Scope(parent=scope)
        self.visit_children(tree, scope=tree.scope)

    def foreach_block(self, tree, scope):
        """
        Create a new scope and add output variables to it
        """
        tree.scope = Scope(parent=scope)
        self.symbol_resolver.update_scope(tree.scope)

        stmt = tree.foreach_statement
        output_type = self.resolver.base_expression(stmt.base_expression)
        outputs = stmt.output.children
        nr_children = len(outputs)
        assert(nr_children > 0)  # given by the grammar

        iterable_types = output_type.output(nr_children)
        stmt.output.expect(iterable_types is not None,
                           'foreach_iterable_required',
                           target=output_type)
        stmt.output.expect(nr_children <= 2,
                           'foreach_output_children')

        for type_, output in zip(iterable_types, outputs):
            sym = Symbol.from_path(output, type_)
            tree.scope.insert(sym)

        for c in tree.nested_block.children:
            self.visit_children(c, scope=tree.scope)

    def while_block(self, tree, scope):
        self.visit_children(tree.nested_block, scope=scope)

    def when_block(self, tree, scope):
        tree.scope = Scope(parent=scope)
        self.symbol_resolver.update_scope(tree.scope)
        output = tree.service.service_fragment.output
        if output is not None:
            output.expect(len(output.children) == 1, 'output_type_only_one',
                          target='when')

            name = output.children[0]
            resolved = tree.scope.resolve(name)
            tree.expect(resolved is None, 'output_unique',
                        name=resolved.name() if resolved else None)
            sym = Symbol.from_path(name, AnyType.instance())
            tree.scope.insert(sym)

        tree.expect(not self.in_when_block, 'nested_when_block')
        self.in_when_block = True
        for c in tree.nested_block.children:
            self.visit_children(c, scope=tree.scope)
        self.in_when_block = False

    def service_block(self, tree, scope):
        tree.scope = Scope(parent=scope)
        self.symbol_resolver.update_scope(tree.scope)

        output = tree.service.service_fragment.output
        if output is not None:
            output.expect(len(output.children) == 1, 'output_type_only_one',
                          target='service')

            name = output.children[0]
            resolved = tree.scope.resolve(name)
            tree.expect(resolved is None, 'output_unique',
                        name=resolved.name() if resolved else None)
            sym = Symbol(name, AnyType.instance())
            tree.scope.insert(sym)

        tree.expect(not self.in_service_block, 'nested_service_block')
        self.in_service_block = True
        if tree.nested_block:
            for c in tree.nested_block.children:
                self.visit_children(c, scope=tree.scope)
        self.in_service_block = False

    def if_block(self, tree, scope):
        self.if_statement(tree, scope)
        for c in tree.children[2:]:
            self.visit(c, scope)

    def if_statement(self, tree, scope):
        """
        If blocks don't create a new scope.
        """
        if_statement = tree.if_statement
        self.symbol_resolver.update_scope(scope)
        self.resolver.base_expression(if_statement.base_expression)
        self.visit_children(tree.nested_block, scope=scope)

    def elseif_block(self, tree, scope):
        """
        Else if blocks don't create a new scope.
        """
        if_statement = tree.elseif_statement
        self.symbol_resolver.update_scope(scope)
        self.resolver.base_expression(if_statement.base_expression)
        self.visit_children(tree.nested_block, scope=scope)

    def else_block(self, tree, scope):
        """
        Else blocks don't create a new scope.
        """
        self.symbol_resolver.update_scope(scope)
        self.visit_children(tree.nested_block, scope=scope)

    def try_block(self, tree, scope):
        self.visit_children(tree.nested_block, scope=scope)
        for c in tree.children[2:]:
            self.visit(c, scope)

    def catch_block(self, tree, scope):
        self.visit_children(tree, scope=scope)

    def finally_block(self, tree, scope):
        self.visit_children(tree, scope=scope)

    def function_block(self, tree, scope):
        scope, return_type = self.function_statement(tree.function_statement,
                                                     scope)
        self.visit_children(tree.nested_block, scope=scope)
        ReturnVisitor.check(tree, scope, return_type, self.function_table)

    def function_statement(self, tree, scope):
        """
        Create a new scope _without_ a parent scope for this function.
        Prepopulate the scope with symbols from the function arguments.
        """
        scope = Scope.root()
        return_type = AnyType.instance()
        args = {}
        for c in tree.children[2:]:
            if isinstance(c, Tree) and c.data == 'typed_argument':
                name = c.child(0)
                sym = Symbol.from_path(name, self.resolver.types(c.types))
                scope.insert(sym)
                args[sym.name()] = sym
        # add function to the function table
        function_name = tree.child(1).value
        tree.expect(self.function_table.resolve(function_name) is None,
                    'function_redeclaration', name=function_name)
        output = tree.function_output
        if output is not None:
            output = self.resolver.types(output.types)
        self.function_table.insert(function_name, args, output)
        if tree.function_output:
            return_type = self.resolver.types(tree.function_output.types)
        return scope, return_type

    def start(self, tree, scope=None):
        # create the root scope
        tree.scope = Scope.root()
        self.visit_children(tree, scope=tree.scope)
