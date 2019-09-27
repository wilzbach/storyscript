# -*- coding: utf-8 -*-
from storyhub.sdk.service.Action import Action as ServiceAction

from storyscript.compiler.semantics.types.Types import BooleanType, \
    NoneType, ObjectType, StringType
from storyscript.exceptions import expect
from storyscript.parser import Tree

from .ExpressionResolver import ExpressionResolver
from .PathResolver import PathResolver
from .ReturnVisitor import ReturnVisitor
from .SymbolResolver import SymbolResolver
from .Visitors import ScopeSelectiveVisitor
from .symbols.Scope import Scope, ScopeJoiner
from .symbols.Symbols import StorageClass, Symbol


class ScopeBlock:
    """
    Maintains the scope for a current block.
    At the end of a block, the previous scope will be restored.
    This means that scopes are essentially a single-linked list up to the root
    scope.
    """
    def __init__(self, type_resolver, scope, storage_class):
        assert scope is not None
        self.type_resolver = type_resolver
        self.scope = scope
        self.storage_class = storage_class

    def __enter__(self):
        if self.storage_class is not None:
            self.prev_storage_class = self.type_resolver.storage_class_scope
            self.type_resolver.storage_class_scope = self.storage_class
        self.prev_scope = self.type_resolver.current_scope
        self.type_resolver.update_scope(self.scope)
        return self.scope

    def __exit__(self, exc_type, exc_value, traceback):
        if self.storage_class is not None:
            self.type_resolver.storage_class_scope = self.prev_storage_class
        self.type_resolver.update_scope(self.prev_scope)


