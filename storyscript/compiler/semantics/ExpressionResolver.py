# -*- coding: utf-8 -*-
from storyscript.compiler.lowering.utils import service_to_mutation
from storyscript.compiler.semantics.types.Types import AnyType, BooleanType, \
    FloatType, IntType, ListType, MapType, ObjectType, RegExpType, \
    StringType, TimeType
from storyscript.compiler.visitors.ExpressionVisitor import ExpressionVisitor
from storyscript.exceptions import CompilerError
from storyscript.parser import Tree

from .PathResolver import PathResolver
from .symbols.Symbols import Symbol


class SymbolExpressionVisitor(ExpressionVisitor):
    """
    Analyses the symbols of an expression.
    """

    def __init__(self, visitor):
        self.visitor = visitor

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

    def values(self, tree):
        return self.visitor.values(tree)

    def nary_expression(self, tree, op, values):
        if self.op_returns_boolean(op.type):
            assert len(values) <= 2
            # e.g. a < b
            if self.is_cmp(op.type):
                tree.expect(values[0].cmp(values[1]),
                            'type_operation_cmp_incompatible',
                            left=values[0], right=values[1])
                return BooleanType.instance()

            # e.g. a == b
            if self.is_equal(op.type):
                tree.expect(values[0].equal(values[1]),
                            'type_operation_equal_incompatible',
                            left=values[0], right=values[1])
                return BooleanType.instance()

            # e.g. a and b, a or b, !a
            tree.expect(values[0].has_boolean(),
                        'type_operation_boolean_incompatible',
                        val=values[0])
            if len(values) == 2:
                tree.expect(values[1].has_boolean(),
                            'type_operation_boolean_incompatible',
                            val=values[1])
            return BooleanType.instance()

        is_arithmetic = self.is_arithmetic_operator(op.type)
        tree.expect(is_arithmetic, 'compiler_error_no_operator',
                    operator=op.type)
        val = values[0]
        for c in values[1:]:
            new_val = val.binary_op(c, op)
            tree.expect(new_val is not None, 'type_operation_incompatible',
                        left=val, right=c, op=op.value)
            val = new_val
        return val


