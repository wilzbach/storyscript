# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.compiler.lowering.utils import unicode_escape
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
                elif child.data == 'range':
                    value = self.range(child)
                elif child.data == 'number':
                    value = self.number(child)
                else:
                    assert child.data == 'path'
                    value = self.path(child)
            else:
                assert child.type == 'NAME'
                value = {'$OBJECT': 'dot', 'dot': value}
            names.append(value)
        return names

    def path(self, tree):
        paths = self.names(tree)
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
                'args': arguments}

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
    def time(tree):
        """
        Compiles a time tree
        """
        assert tree.data == 'time'
        val = tree.child(0).value
        assert len(val) > 0

        ms_value = 0
        prev_time = None
        time_parts = split_into_time_parts(val)
        for p, time_type in time_parts:
            tree.expect(prev_time != time_type, 'time_value_duplicate',
                        time_type=time_type)
            if time_type == 'w':
                tree.expect(prev_time is None, 'time_value_inconsistent_week')
                ms_value += 604800000 * p
            elif time_type == 'd':
                tree.expect(prev_time is None or prev_time in 'w',
                            'time_value_inconsistent',
                            prev=prev_time, current=time_type)
                ms_value += 86400000 * p
            elif time_type == 'h':
                tree.expect(prev_time is None or prev_time in 'wd',
                            'time_value_inconsistent',
                            prev=prev_time, current=time_type)
                ms_value += 3600000 * p
            elif time_type == 'm':
                tree.expect(prev_time is None or prev_time in 'wdh',
                            'time_value_inconsistent',
                            prev=prev_time, current=time_type)
                ms_value += 60000 * p
            elif time_type == 's':
                assert time_type == 's'
                tree.expect(prev_time is None or prev_time in 'wdhm',
                            'time_value_inconsistent',
                            prev=prev_time, current=time_type)
                ms_value += 1000 * p
            else:
                assert time_type == 'ms'
                tree.expect(prev_time is None or prev_time in 'wdhms',
                            'time_value_inconsistent',
                            prev=prev_time, current=time_type)
                ms_value += p
            prev_time = time_type
        return {'$OBJECT': 'time', 'ms': ms_value}

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

    def string(self, tree):
        """
        Compiles a string tree.
        """
        value = unicode_escape(tree, tree.child(0).value)
        return {'$OBJECT': 'string', 'string': value}

    @staticmethod
    def boolean(tree):
        if tree.child(0).value == 'true':
            return {'$OBJECT': 'boolean', 'boolean': True}
        return {'$OBJECT': 'boolean', 'boolean': False}

    def range_child(self, tree):
        """
        Compiles an individual range token.
        It can be either a number or a path.
        """
        if tree.data == 'number':
            return self.number(tree)
        assert tree.data == 'path'
        return self.path(tree)

    def range(self, tree):
        """
        Compiles a range tree.
        """
        val = self.range_child(tree.child(0).child(0))
        if tree.range_start:
            r = {'start': val}
        elif tree.range_end:
            r = {'end': val}
        else:
            assert tree.range_start_end
            end = self.range_child(tree.child(0).child(1))
            r = {'start': val, 'end': end}
        return {'$OBJECT': 'range', 'range': r}

    def list(self, tree):
        items = []
        for value in tree.children:
            if isinstance(value, Tree):
                items.append(self.base_expression(value))
        return {'$OBJECT': 'list', 'items': items}

    def map(self, tree):
        items = []
        for item in tree.children:
            child = item.child(0)
            if child.data == 'string':
                key = self.string(child)
            elif child.data == 'number':
                key = self.number(child)
            elif child.data == 'boolean':
                key = self.boolean(child)
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
        value = tree.child(0).value
        re_arr = value.split('/')[1:]
        dictionary = {'$OBJECT': 'regexp', 'regexp': re_arr[0]}
        if len(re_arr[1]) > 0:
            dictionary['flags'] = re_arr[1]
        return dictionary

    @classmethod
    def types(cls, tree):
        assert tree.data == 'types'
        c = tree.first_child()
        if c.data == 'map_type':
            key = cls.base_type(c.child(0))
            value = cls.types(c.child(1))
            return {'$OBJECT': 'type', 'type': 'Map', 'values': [key, value]}
        elif c.data == 'list_type':
            inner = cls.types(c.child(0))
            return {'$OBJECT': 'type', 'type': 'List', 'values': [inner]}
        else:
            return cls.base_type(c)

    @staticmethod
    def base_type(tree):
        assert tree.data == 'base_type'
        t = tree.child(0).value
        return {'$OBJECT': 'type', 'type': t}

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
            elif subtree.data == 'time':
                return self.time(subtree)
            elif subtree.data == 'map':
                return self.map(subtree)
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
        return {'$OBJECT': 'arg', 'name': name, 'arg': value}

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
        return {'$OBJECT': 'arg', 'name': name, 'arg': value}

    def function_arguments(self, tree):
        arguments = []
        for argument in tree.find_data('typed_argument'):
            arguments.append(self.typed_argument(argument))
        return arguments

    def expression(self, tree):
        """
        Compiles an expression object with the given tree.
        """
        assert tree.data == 'expression'
        return self.expr_visitor.expression(tree)

    def primary_expression(self, tree):
        """
        Compiles a primary expression object with the given tree.
        """
        assert tree.data == 'primary_expression'
        return self.expr_visitor.primary_expression(tree)

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


def split_into_time_parts(value):
    """
    Splits a time string into its subparts.
    Example: 1h5s = [(1, 'h'), (5, 's')]
    """
    num_buf = ''
    i = 0
    nr_values = len(value)
    while i < nr_values:
        c = value[i]
        if c.isdigit():
            num_buf += c
        else:
            # peek into the future for 'ms'
            if c == 'm' and i + 1 < nr_values and value[i + 1] == 's':
                i = i + 1
                yield int(num_buf), 'ms'
            else:
                assert c in 'smhdw'
                yield int(num_buf), c
            num_buf = ''
        i = i + 1

    assert len(num_buf) == 0
