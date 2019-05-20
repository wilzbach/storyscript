# -*- coding: utf-8 -*-
from unittest.mock import call

from storyscript.compiler.semantics.ExpressionResolver \
    import SymbolExpressionVisitor
from storyscript.compiler.semantics.types.Types import BooleanType, \
    IntType, MapType
from storyscript.parser import Tree


def test_type_to_tree_boolean(magic):
    tree = magic()
    bt = BooleanType.instance()
    se = SymbolExpressionVisitor.type_to_tree(tree, bt)
    assert se.data == 'base_type'
    tree.create_token.assert_called_with('BOOLEAN_TYPE', 'boolean')


def test_type_to_tree_map(magic, patch):
    tree = magic()
    mt = MapType(IntType.instance(), BooleanType.instance())
    type_to_tree = SymbolExpressionVisitor.type_to_tree
    patch.object(SymbolExpressionVisitor, 'type_to_tree')
    se = type_to_tree(tree, mt)
    assert SymbolExpressionVisitor.type_to_tree.call_args_list == [
        call(tree, IntType.instance()),
        call(tree, BooleanType.instance())
    ]
    assert se == Tree('map_type', [
        SymbolExpressionVisitor.type_to_tree(),
        Tree('types', [
            SymbolExpressionVisitor.type_to_tree()
        ])
    ])
