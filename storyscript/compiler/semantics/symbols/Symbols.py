# -*- coding: utf-8 -*-
from .SymbolTypes import SymbolType


class Symbol:
    """
    Representation of an individual symbol.
    """
    def __init__(self, name, type_):
        self._name = name
        self._type = type_

    def name(self):
        return self._name

    def type(self):
        return self._type

    def pretty(self):
        return f'{self._type}'

    def __str__(self):
        return f'Symbol(\'{self._name}\', {self._type})'

    def index(self, paths, tree):
        """
        Runs index operations on a resolved symbol.
        """
        symbol = self
        for p in paths:
            if isinstance(p, Symbol):
                p = p.type()
            else:
                assert isinstance(p, SymbolType)
            new_type = symbol.type().index(p)
            tree.expect(new_type is not None,
                        'type_index_incompatible',
                        left=symbol.type(),
                        right=p)
            symbol = Symbol(name=symbol.name() + '[]', type_=new_type)
        return symbol


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
