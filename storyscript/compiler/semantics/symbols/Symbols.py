# -*- coding: utf-8 -*-


class Symbol:
    """
    Representation of an individual symbol.
    """
    def __init__(self, name, type_):
        self._name = name
        self._type = type_

    @staticmethod
    def resolve_path(tree):
        assert tree.data == 'path'
        name = tree.first_child().value
        return name

    def name(self):
        return self._name

    def type(self):
        return self._type

    def pretty(self):
        return f'{self._type}'


class Symbols:
    """
    Represents all symbols in a scope
    """

    def __init__(self):
        self._symbols = {}

    def resolve(self, name):
        assert len(name) > 0
        if name in self._symbols:
            return self._symbols[name]

    def insert(self, name, symbol):
        self._symbols[name] = symbol

    def pretty(self, indent=''):
        result = ''
        for k, v in self._symbols.items():
            result += f'{indent}{k}: {v.pretty()}\n'
        return result
