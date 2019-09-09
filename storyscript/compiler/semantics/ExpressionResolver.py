# -*- coding: utf-8 -*-
from contextlib import contextmanager


from lark.lexer import Token

from storyscript.compiler.semantics.types.Types import AnyType, BaseType, \
    BooleanType, FloatType, IntType, ListType, MapType, ObjectType, \
    RegExpType, StringType, TimeType, explicit_cast
from storyscript.compiler.visitors.ExpressionVisitor import ExpressionVisitor
from storyscript.exceptions import CompilerError
from storyscript.parser import Tree

from .PathResolver import PathResolver
from .symbols.Symbols import Symbol, base_symbol


class SymbolExpressionVisitor(ExpressionVisitor):
    """
    Analyses the symbols of an expression.
    """

    def __init__(self, visitor):
        self.visitor = visitor
        super().__init__()

    @classmethod
    def is_cmp(cls, op):
        """
        Tests whether a binary operation requires comparison between types.
        """
        return op == 'LESSER' or op == 'LESSER_EQUAL'

    @classmethod
    def is_equal(cls, op):
        """
        Tests whether a binary operation requires equality comparison.
        """
        return op == 'EQUAL'

    @classmethod
    def is_boolean(cls, op):
        """
        Tests whether a binary operation involves boolean logic.
        """
        return op == 'AND' or op == 'OR' or op == 'NOT'

    @classmethod
    def op_returns_boolean(cls, op):
        """
        Checks whether a given operator is boolean.
        """
        return cls.is_cmp(op) or cls.is_equal(op) or cls.is_boolean(op)

    _arithmetic_types = {
        'PLUS': True, 'DASH': True, 'POWER': True, 'MULTIPLIER': True,
        'BSLASH': True, 'MODULUS': True
    }

    @classmethod
    def is_arithmetic_operator(cls, operator):
        """
        Checks whether a given operator is arithmetic.
        """
        return operator in cls._arithmetic_types

    @contextmanager
    def with_as_cast(self):
        """
        Context manager during as cast expression handling.
        """
        prev = self.visitor.with_as
        self.visitor.with_as = True
        yield
        self.visitor.with_as = prev

    def as_expression(self, tree, expr):
        assert tree.child(1).data == 'as_operator'
        # check for compatibility
        t = self.visitor.types(tree.child(1).types)
        tree.expect(explicit_cast(expr.type(), t.type()),
                    'type_operation_cast_incompatible',
                    left=expr.type(), right=t.type())
        return t

    def values(self, tree):
        return self.visitor.values(tree)

    @staticmethod
    def type_to_tree(tree, t):
        """
        Converts a type to its respective AST Tree representation.
        """
        if isinstance(t, ListType):
            inner = SymbolExpressionVisitor.type_to_tree(tree, t.inner)
            return Tree('list_type', [
                Tree('types', [inner])
            ])
        if isinstance(t, MapType):
            key = SymbolExpressionVisitor.type_to_tree(tree, t.key)
            value = SymbolExpressionVisitor.type_to_tree(tree, t.value)
            return Tree('map_type', [
                key,
                Tree('types', [value]),
            ])
        if t == BooleanType.instance():
            base_type = tree.create_token('BOOLEAN_TYPE', 'boolean')
        elif t == IntType.instance():
            base_type = tree.create_token('INTEGER_TYPE', 'int')
        elif t == FloatType.instance():
            base_type = tree.create_token('FLOAT_TYPE', 'float')
        elif t == StringType.instance():
            base_type = tree.create_token('STRING_TYPE', 'string')
        elif t == TimeType.instance():
            base_type = tree.create_token('TIME_TYPE', 'time')
        elif t == RegExpType.instance():
            base_type = tree.create_token('REGEXP_TYPE', 'regex')
        else:
            assert t == AnyType.instance()
            base_type = tree.create_token('ANY_TYPE', 'any')

        return Tree('base_type', [base_type])

    def nary_expression(self, tree, op, values):
        types = [v.type() for v in values]
        if self.op_returns_boolean(op.type):
            assert len(types) <= 2
            # e.g. a < b
            if self.is_cmp(op.type):
                target_type = types[0].cmp(types[1])
                tree.expect(target_type, 'type_operation_cmp_incompatible',
                            left=types[0], right=types[1])
                self.nary_args_implicit_cast(tree, target_type, types)
                return base_symbol(BooleanType.instance())

            # e.g. a == b
            if self.is_equal(op.type):
                target_type = types[0].equal(types[1])
                tree.expect(target_type,
                            'type_operation_equal_incompatible',
                            left=types[0], right=types[1])
                self.nary_args_implicit_cast(tree, target_type, types)
                return base_symbol(BooleanType.instance())

            # e.g. a and b, a or b, !a
            tree.expect(types[0].has_boolean(),
                        'type_operation_boolean_incompatible',
                        val=types[0])
            if len(types) == 2:
                tree.expect(types[1].has_boolean(),
                            'type_operation_boolean_incompatible',
                            val=types[1])
            return base_symbol(BooleanType.instance())

        is_arithmetic = self.is_arithmetic_operator(op.type)
        tree.expect(is_arithmetic, 'compiler_error_no_operator',
                    operator=op.type)
        target_type = types[0]
        for t in types[1:]:
            new_target_type = target_type.binary_op(t, op)
            tree.expect(new_target_type is not None,
                        'type_operation_incompatible',
                        left=target_type, right=t, op=op.value)
            target_type = new_target_type
        # add implicit casts
        if tree.kind == 'pow_expression':
            return base_symbol(target_type)
        if tree.kind == 'mul_expression':
            self.nary_args_implicit_cast(tree, target_type, types)
        else:
            assert tree.kind == 'arith_expression'
            self.nary_args_implicit_cast(tree, target_type, types)
        return base_symbol(target_type)

    @staticmethod
    def type_cast_expression(expr_node, target_type):
        """
        Type casts the given expr_node to the target_type.
        This is done by creating a new AST for the expr_node with an
        `as_operator`.

        Args:
            expr_node: Tree node representing an expression. This is the
                expression for which this function will generate a new
                expression node which also contains an `as_operator` to
                represent the type cast.
            target_type: The type to type cast given expression (expr_node)
                into. Must be a `types` node.

        Note: This does not perform any checks around feasibility of performing
        the type cast operation and depends upon the caller to have had
        performed these checks before making the call.
        """
        assert expr_node.data == 'expression'
        assert isinstance(target_type, BaseType)
        cast_type = SymbolExpressionVisitor.type_to_tree(
            expr_node,
            target_type
        )
        element = Tree('expression', [
            expr_node,
            Tree('as_operator', [
                Tree('types', [
                    cast_type
                ])
            ])
        ])
        element.kind = 'as_expression'
        return element

    def nary_args_implicit_cast(self, tree, target_type, source_types):
        """
        Cast nary_expression arguments implicitly.
        """
        if target_type == AnyType.instance():
            return
        for i, t in enumerate(source_types):
            if i > 0:
                # ignore the arith_operator tree child
                i += 1
            # check whether a tree child needs casting
            if t != target_type:
                tree.children[i] = self.type_cast_expression(
                    tree.children[i], target_type)


