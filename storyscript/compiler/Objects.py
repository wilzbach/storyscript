# -*- coding: utf-8 -*-
from lark.lexer import Token

from ..exceptions import internal_assert
from ..parser import Tree


class Objects:

    @classmethod
    def names(cls, tree):
        """
        Extracts names from a path tree
        """
        names = [tree.child(0).value]
        for fragment in tree.children[1:]:
            child = fragment.child(0)
            value = child.value
            if isinstance(child, Tree):
                if child.data == 'string':
                    value = cls.string(child)
                elif child.data == 'path':
                    value = cls.path(child)
            names.append(value)
        return names

    @classmethod
    def path(cls, tree):
        paths = cls.names(tree)
        for p in paths:
            if not isinstance(p, str) or p.startswith('__p-'):
                continue
            tree.expect('-' not in p,
                        'path_name_invalid_char', path=p, token='-')
            tree.expect('/' not in p,
                        'path_name_invalid_char', path=p, token='/')
        return {'$OBJECT': 'path', 'paths': paths}

    @classmethod
    def mutation(cls, tree):
        entity = Objects.entity(tree.entity)
        args = Objects.mutation_fragment(tree.mutation_fragment)
        return {'method': 'mutation', 'name': [entity], 'args': [args]}

    @classmethod
    def mutation_fragment(cls, tree):
        """
        Compiles a mutation object, either from a mutation or a
        service_fragment tree.
        """
        mutation = tree.child(0).value
        arguments = []
        if tree.arguments:
            arguments = cls.arguments(tree)
        if tree.command:
            mutation = tree.command.child(0).value
        return {'$OBJECT': 'mutation', 'mutation': mutation,
                'arguments': arguments}

    @staticmethod
    def number(tree):
        """
        Compiles a number tree
        """
        token = tree.child(0)
        if token.value[0] == '+':
            token.value = token.value[1:]
        if token.type == 'FLOAT':
            return {'$OBJECT': 'float', 'float': float(token.value)}
        return {'$OBJECT': 'int', 'int': int(token.value)}

    @staticmethod
    def name_to_path(name):
        """
        Builds the tree for a name or dotted name.
        """
        names = name.split('.')
        tree = Tree('path', [Token('NAME', names[0])])
        if len(names) > 1:
            for name in names[1:]:
                fragment = Tree('path_fragment', [Token('NAME', name)])
                tree.children.append(fragment)
        return tree

    @staticmethod
    def unescape_string(tree):
        """
        Unescapes a string tree, returning the real string.
        """
        string = tree.child(0).value[1:-1]
        unescaped = string.encode('utf-8').decode('unicode_escape')
        return unescaped.encode('latin1').decode()

    @classmethod
    def string(cls, tree):
        """
        Compiles a string tree.
        """
        return {'$OBJECT': 'string', 'string': cls.unescape_string(tree)}

    @staticmethod
    def boolean(tree):
        if tree.child(0).value == 'true':
            return True
        return False

    @classmethod
    def list(cls, tree):
        items = []
        for value in tree.children:
            if isinstance(value, Tree):
                items.append(cls.base_expression(value))
        return {'$OBJECT': 'list', 'items': items}

    @classmethod
    def objects(cls, tree):
        items = []
        for item in tree.children:
            child = item.child(0)
            if child.data == 'string':
                key = cls.string(child)
            else:
                internal_assert(child.data == 'path')
                key = cls.path(child)
            value = cls.base_expression(item.child(1))
            items.append([key, value])
        return {'$OBJECT': 'dict', 'items': items}

    @classmethod
    def regular_expression(cls, tree):
        """
        Compiles a regexp object from a regular_expression tree
        """
        dictionary = {'$OBJECT': 'regexp', 'regexp': tree.child(0)}
        if len(tree.children) > 1:
            dictionary['flags'] = tree.child(1)
        return dictionary

    @staticmethod
    def types(tree):
        return {'$OBJECT': 'type', 'type': tree.child(0).value}

    @classmethod
    def entity(cls, tree):
        return cls.values(tree.child(0))

    @classmethod
    def values(cls, tree):
        """
        Parses a values subtree
        """
        subtree = tree.child(0)
        if hasattr(subtree, 'data'):
            if subtree.data == 'string':
                return cls.string(subtree)
            elif subtree.data == 'boolean':
                return cls.boolean(subtree)
            elif subtree.data == 'list':
                return cls.list(subtree)
            elif subtree.data == 'number':
                return cls.number(subtree)
            elif subtree.data == 'objects':
                return cls.objects(subtree)
            elif subtree.data == 'regular_expression':
                return cls.regular_expression(subtree)
            elif subtree.data == 'types':
                return cls.types(subtree)
            elif subtree.data == 'void':
                return None

        internal_assert(subtree.type == 'NAME')
        return cls.path(tree)

    @classmethod
    def argument(cls, tree):
        """
        Compiles an argument tree to the corresponding object.
        """
        name = tree.child(0).value
        value = cls.expression(tree.child(1))
        return {'$OBJECT': 'argument', 'name': name, 'argument': value}

    @classmethod
    def arguments(cls, tree):
        """
        Parses a group of arguments rules
        """
        arguments = []
        for argument in tree.find_data('arguments'):
            arguments.append(cls.argument(argument))
        return arguments

    @classmethod
    def typed_argument(cls, tree):
        name = tree.child(0).value
        value = cls.values(Tree('anon', [tree.child(1)]))
        return {'$OBJECT': 'argument', 'name': name, 'argument': value}

    @classmethod
    def function_arguments(cls, tree):
        arguments = []
        for argument in tree.find_data('typed_argument'):
            arguments.append(cls.typed_argument(argument))
        return arguments

    @staticmethod
    def expression_type(operator, tree):
        types = {'PLUS': 'sum', 'DASH': 'subtraction', 'POWER': 'exponential',
                 'MULTIPLIER': 'multiplication', 'BSLASH': 'division',
                 'MODULUS': 'modulus',
                 'AND': 'and', 'OR': 'or', 'NOT': 'not', 'EQUAL': 'equals',
                 'GREATER': 'greater', 'LESSER': 'less',
                 'NOT_EQUAL': 'not_equal',
                 'GREATER_EQUAL': 'greater_equal',
                 'LESSER_EQUAL': 'less_equal'}
        tree.expect(operator in types, 'compiler_error_no_operator',
                    operator=operator)
        return types[operator]

    @classmethod
    def expression(cls, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.child(0).data == 'or_expression'
        return cls.or_expression(tree.child(0))

    @classmethod
    def absolute_expression(cls, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.child(0).data == 'expression'
        return cls.expression(tree.child(0))

    @classmethod
    def base_expression(cls, tree):
        """
        Compiles an soon to be expression object with the given tree.
        """
        child = tree.child(0)
        if child.data == 'expression':
            return cls.expression(child)
        else:
            assert child.data == 'path'
            return cls.path(child)

    @classmethod
    def build_unary_expression(cls, tree, op, left):
        expression_type = Objects.expression_type(op.type, tree)
        return {
            '$OBJECT': 'expression',
            'expression': expression_type,
            'values':  [left],
        }

    @classmethod
    def build_binary_expression(cls, tree, op, left, right):
        expression = Objects.expression_type(op.type, tree)
        return {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': [left, right],
        }

    @classmethod
    def primary_expression(cls, tree):
        """
        Compiles a primary expression object with the given tree.
        """
        if tree.child(0).data == 'entity':
            return cls.entity(tree.entity)
        else:
            assert tree.child(0).data == 'or_expression'
            return cls.or_expression(tree.child(0))

    @classmethod
    def pow_expression(cls, tree):
        """
        Compiles a pow expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'primary_expression'
            return cls.primary_expression(tree.child(0))

        assert tree.child(1).type == 'POWER'
        return cls.build_binary_expression(
                    tree, tree.child(1),
                    cls.primary_expression(tree.child(0)),
                    cls.unary_expression(tree.child(2)))

    @classmethod
    def unary_expression(cls, tree):
        """
        Compiles an unary expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'pow_expression'
            return cls.pow_expression(tree.child(0))

        assert tree.child(0).data == 'unary_operator'
        op = tree.unary_operator.child(0)
        return cls.build_unary_expression(
                    tree, op,
                    cls.unary_expression(tree.child(1)))

    @classmethod
    def mul_expression(cls, tree):
        """
        Compiles a mul_expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'unary_expression'
            return cls.unary_expression(tree.child(0))

        assert tree.child(1).data == 'mul_operator'
        op = tree.child(1).child(0)
        return cls.build_binary_expression(
                    tree, op,
                    cls.mul_expression(tree.child(0)),
                    cls.unary_expression(tree.child(2)))

    @classmethod
    def arith_expression(cls, tree):
        """
        Compiles a binary expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'mul_expression'
            return cls.mul_expression(tree.child(0))

        assert len(tree.children) >= 3
        assert tree.child(1).data == 'arith_operator'
        op = tree.child(1).child(0)

        expression = Objects.expression_type(op.type, tree)
        c0 = cls.arith_expression(tree.child(0))
        cs = [cls.mul_expression(n) for n in tree.children[2:]]
        return {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': [c0, *cs]
        }

    @classmethod
    def cmp_expression(cls, tree):
        """
        Compiles a comparison expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'arith_expression'
            return cls.arith_expression(tree.child(0))

        assert tree.child(1).data == 'cmp_operator'
        op = tree.child(1).child(0)
        return cls.build_binary_expression(
                    tree, op,
                    cls.cmp_expression(tree.child(0)),
                    cls.arith_expression(tree.child(2)))

    @classmethod
    def and_expression(cls, tree):
        """
        Compiles an AND expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'cmp_expression'
            return cls.cmp_expression(tree.child(0))

        assert tree.child(1).type == 'AND'
        op = tree.child(1)
        return cls.build_binary_expression(
                    tree, op,
                    cls.and_expression(tree.child(0)),
                    cls.cmp_expression(tree.child(2)))

    @classmethod
    def or_expression(cls, tree):
        """
        Compiles an OR expression object with the given tree.
        """
        if len(tree.children) == 1:
            assert tree.child(0).data == 'and_expression'
            return cls.and_expression(tree.child(0))

        assert tree.child(1).type == 'OR'
        op = tree.child(1)
        return cls.build_binary_expression(
                    tree, op,
                    cls.or_expression(tree.child(0)),
                    cls.and_expression(tree.child(2)))
