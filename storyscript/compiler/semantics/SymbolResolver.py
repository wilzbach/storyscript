# -*- coding: utf-8 -*-
from storyscript.compiler.semantics.types.Indexing import IndexKind
from storyscript.compiler.semantics.types.Types import NoneType

from .symbols.Symbols import Symbol


class SymbolResolver:
    """
    Allows resolving symbols from a scope, but doesn't provide more scope
    operations.
    """

    def __init__(self, scope, check_variable_existence=True, module=None):
        self.scope = scope
        self._check_variable_existence = check_variable_existence
        self.module = module

    def update_scope(self, scope):
        """
        Update the current scope
        """
        self.scope = scope

    def resolve(self, tree, val, paths):
        assert isinstance(val, str)
        symbol = self.scope.resolve(val)

        if self._check_variable_existence:
            tree.expect(symbol is not None, 'var_not_defined', name=val)
        else:
            if symbol is None:
                tree.expect(len(paths) == 0, 'var_not_defined', name=val)
                return Symbol(val, NoneType.instance())

        for p in paths:
            symbol = self.index(tree, symbol, name=p.value, type_=p.type,
                                kind=p.kind)
        return symbol

    def index(self, tree, symbol, name, type_, kind):
        ret = symbol.index(name=name, type_=type_, kind=kind)
        if ret == IndexKind.DOT:
            msg = 'type_dot_incompatible'
        elif ret == IndexKind.INDEX:
            msg = 'type_index_incompatible'
        else:
            assert isinstance(ret, Symbol)
            return ret

        if isinstance(type_, Symbol):
            type_ = type_.type()
        else:
            # assert isinstance(type_, BaseType)
            pass

        if name.startswith('__'):
            name = self.module.print_tmp_assignment(name)

        tree.expect(0, msg,
                    left=symbol.type(),
                    name=name,
                    right=type_)