class ExpressionResolver:

    def __init__(self, module):
        self.expr_visitor = SymbolExpressionVisitor(self)
        # how to resolve existing symbols
        self.path_resolver = PathResolver(
            symbol_resolver=module.symbol_resolver
        )
        self.module = module
        self.with_as = False

    def path(self, tree):
        assert tree.data == 'path'
        return self.path_resolver.path(tree)

    def number(self, tree):
        """
        Compiles a number tree
        """
        assert tree.data == 'number'
        token = tree.child(0)
        if token.value[0] == '+':
            token.value = token.value[1:]
        if token.type == 'FLOAT':
            return base_symbol(FloatType.instance())
        return base_symbol(IntType.instance())

    def time(self, tree):
        """
        Compiles a time tree.
        """
        assert tree.data == 'time'
        return base_symbol(TimeType.instance())

    def string(self, tree):
        """
        Compiles a string tree.
        """
        assert tree.data == 'string'
        return base_symbol(StringType.instance())

    def boolean(self, tree):
        """
        Compiles a boolean tree.
        """
        assert tree.data == 'boolean'
        return base_symbol(BooleanType.instance())

    def list(self, tree):
        assert tree.data == 'list'
        value = None
        for i, c in enumerate(tree.children[1:]):
            if not isinstance(c, Tree):
                continue
            val = self.base_expression(c).type()
            if i >= 1:
                # type mismatch in the list
                if val != value:
                    value = AnyType.instance()
                    break
            else:
                value = val
        if not self.with_as:
            tree.expect(value is not None, 'list_type_no_any')
        if value is None:
            value = AnyType.instance()
        return base_symbol(ListType(value))

    def map(self, tree):
        assert tree.data == 'map'
        keys = []
        values = []
        for i, item in enumerate(tree.children):
            assert isinstance(item, Tree)
            key_child = item.child(0)
            if key_child.data == 'string':
                new_key = self.string(key_child).type()
            elif key_child.data == 'number':
                new_key = self.number(key_child).type()
            elif key_child.data == 'boolean':
                new_key = self.boolean(key_child).type()
            else:
                assert key_child.data == 'path'
                new_key = self.path(key_child).type()
            keys.append(new_key)
            values.append(self.base_expression(item.child(1)).type())

            # check all keys - even if they don't match
            key_child.expect(new_key.hashable(),
                             'type_key_not_hashable',
                             key=new_key)

        key = None
        value = None
        for i, p in enumerate(zip(keys, values)):
            new_key, new_value = p
            if i >= 1:
                # type mismatch in the list
                if key != new_key:
                    key = AnyType.instance()
                    break
                if value != new_value:
                    value = AnyType.instance()
                    break
            else:
                key = new_key
                value = new_value

        if not self.with_as:
            tree.expect(key is not None, 'map_type_no_any')
            tree.expect(value is not None, 'map_type_no_any')
        if key is None:
            key = AnyType.instance()
        if value is None:
            value = AnyType.instance()
        return base_symbol(MapType(key, value))

    def regular_expression(self, tree):
        """
        Compiles a regexp object from a regular_expression tree
        """
        assert tree.data == 'regular_expression'
        return base_symbol(RegExpType.instance())

    def types(self, tree):
        """
        Resolves a type expression to a type
        """
        assert tree.data == 'types'
        c = tree.first_child()
        if c.data == 'map_type':
            return self.map_type(c)
        elif c.data == 'list_type':
            return self.list_type(c)
        else:
            assert c.data == 'base_type'
            return self.base_type(c)

    def map_type(self, tree):
        """
        Resolves a map type expression to a type
        """
        assert tree.data == 'map_type'
        key_type = self.base_type(tree.child(0)).type()
        value_type = self.types(tree.child(1)).type()
        return base_symbol(MapType(key_type, value_type))

    def list_type(self, tree):
        """
        Resolves a list type expression to a type
        """
        assert tree.data == 'list_type'
        c = tree.first_child()
        item = self.types(c).type()
        return base_symbol(ListType(item))

    def base_type(self, tree):
        """
        Resolves a base type expression to a type
        """
        assert tree.data == 'base_type'
        tok = tree.first_child()
        if tok.type == 'BOOLEAN_TYPE':
            return base_symbol(BooleanType.instance())
        elif tok.type == 'INT_TYPE':
            return base_symbol(IntType.instance())
        elif tok.type == 'FLOAT_TYPE':
            return base_symbol(FloatType.instance())
        elif tok.type == 'STRING_TYPE':
            return base_symbol(StringType.instance())
        elif tok.type == 'ANY_TYPE':
            return base_symbol(AnyType.instance())
        elif tok.type == 'OBJECT_TYPE':
            return base_symbol(ObjectType.instance())
        elif tok.type == 'FUNCTION_TYPE':
            return base_symbol(AnyType.instance())
        elif tok.type == 'TIME_TYPE':
            return base_symbol(TimeType.instance())
        else:
            assert tok.type == 'REGEXP_TYPE'
            return base_symbol(RegExpType.instance())

    def values(self, tree):
        """
        Parses a values subtree
        """
        subtree = tree.child(0)
        if hasattr(subtree, 'data'):
            if subtree.data == 'string':
                return self.string(subtree)
            elif subtree.data == 'boolean':
                return self.boolean(subtree)
            elif subtree.data == 'list':
                return self.list(subtree)
            elif subtree.data == 'number':
                return self.number(subtree)
            elif subtree.data == 'time':
                return self.time(subtree)
            elif subtree.data == 'map':
                return self.map(subtree)
            elif subtree.data == 'regular_expression':
                return self.regular_expression(subtree)
            else:
                assert subtree.data == 'void'
                return base_symbol(AnyType.instance())

        assert subtree.type == 'NAME'
        return self.path(tree)

    def entity(self, tree):
        """
        Parses a entity subtree
        """
        assert tree.data == 'entity'
        return self.expr_visitor.entity(tree)

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.data == 'expression'
        return self.expr_visitor.expression(tree)

    def build_arguments(self, tree, fname, fn_type):
        args = {}
        for c in tree.extract('arguments'):
            tree.expect(len(c.children) >= 2, 'arg_name_required',
                        fn_type=fn_type, name=fname)
            name = c.child(0)
            type_ = self.expression(c.child(1)).type()
            sym = Symbol.from_path(name, type_)
            args[sym.name()] = (sym, c)
        return args

    def path_resolve_only_name(self, tree, fn_type):
        """
        Resolves only the first argument of a path.
        Errors if the path contains more children.
        """
        names = tree.children
        tree.expect(len(names) == 1, 'function_call_invalid_path',
                    fn_type=fn_type)
        return names[0].value

    def show_available_mutation_overloads(self, tree, overloads):
        """
        A mutation has multiple overloads, but none matches exactly.
        Thus, we show all of them to the user.
        """
        t = overloads.type()
        overload_list = []
        for me in overloads.all():
            overload = me.instantiate(t).pretty()
            if isinstance(t, AnyType):
                overload = f'{me.type()} {overload}'
            overload_list.append(overload)
        sep = '\n\t- '
        overload_list = sep + sep.join(overload_list)
        tree.mutation_fragment.expect(0, 'mutation_overload_mismatch',
                                      name=overloads.name(),
                                      overloads=overload_list)

    def resolve_mutation(self, s, tree):
        """
        Resolve a mutation on t with the MutationTable, instantiate it and
        check the caller arguments.
        """
        t = s.type()
        # a mutation on 'object' returns 'any' (for now)
        if t == ObjectType.instance():
            return base_symbol(AnyType.instance())

        name = tree.mutation_fragment.child(0).value
        args = self.build_arguments(tree.mutation_fragment, name,
                                    fn_type='Mutation')

        # a mutation on 'any' returns 'any'
        overloads = self.module.mutation_table.resolve(t, name)
        tree.expect(overloads is not None, 'mutation_invalid_name', name=name)
        ms = overloads.match(args.keys())
        if ms is None:
            # if there's only one overload, use this for a better error
            # message
            single = overloads.single()
            if single is None:
                self.show_available_mutation_overloads(tree, overloads)
            else:
                ms = [single]

        if len(ms) > 1:
            # a mutation on any might have matched multiple overloads
            return base_symbol(AnyType.instance())
        else:
            assert len(ms) == 1
            m = ms[0]
            m = m.instantiate(t)
            m.check_call(tree.mutation_fragment, args)
            return base_symbol(m.output())

    def resolve_function(self, tree):
        """
        Resolve a function with the FunctionTable and
        check the caller arguments.
        """
        tree.expect(tree.path.inline_expression is None,
                    'function_call_no_inline_expression')
        name = self.path_resolve_only_name(tree.path, fn_type='Function')
        fn = self.module.function_table.resolve(name)
        tree.expect(fn is not None, 'function_not_found', name=name)
        args = self.build_arguments(tree, name, fn_type='Function')
        fn.check_call(tree, args)
        return base_symbol(fn.output())

    def resolve_service(self, tree, output_sym=None):
        """
        Resolve a service using hub-sdk API and check the caller arguments.
        Params:
            tree: Service tree root node.
            output_sym: Symbol of the object output from when block
                in case of event based service.
        """
        service_name = tree.path.child(0).value
        action_node = tree.service_fragment.command
        tree.expect(action_node is not None, 'service_without_command')
        action_name = action_node.child(0).value
        args = self.build_arguments(
            tree.service_fragment,
            fname=service_name,
            fn_type='Service'
        )

        if output_sym is not None:
            return self.module.service_typing.resolve_service_output_object(
                tree,
                service_name,
                action_name,
                args,
                output_sym
            )

        return self.module.service_typing.resolve_service(
            tree, service_name, action_name, args)

    def check_service_fragment_arguments(self, tree):
        if tree.arguments:
            # if arguments are malformed (don't start with name)
            # then the user didn't specify a command
            first_arg_name = tree.arguments.children[0]
            tree.expect(isinstance(first_arg_name, Token) and
                        first_arg_name.type == 'NAME',
                        'service_without_command')

    def service(self, tree):
        # unknown for now
        if tree.service_fragment.output is not None:
            tree.service_fragment.output.expect(
                0, 'service_no_inline_output')

        command = tree.service_fragment.command
        tree.expect(command is not None, 'service_without_command')

        self.check_service_fragment_arguments(tree.service_fragment)

        t = None
        try:
            # check whether variable exists
            t = self.path(tree.path)
        except CompilerError:
            # ignore invalid variables (not existent or invalid)
            # -> must be a service
            return base_symbol(self.resolve_service(tree))

        # variable exists -> event-based service
        if t.type() == ObjectType.instance():
            # In case of event-based service resolve using output_sym.
            return base_symbol(self.resolve_service(tree, t))

        var_name = tree.path.child(0).value
        tree.path.expect(0, 'service_name_not_var', var=var_name)

    def mutation(self, tree):
        assert tree.expression is not None
        s = self.expression(tree.expression)
        return self.resolve_mutation(s, tree)

    def call_expression(self, tree):
        return self.resolve_function(tree)

    def base_expression(self, tree):
        """
        Compiles an soon to be expression object with the given tree.
        """
        assert tree.data == 'base_expression'
        child = tree.child(0)
        if child.data == 'expression':
            return self.expression(child)
        elif child.data == 'service':
            return self.service(child)
        elif child.data == 'mutation':
            return self.mutation(child)
        elif child.data == 'call_expression':
            return self.call_expression(child)
        else:
            assert child.data == 'path'
            return self.path(child)
