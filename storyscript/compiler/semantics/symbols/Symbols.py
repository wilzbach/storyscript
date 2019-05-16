# -*- coding: utf-8 -*-
from storyscript.compiler.semantics.types.Types import BaseType


class StorageClass:
    write = 0
    read = 1


def base_symbol(type_):
    """
    Creates a temporary symbol for a base type
    """
    return Symbol('tmp', type_)


class Symbol:
    """
    Representation of an individual symbol.
    """
    def __init__(self, name, type_, storage_class=StorageClass.write):
        self._name = name
        self._type = type_
        self._storage_class = storage_class

    def name(self):
        return self._name

    def type(self):
        return self._type

    def pretty(self):
        return f'{self._type}'

    def __str__(self):
        base = f"'{self._name}', {self._type}"
        if not self.can_write():
            base += ', ro'
        return f'Symbol({base})'

    @classmethod
    def from_path(cls, node, type_, storage_class=StorageClass.write):
        assert node.type == 'NAME'
        name = node.value
        return cls(name, type_, storage_class=storage_class)

    def is_internal(self):
        return self._name.startswith('__p-')

    def index(self, paths, tree):
        """
        Runs index operations on a resolved symbol.
        """
        symbol = self
        for p in paths:
            if isinstance(p, Symbol):
                p = p.type()
            else:
                assert isinstance(p, BaseType)
            new_type = symbol.type().index(p)
            tree.expect(new_type is not None,
                        'type_index_incompatible',
                        left=symbol.type(),
                        right=p)
            symbol = Symbol(name=symbol.name() + '[]', type_=new_type,
                            storage_class=self._storage_class)
        return symbol

    def can_write(self):
        return self._storage_class == StorageClass.write


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

    def insert(self, symbol):
        self._symbols[symbol.name()] = symbol

    def pretty(self, indent=''):
        result = ''
        for k, v in self._symbols.items():
            result += f'{indent}{k}: {v.pretty()}\n'
        return result
