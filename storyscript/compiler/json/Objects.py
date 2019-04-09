# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.exceptions import internal_assert
from storyscript.parser import Tree

from .JSONExpressionVisitor import JSONExpressionVisitor


class Objects:

    def __init__(self):
        self.expr_visitor = JSONExpressionVisitor(visitor=self)

    def names(self, tree):
        """
        Extracts names from a path tree
        """
        names = [tree.child(0).value]
        for fragment in tree.children[1:]:
            child = fragment.child(0)
            value = child.value
            if isinstance(child, Tree):
                if child.data == 'string':
                    value = self.string(child)
                elif child.data == 'path':
                    value = self.path(child)
            names.append(value)
        return names

    def path(self, tree):
        paths = self.names(tree)
        for p in paths:
            if not isinstance(p, str) or p.startswith('__p-'):
                continue
            tree.expect('-' not in p,
                        'path_name_invalid_char', path=p, token='-')
            tree.expect('/' not in p,
                        'path_name_invalid_char', path=p, token='/')
        return {'$OBJECT': 'path', 'paths': paths}

    def mutation(self, tree):
        entity = self.entity(tree.entity)
        args = self.mutation_fragment(tree.mutation_fragment)
        return {'method': 'mutation', 'name': [entity], 'args': [args]}

    def mutation_fragment(self, tree):
        """
        Compiles a mutation object, either from a mutation or a
        service_fragment tree.
        """
        mutation = tree.child(0).value
        arguments = []
        if tree.arguments:
            arguments = self.arguments(tree)
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

    def string(self, tree):
        """
        Compiles a string tree.
        """
        return {'$OBJECT': 'string', 'string': self.unescape_string(tree)}

    @staticmethod
    def boolean(tree):
        if tree.child(0).value == 'true':
            return {'$OBJECT': 'boolean', 'boolean': True}
        return {'$OBJECT': 'boolean', 'boolean': False}

    def list(self, tree):
        items = []
        for value in tree.children:
            if isinstance(value, Tree):
                items.append(self.base_expression(value))
        return {'$OBJECT': 'list', 'items': items}

    def objects(self, tree):
        items = []
        for item in tree.children:
            child = item.child(0)
            if child.data == 'string':
                key = self.string(child)
            elif child.data == 'number':
                key = self.number(child)
            else:
                internal_assert(child.data == 'path')
                key = self.path(child)
            value = self.base_expression(item.child(1))
            items.append([key, value])
        return {'$OBJECT': 'dict', 'items': items}

    def regular_expression(self, tree):
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

    def entity(self, tree):
        return self.values(tree.child(0))

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
            elif subtree.data == 'objects':
                return self.objects(subtree)
            elif subtree.data == 'regular_expression':
                return self.regular_expression(subtree)
            elif subtree.data == 'types':
                return self.types(subtree)
            elif subtree.data == 'void':
                return None

        internal_assert(subtree.type == 'NAME')
        return self.path(tree)

    def argument(self, tree):
        """
        Compiles an argument tree to the corresponding object.
        """
        name = tree.child(0).value
        value = self.expression(tree.child(1))
        return {'$OBJECT': 'argument', 'name': name, 'argument': value}

    def arguments(self, tree):
        """
        Parses a group of arguments rules
        """
        arguments = []
        for argument in tree.find_data('arguments'):
            arguments.append(self.argument(argument))
        return arguments

    def typed_argument(self, tree):
        name = tree.child(0).value
        value = self.values(Tree('anon', [tree.child(1)]))
        return {'$OBJECT': 'argument', 'name': name, 'argument': value}

    def function_arguments(self, tree):
        arguments = []
        for argument in tree.find_data('typed_argument'):
            arguments.append(self.typed_argument(argument))
        return arguments

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.child(0).data == 'or_expression'
        return self.expr_visitor.expression(tree)

    def absolute_expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.child(0).data == 'expression'
        return self.expression(tree.child(0))

    def base_expression(self, tree):
        """
        Compiles an soon to be expression object with the given tree.
        """
        child = tree.child(0)
        if child.data == 'expression':
            return self.expression(child)
        else:
            assert child.data == 'path'
            return self.path(child)
