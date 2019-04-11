# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.compiler.visitors.ExpressionVisitor import ExpressionVisitor
from storyscript.parser import Tree

from .PathResolver import PathResolver
from .symbols.SymbolTypes import AnyType, BooleanType, \
    FloatType, IntType, ListType, ObjectType, StringType, TimeType
from .symbols.Symbols import Symbol


class SymbolExpressionVisitor(ExpressionVisitor):
    """
    Analyses the symbols of an expression.
    """

    def __init__(self, visitor):
        self.visitor = visitor

    _boolean_types = {
        'AND': True, 'OR': True, 'NOT': True, 'EQUAL': True, 'GREATER': True,
        'LESSER': True, 'NOT_EQUAL': True, 'GREATER_EQUAL': True,
        'LESSER_EQUAL': True,
    }

    @classmethod
    def is_boolean_operator(cls, operator):
        """
        Checks whether a given operator is boolean.
        """
        return operator in cls._boolean_types

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
        if self.is_boolean_operator(op.type):
            return BooleanType.instance()
        is_arithmetic = self.is_arithmetic_operator(op.type)
        tree.expect(is_arithmetic, 'compiler_error_no_operator',
                    operator=op.type)
        val = values[0]
        for c in values[1:]:
            new_val = val.op(c, op)
            tree.expect(new_val is not None, 'type_operation_incompatible',
                        left=val, right=c)
            val = new_val
        return val


class ExpressionResolver:

    def __init__(self, symbol_resolver, function_table):
        self.expr_visitor = SymbolExpressionVisitor(self)
        # how to resolve existing symbols
        self.path_resolver = PathResolver(symbol_resolver=symbol_resolver)
        self.function_table = function_table

    def path(self, tree):
        assert tree.data == 'path'
        return self.path_resolver.path(tree).type()

    def entity(self, tree):
        """
        Compiles an entity expression with the given tree
        """
        return self.expr_visitor.entity(tree)

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

    def objects(self, tree):
        assert tree.data == 'objects'
        key = None
        value = None
        for i, item in enumerate(tree.children):
            assert isinstance(item, Tree)
            child = item.child(0)
            if child.data == 'string':
                new_key = self.string(child)
            elif child.data == 'number':
                new_key = self.number(child)
            else:
                assert child.data == 'path'
                new_key = self.path(child)
            new_value = self.base_expression(item.child(1))
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
        return ObjectType(key, value)

    def regular_expression(self, tree):
        """
        Compiles a regexp object from a regular_expression tree
        """
        assert tree.data == 'regular_expression'
        return AnyType.instance()

    def types(self, tree):
        """
        Resolves a type expression to a type
        """
        assert tree.data == 'types'
        tok = tree.first_child()
        if tok.type == 'BOOLEAN_TYPE':
            return BooleanType.instance()
        elif tok.type == 'INT_TYPE':
            return IntType.instance()
        elif tok.type == 'STRING_TYPE':
            return StringType.instance()
        elif tok.type == 'ANY_TYPE':
            return AnyType.instance()
        elif tok.type == 'LIST_TYPE':
            return ListType(AnyType.instance())
        elif tok.type == 'OBJECT_TYPE':
            return ObjectType(AnyType.instance(), AnyType.instance())
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
            elif subtree.data == 'objects':
                return self.objects(subtree)
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

    def base_expression(self, tree):
        """
        Compiles an soon to be expression object with the given tree.
        """
        assert tree.data == 'base_expression'
        child = tree.child(0)
        if child.data == 'expression':
            return self.expression(child)
        elif child.data == 'service':
            # unknown for now
            if child.service_fragment.output is not None:
                child.service_fragment.output.expect(
                    0, 'service_no_inline_output')
            return AnyType.instance()
        elif child.data == 'mutation':
            # unknown for now
            return AnyType.instance()
        elif child.data == 'call_expression':
            tree.expect(child.path.inline_expression is None,
                        'function_call_no_inline_expression')
            names = child.path.children
            tree.expect(len(names) == 1, 'function_call_invalid_path')
            name = names[0].value
            fn = self.function_table.resolve(name)
            tree.expect(fn is not None, 'function_not_found', name=name)
            args = {}
            for c in child.children[1:]:
                name = c.child(0)
                type_ = self.expression(c.child(1))
                sym = Symbol.from_path(name, type_)
                args[sym.name()] = sym
            to_be_added = fn.check_call(child, args)
            for c in to_be_added:
                child.children.append(Tree('arguments', [
                    Token('NAME', c[0].name()),
                    c[1],
                ]))
            return fn.output()
        else:
            assert child.data == 'path'
            return self.path(child)
