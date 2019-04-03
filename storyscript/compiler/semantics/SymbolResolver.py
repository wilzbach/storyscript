# -*- coding: utf-8 -*-
from lark.lexer import Token

from .symbols.SymbolTypes import IntType, StringType, SymbolType
from .symbols.Symbols import Symbol


class SymbolResolver:
    """
    Allows resolving symbols from a scope, but doesn't provide more scope
    operations.
    """

    def __init__(self, scope):
        self.scope = scope

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
        tree.expect(symbol is not None, 'var_not_defined', name=paths[0])
        for p in paths[1:]:
            if isinstance(p, str):
                if p.isdigit():
                    p = IntType.instance()
                else:
                    p = StringType.instance()
            else:
                assert isinstance(p, SymbolType)
            new_type = symbol.type().index(p)
            tree.expect(new_type is not None,
                        'type_index_incompatible',
                        left=symbol.type(),
                        right=p)
            symbol = Symbol(name=symbol.name() + '[]', type_=new_type)
        return symbol.type()