class ExpressionResolver:

    def __init__(self, symbol_resolver, function_table, mutation_table):
        self.expr_visitor = SymbolExpressionVisitor(self)
        # how to resolve existing symbols
        self.path_resolver = PathResolver(symbol_resolver=symbol_resolver)
        self.function_table = function_table
        self.mutation_table = mutation_table

    def path(self, tree):
        assert tree.data == 'path'
        return self.path_resolver.path(tree).type()

    def number(self, tree):
        """
        Compiles a number tree
        """
        assert tree.data == 'number'
        token = tree.child(0)
        if token.value[0] == '+':
            token.value = token.value[1:]
        if token.type == 'FLOAT':
            return FloatType.instance()
        return IntType.instance()

    def time(self, tree):
        """
        Compiles a time tree.
        """
        assert tree.data == 'time'
        return TimeType.instance()

    def string(self, tree):
        """
        Compiles a string tree.
        """
        assert tree.data == 'string'
        return StringType.instance()

    def boolean(self, tree):
        """
        Compiles a boolean tree.
        """
        assert tree.data == 'boolean'
        return BooleanType.instance()

    def list(self, tree):
        assert tree.data == 'list'
        value = None
        for i, c in enumerate(tree.children[1:]):
            if not isinstance(c, Tree):
                continue
            val = self.base_expression(c)
            if i >= 1:
                # type mismatch in the list
                if val != value:
                    value = AnyType.instance()
                    break
            else:
                value = val
        if value is None:
            value = AnyType.instance()
        return ListType(value)

    def map(self, tree):
        assert tree.data == 'map'
        keys = []
        values = []
        for i, item in enumerate(tree.children):
            assert isinstance(item, Tree)
            key_child = item.child(0)
            if key_child.data == 'string':
                new_key = self.string(key_child)
            elif key_child.data == 'number':
                new_key = self.number(key_child)
            elif key_child.data == 'boolean':
                new_key = self.boolean(key_child)
            else:
                assert key_child.data == 'path'
                new_key = self.path(key_child)
            keys.append(new_key)
            values.append(self.base_expression(item.child(1)))

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
        if key is None:
            key = AnyType.instance()
        if value is None:
            value = AnyType.instance()
        return MapType(key, value)

    def regular_expression(self, tree):
        """
        Compiles a regexp object from a regular_expression tree
        """
        assert tree.data == 'regular_expression'
        return RegExpType.instance()

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
        key_type = self.base_type(tree.child(0))
        value_type = self.types(tree.child(1))
        return MapType(key_type, value_type)

    def list_type(self, tree):
        """
        Resolves a list type expression to a type
        """
        assert tree.data == 'list_type'
        c = tree.first_child()
        item = self.types(c)
        return ListType(item)

    def base_type(self, tree):
        """
        Resolves a base type expression to a type
        """
        assert tree.data == 'base_type'
        tok = tree.first_child()
        if tok.type == 'BOOLEAN_TYPE':
            return BooleanType.instance()
        elif tok.type == 'INT_TYPE':
            return IntType.instance()
        elif tok.type == 'STRING_TYPE':
            return StringType.instance()
        elif tok.type == 'ANY_TYPE':
            return AnyType.instance()
        elif tok.type == 'OBJECT_TYPE':
            return ObjectType.instance()
        elif tok.type == 'FUNCTION_TYPE':
            return AnyType.instance()
        elif tok.type == 'TIME_TYPE':
            return TimeType.instance()
        else:
            assert tok.type == 'REGEXP_TYPE'
            return AnyType.instance()

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
                return AnyType.instance()

        assert subtree.type == 'NAME'
        return self.path(tree)

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.data == 'expression'
        assert tree.child(0).data == 'or_expression'
        return self.expr_visitor.expression(tree)

    def build_arguments(self, tree, name, fn_type):
        args = {}
        for c in tree.children[1:]:
            tree.expect(len(c.children) >= 2, 'arg_name_required',
                        fn_type=fn_type, name=name)
            name = c.child(0)
            type_ = self.expression(c.child(1))
            sym = Symbol.from_path(name, type_)
            args[sym.name()] = sym
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

    def resolve_any_mutation(self, name, args, tree):
        """
        Resolve a mutation on `any`.
        This is special as the normal mutation resolving process no longer
        applies and we can only check that at least one mutation with the
        given name and parameters exists.
        """
        return AnyType.instance()

    def resolve_mutation(self, t, tree):
        """
        Resolve a mutation on t with the MutationTable, instantiate it and
        check the caller arguments.
        """
        # a mutation on 'object' returns 'any' (for now)
        if t == AnyType.instance():
            return AnyType.instance()

        name = tree.mutation_fragment.child(0).value
        args = self.build_arguments(tree.mutation_fragment, name,
                                    fn_type='Mutation')

        # a mutation on 'any' returns 'any'
        overloads = self.mutation_table.resolve(t, name)
        tree.expect(overloads is not None, 'mutation_invalid_name', name=name)
        m = overloads.match(args.keys())
        if m is None:
            # multiple overloads, but no exact match
            overload_list = []
            for me in overloads.all():
                overload_list.append(me.instantiate(t).pretty())
            sep = '\n\t- '
            overload_list = sep + sep.join(overload_list)
            tree.mutation_fragment.expect(0, 'mutation_overload_mismatch',
                                          name=name,
                                          overloads=overload_list)
        m = m.instantiate(t)
        m.check_call(tree.mutation_fragment, args)
        return m.output()

    def resolve_function(self, tree):
        """
        Resolve a function with the FunctionTable and
        check the caller arguments.
        """
        tree.expect(tree.path.inline_expression is None,
                    'function_call_no_inline_expression')
        name = self.path_resolve_only_name(tree.path, fn_type='Function')
        fn = self.function_table.resolve(name)
        tree.expect(fn is not None, 'function_not_found', name=name)
        args = self.build_arguments(tree, name, fn_type='Function')
        fn.check_call(tree, args)
        return fn.output()

    def service(self, tree):
        # unknown for now
        if tree.service_fragment.output is not None:
            tree.service_fragment.output.expect(
                0, 'service_no_inline_output')
        try:
            # check whether variable exists
            t = self.path(tree.path)
            service_to_mutation(tree)
            return self.resolve_mutation(t, tree)
        except CompilerError as e:
            # ignore only invalid variables (must be services)
            if e.error == 'var_not_defined':
                return AnyType.instance()
            raise e

    def mutation(self, tree):
        if tree.path:
            t = self.path(tree.path)
        else:
            t = self.expr_visitor.primary_expression(
                tree.primary_expression
            )
        return self.resolve_mutation(t, tree)

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
