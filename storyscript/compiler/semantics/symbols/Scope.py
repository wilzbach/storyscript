# -*- coding: utf-8 -*-

from storyscript.compiler.semantics.types.Types import ObjectType

from .Symbols import StorageClass, Symbol, Symbols


class Scope:
    """
    Manages an individual scope
    """

    def __init__(self, parent=None):
        self._parent = parent
        self._symbols = Symbols()

    def insert(self, sym):
        self._symbols.insert(sym)

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
        app = Symbol(name='app', type_=ObjectType.instance(),
                     storage_class=StorageClass.read())
        scope.insert(app)
        return scope


class ScopeJoiner:
    """
    Manages a joint scope of one or more scopes.
    The joint scope is the intersection of these scopes.
    """

    def __init__(self):
        self.scope = None
        self.invalid_symbols = {}

    def add(self, scope):
        """
        Performs the join operation on one or more scopes.
        """
        if self.scope is None:
            self.scope = scope
            self.symbols = scope._symbols._symbols
        else:
            # join symbols
            new_symbols = scope._symbols._symbols
            for k in [*self.symbols.keys()]:
                if k not in new_symbols:
                    del self.symbols[k]
                    self.invalid_symbols.pop(k, None)
                else:
                    # check for type compatibility
                    t1 = self.symbols[k]
                    t2 = new_symbols[k]
                    if t1.type() != t2.type():
                        # it is possible that a symbol doesn't appear in
                        # all scopes, so we must save it for later and check
                        # for such invalid symbols at the end
                        self.invalid_symbols[k] = {
                            't1name': t1.name(),
                            't1type': t1.type(),
                            't2name': t2.name(),
                            't2type': t2.type(),
                        }

    def insert_to(self, tree, scope):
        """
        Inserts the joined set of symbols into a scope.
        Enforces that such inserted symbols have the same type.
        """
        # It is possible that the symbol doesn't appear in all scopes and
        # wouldn't be hoisted. However, all scopes have been added now and
        # we can check if any symbols had type mismatches.
        for v in self.invalid_symbols.values():
            tree.expect(False, 'scope_join_incompatible', **v)

        for s in self.symbols.values():
            scope.insert(s)
