# -*- coding: utf-8 -*-
from lark.lexer import Token

from .symbols.SymbolTypes import NoneType
from .symbols.Symbols import Symbol


class SymbolResolver:
    """
    Allows resolving symbols from a scope, but doesn't provide more scope
    operations.
    """

    def __init__(self, scope, check_variable_existence=True):
        self.scope = scope
        self._check_variable_existence = check_variable_existence

    def update_scope(self, scope):
        """
        Update the current scope
        """
        self.scope = scope

    def resolve(self, tree, paths):
        val = paths[0]
        if isinstance(val, Token):
            val = val.value
        assert isinstance(val, str)
        symbol = self.scope.resolve(val)

        if self._check_variable_existence:
            tree.expect(symbol is not None, 'var_not_defined', name=paths[0])
        else:
            if symbol is None:
                tree.expect(len(paths) == 1, 'var_not_defined', name=paths[0])
                return Symbol(val, NoneType.instance())

        return symbol.index(paths[1:], tree)
