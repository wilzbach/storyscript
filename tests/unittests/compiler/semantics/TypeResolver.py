# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.compiler.semantics.TypeResolver import ScopeSelectiveVisitor
from storyscript.parser import Tree


class ScopeSelectiveTestVisitor(ScopeSelectiveVisitor):

    def __init__(self):
        self._a = 0
        self._b = 0

    def a(self, tree, scope):
        self._a = self._a + 1
        self.visit_children(tree, scope)

    def b(self, tree, scope):
        self._b = self._b + 1
        self.visit_children(tree, scope)


def test_scope_selective_visitor_empty():
    tv = ScopeSelectiveTestVisitor()
    tv.visit_children(Tree('a', []), scope=None)
    assert tv._a == 0
    assert tv._b == 0


def test_scope_selective_visitor_single():
    tv = ScopeSelectiveTestVisitor()
    tv.visit_children(Tree('c', [
        Tree('a', [])
    ]), scope=None)
    assert tv._a == 1
    assert tv._b == 0


def test_scope_selective_visitor_multiple():
    tv = ScopeSelectiveTestVisitor()
    tv.visit_children(Tree('c', [
        Tree('a', []),
        Tree('b', []),
        Tree('a', []),
    ]), scope=None)
    assert tv._a == 2
    assert tv._b == 1


def test_scope_selective_visitor_nested():
    tv = ScopeSelectiveTestVisitor()
    tv.visit_children(Tree('c', [
        Tree('a', [
            Tree('a', [])
        ]),
        Tree('b', []),
        Tree('a', []),
    ]), scope=None)
    assert tv._a == 3
    assert tv._b == 1


def test_scope_selective_visitor_token():
    tv = ScopeSelectiveTestVisitor()
    tv.visit_children(Tree('c', [
        Tree('a', [
            Tree('a', [Token('A', 0)])
        ]),
        Token('b', 0),
        Tree('b', []),
        Tree('a', []),
    ]), scope=None)
    assert tv._a == 3
    assert tv._b == 1
