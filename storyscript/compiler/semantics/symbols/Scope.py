# -*- coding: utf-8 -*-

from .SymbolTypes import AnyType
from .Symbols import Symbol, Symbols


class Scope:
    """
    Manages an individual scope
    """

    def __init__(self, parent=None):
        self._parent = parent
        self._symbols = Symbols()

    def insert(self, name, sym):
        self._symbols.insert(name, sym)

    def resolve(self, path):
        for scope in self.scopes():
            p = scope._symbols.resolve(path)
            if p:
                return p

    def symbols(self):
        """
        Returns all symbols available in the current scope
        """
        return self._symbols

    def parent(self):
        """
        Returns the parent scope
        """
        return self._parent

    def scopes(self):
        """
        Iterator over this and all its parent scopes
        """
        yield self
        if self._parent is not None:
            yield from self._parent.scopes()

    def pretty(self):
        indent = '\t'
        return (f'Parent: {self.parent()}\n'
                f'Symbols:\n{self.symbols().pretty(indent=indent)}')

    @classmethod
    def root(cls):
        """
        Creates a root scope.
        """
        scope = cls(parent=None)
        # insert global symbols
        app = Symbol(name='app', type_=AnyType.instance())
        scope.insert('app', app)
        return scope
