# -*- coding: utf-8 -*-
import re

from lark.lexer import Token

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
        return {'$OBJECT': 'path', 'paths': cls.names(tree)}

    @classmethod
    def mutation(cls, tree):
        """
        Compiles a mutation object, either from a mutation or a
        service_fragment tree.
        """
        mutation = tree.child(0).value
        arguments = []
        if tree.arguments:
            arguments = cls.arguments(tree.arguments)
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
        if token.type == 'FLOAT':
            return float(token.value)
        return int(token.value)

    @staticmethod
    def replace_fillers(string, matches):
        """
        Replaces filler values with '{}'
        """
        for match in matches:
            placeholder = '{}{}{}'.format('{', match, '}')
            string = string.replace(placeholder, '{}')
        return string

    @classmethod
    def fillers_values(cls, matches):
        values = []
        for match in matches:
            values.append(cls.path(Tree('path', [Token('WORD', match)])))
        return values

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
        Compiles a string tree. If the string has templated values, they
        are processed and compiled.
        """
        item = {'$OBJECT': 'string', 'string': cls.unescape_string(tree)}
        matches = re.findall(r'{([^}]*)}', item['string'])
        if matches == []:
            return item
        item['values'] = cls.fillers_values(matches)
        item['string'] = cls.replace_fillers(item['string'], matches)
        return item

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
                items.append(cls.values(value))
        return {'$OBJECT': 'list', 'items': items}

    @classmethod
    def objects(cls, tree):
        items = []
        for item in tree.children:
            child = item.child(0)
            if child.data == 'string':
                key = cls.string(child)
            elif child.data == 'path':
                key = cls.path(child)
            value = cls.values(item.child(1))
            items.append([key, value])
        return {'$OBJECT': 'dict', 'items': items}

    @classmethod
    def regular_expression(cls, tree):
        """
        Compiles a regexp object from a regular_expression tree
        """
        dictionary = {'$OBJECT': 'regexp', 'regexp': tree.child(0)}
        flags = tree.child(1)
        if flags:
            dictionary['flags'] = flags
        return dictionary

    @staticmethod
    def types(tree):
        return {'$OBJECT': 'type', 'type': tree.child(0).value}

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
        if subtree.type == 'NAME':
            return cls.path(tree)

    @classmethod
    def argument(cls, tree):
        """
        Compiles an argument tree to the corresponding object.
        """
        name = tree.child(0).value
        value = cls.values(tree.child(1))
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
    def expression_type(operator):
        types = {'+': 'sum', '-': 'subtraction', '^': 'exponential',
                 '*': 'multiplication', '/': 'division', '%': 'modulus',
                 'and': 'and', 'or': 'or', 'not': 'not'}
        return types[operator]

    @classmethod
    def expression(cls, tree):
        """
        Compiles an expression object with the given tree.
        """
        if tree.values:
            operator = tree.operator.child(0).child(0).value
            expression_type = Objects.expression_type(operator)
            values = [cls.values(tree.values), cls.values(tree.child(2))]
            return {'$OBJECT': 'expression', 'expression': expression_type,
                    'values': values}
        left_handside = cls.values(tree.path_value.child(0))
        comparison = tree.child(1)
        if comparison is None:
            return [left_handside]
        right_handside = cls.values(tree.child(2).child(0))
        expression = Objects.expression_type(comparison.child(0))
        return [{'$OBJECT': 'expression', 'expression': expression,
                'values': [left_handside, right_handside]}]