class TypeResolver(ScopeSelectiveVisitor):
    """
    Tries to resolve the type of a variable or function call.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resolver = ExpressionResolver(module=self.module)
        self.path_symbol_resolver = SymbolResolver(
            scope=None, check_variable_existence=False)
        self.path_resolver = PathResolver(self.path_symbol_resolver)
        # Service output object when inside a service block
        self.service_block_output = None
        self.in_when_block = False
        if self.module.features.globals:
            self.storage_class_scope = StorageClass.write()
        else:
            self.storage_class_scope = StorageClass.read()

    def assignment(self, tree, scope):
        target_symbol = self.path_resolver.path(tree.path)

        # allow rebindable assignments here
        tree.expect(target_symbol.can_assign(), 'readonly_type_assignment',
                    left=target_symbol.name())

        frag = tree.assignment_fragment
        expr_sym = self.resolver.base_expression(frag.base_expression)
        expr_type = expr_sym.type()
        storage_class = expr_sym._storage_class
        if expr_sym.can_write():
            storage_class = self.storage_class_scope

        token = frag.child(0)
        tree.expect('/' not in token.value,
                    'variables_backslash', token=token)
        tree.expect('/' not in token.value,
                    'variables_dash', token=token)

        if target_symbol.type() == NoneType.instance():
            can_assign = self.storage_class_scope.can_assign()
            storage_class = storage_class.declaration_from_symbol(
                rebindable=can_assign
            )
            if not target_symbol.is_internal():
                frag.base_expression.expect(expr_type != NoneType.instance(),
                                            'assignment_type_none')
            sym = Symbol(target_symbol.name(), expr_type,
                         storage_class=storage_class)
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
        self.visit_children(tree, scope)

    def absolute_expression(self, tree, scope):
        # resolve to perform checks
        self.resolver.expression(tree.expression)

    def implicit_output(self, tree):
        """
        Adds implicit output to a service.
        """
        fragment = tree.service.service_fragment
        if fragment and fragment.output is None and \
                tree.nested_block is not None:
            command = fragment.command
            if command:
                command = command.child(0)
            else:
                command = tree.service.path.child(0)
            output = Tree('output', [command])
            fragment.children.append(output)

    def foreach_block(self, tree, scope):
        """
        Create a new scope and add output variables to it
        """
        tree.scope = Scope(parent=scope)
        with self.create_scope(tree.scope, storage_class=StorageClass.write()):
            stmt = tree.foreach_statement
            output_expr = self.resolver.base_expression(stmt.base_expression)
            output_type = output_expr.type()
            stmt.expect(stmt.output is not None, 'foreach_output_required')
            outputs = stmt.output.children
            nr_children = len(outputs)
            stmt.expect(nr_children > 0, 'foreach_output_required')

            iterable_types = output_type.output(nr_children)
            stmt.output.expect(iterable_types is not None,
                               'foreach_iterable_required',
                               target=output_type)
            stmt.output.expect(nr_children <= 2,
                               'foreach_output_children')

            for i, type_, output in zip(range(nr_children), iterable_types,
                                        outputs):
                sym = Symbol.from_path(output, type_)
                s = tree.scope.resolve(output)
                expect(s is None, 'output_assignment_existing_var',
                       token=outputs[i],
                       var=output)
                tree.scope.insert(sym)

            for c in tree.nested_block.children:
                self.visit_children(c, scope=tree.scope)

    def while_block(self, tree, scope):
        self.while_statement(tree.while_statement, scope)
        tree.scope = Scope(parent=scope)
        with self.create_scope(tree.scope, storage_class=StorageClass.write()):
            self.visit_children(tree.nested_block, scope=tree.scope)

    def while_statement(self, tree, scope):
        """
        Checks the inside of while statements
        """
        self.resolver.base_expression(tree.base_expression)

    def check_output(self, tree, output, output_type, target):
        output.expect(len(output.children) == 1, 'output_type_only_one',
                      target=target)

        name = output.children[0]
        resolved = tree.scope.resolve(name)
        output.expect(resolved is None, 'output_unique',
                      name=resolved.name() if resolved else None)
        sym = Symbol.from_path(name, output_type,
                               storage_class=StorageClass.rebindable())
        tree.scope.insert(sym)

    def when_block(self, tree, scope):
        tree.expect(not self.in_when_block, 'nested_when_block')
        tree.scope = Scope(parent=scope)
        self.implicit_output(tree)

        listener_name = tree.service.path.child(0).value
        event_node = tree.service.service_fragment.command
        if event_node is None:
            tree.expect(self.service_block_output is not None,
                        'when_no_output_parent')
            event_node = tree.service.path
            listener_name = self.service_block_output.child(0).value

        event_name = event_node.child(0).value

        if self.service_block_output is not None:
            service_output_name = self.service_block_output.child(0).value
            # If when is nested in service block, it should be listening to
            # events defined for actions in that service only.
            tree.expect(listener_name == service_output_name,
                        'event_not_defined',
                        event=event_name, output=listener_name)

        listener_sym = scope.resolve(listener_name)
        tree.expect(
            listener_sym is not None and
            isinstance(listener_sym.type(), ObjectType) and
            listener_sym.type().object() is not None,
            'event_not_defined',
            event=event_name, output=listener_name)

        listener = listener_sym.type().object()
        tree.expect(isinstance(listener, ServiceAction),
                    'object_expect_action', var=listener_name)
        args = self.resolver.build_arguments(
            tree.service.service_fragment,
            fname=event_name,
            fn_type='Service Event',
        )
        output_type = self.module.service_typing.resolve_service_event(
            tree,
            listener,
            event_name,
            args
        )

        output = tree.service.service_fragment.output
        self.check_output(tree, output, output_type, target='when')

        with self.create_scope(tree.scope, storage_class=StorageClass.write()):
            self.in_when_block = True
            for c in tree.nested_block.children:
                self.visit_children(c, scope=tree.scope)
            self.in_when_block = False

    def service_block(self, tree, scope):
        service_path = tree.service.path
        service_name = service_path.child(0).value
        name = scope.resolve(service_name)

        # Whitespace syntax for mutations is not allowed anymore.
        service_path.expect(
            name is None or isinstance(name.type(), ObjectType),
            'service_name_not_var', var=service_name)

        action_node = tree.service.service_fragment.command
        tree.expect(action_node is not None, 'service_without_command')
        action_name = action_node.child(0).value

        # check for malformed arguments
        self.resolver.check_service_fragment_arguments(
            tree.service.service_fragment
        )

        args = self.resolver.build_arguments(
            tree.service.service_fragment,
            fn_type='Service',
            fname=service_name,
        )

        if name is None:
            output_type = self.module.service_typing.resolve_service(
                tree.service,
                service_name,
                action_name,
                args,
                nested_block=True
            )
        else:
            output_type = self.module.service_typing. \
                resolve_service_output_object(
                    tree,
                    service_name,
                    action_name,
                    args,
                    name
                )

        tree.scope = Scope(parent=scope)

        self.implicit_output(tree)
        output = tree.service.service_fragment.output
        if output is not None:
            self.check_output(tree, output, output_type, target='service')

        if tree.nested_block:
            with self.create_scope(tree.scope):
                tree.expect(self.service_block_output is None,
                            'nested_service_block')
                # In case of nested_block, we will always have output
                self.service_block_output = output
                for c in tree.nested_block.children:
                    self.visit_children(c, scope=tree.scope)
                self.service_block_output = None
        else:
            tree.service.service_fragment.expect(output is None,
                                                 'service_no_inline_output')

    def concise_when_block(self, tree, scope):
        tree.expect(0, 'nested_when_block')

    def if_block(self, tree, scope):
        self.if_statement(tree.if_statement, scope)
        scope_joiner = ScopeJoiner()

        with self.create_scope(Scope(parent=scope)) as if_scope:
            self.visit_children(tree.nested_block, scope=if_scope)
            scope_joiner.add(if_scope)

        for c in tree.children[2:]:
            with self.create_scope(Scope(parent=scope)) as if_scope:
                self.visit(c, scope=if_scope)
                scope_joiner.add(if_scope)

        # An if without 'else' won't cover all codepaths
        if tree.else_block is not None:
            scope_joiner.insert_to(tree, scope)

    def if_statement(self, tree, scope):
        """
        If blocks don't create a new scope.
        """
        self.ensure_boolean_expression(tree, tree.base_expression)

    def elseif_block(self, tree, scope):
        """
        Else if blocks don't create a new scope.
        """
        self.ensure_boolean_expression(
            tree,
            tree.elseif_statement.base_expression,
        )
        self.visit_children(tree.nested_block, scope=scope)

    def else_block(self, tree, scope):
        """
        Else blocks don't create a new scope.
        """
        self.visit_children(tree.nested_block, scope=scope)

    def ensure_boolean_expression(self, tree, expr):
        """
        Ensures that the expression resolves to a boolean.
        """
        t = self.resolver.base_expression(expr).type()
        expr.expect(t == BooleanType.instance(),
                    'if_expression_boolean', type=t)

    def try_block(self, tree, scope):
        scope_joiner = ScopeJoiner()
        with self.create_scope(Scope(parent=scope)) as try_scope:
            self.visit_children(tree.nested_block, scope=try_scope)
            scope_joiner.add(try_scope)

        if tree.catch_block is not None:
            with self.create_scope(Scope(parent=scope)) as try_scope:
                self.visit(tree.catch_block, try_scope)
                scope_joiner.add(try_scope)

            # only variables declared in both try/catch should be moved in the
            # parent scope
            scope_joiner.insert_to(tree, scope)

        # finally block operates on the parent scope
        if tree.finally_block is not None:
            self.visit(tree.finally_block, scope)

    def catch_block(self, tree, scope):
        catch_stmt = tree.catch_statement
        tree.catch_statement.expect(
            len(catch_stmt.children) == 1,
            'catch_no_output')
        self.visit_children(tree, scope=scope)

    def finally_block(self, tree, scope):
        self.visit_children(tree, scope=scope)

    def throw_statement(self, tree, scope):
        tree.expect(tree.entity is not None,
                    'throw_only_string')
        sym = self.resolver.entity(tree.entity)
        tree.entity.expect(sym.type() == StringType.instance(),
                           'throw_only_string')

    def function_block(self, tree, scope):
        tree.scope, return_type = self.function_statement(
            tree.function_statement, scope
        )
        with self.create_scope(tree.scope, storage_class=StorageClass.write()):
            self.visit_children(tree.nested_block, scope=tree.scope)
            ReturnVisitor.check(tree, tree.scope, return_type, self.module)

    def function_statement(self, tree, scope):
        """
        Create a new scope _without_ a parent scope for this function.
        Prepopulate the scope with symbols from the function arguments.
        """
        scope = Scope(parent=scope)
        function_name = tree.child(1).value
        function = self.module.function_table.resolve(function_name)
        for arg, sym in function._args.items():
            scope.insert(sym)
        return scope, function._output

    def update_scope(self, scope):
        """
        Updates the current scope for the respective resolvers.
        """
        self.current_scope = scope
        self.module.symbol_resolver.update_scope(scope)
        self.path_symbol_resolver.update_scope(scope)

    def create_scope(self, scope, storage_class=None):
        return ScopeBlock(self, scope, storage_class)

    def start(self, tree, scope=None):
        # create the root scope
        tree.scope = Scope.root()
        self.update_scope(tree.scope)
        self.visit_children(tree, scope=tree.scope)
