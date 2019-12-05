# -*- coding: utf-8 -*-
from storyscript.compiler.semantics.symbols.Scope import Scope
from storyscript.compiler.semantics.symbols.Symbols import Symbols


def test_scope_pretty_none(patch):
    scope = Scope()
    patch.object(Symbols, "pretty", return_value=".symbols.")
    assert (
        scope.pretty()
        == """Parent: None
Symbols:
.symbols."""
    )
    Symbols.pretty.assert_called_with(indent="\t")


def test_scope_pretty(patch, magic):
    root_scope = ".parent."
    scope = Scope(parent=root_scope)
    patch.object(Symbols, "pretty", return_value=".symbols.")
    assert (
        scope.pretty()
        == """Parent: .parent.
Symbols:
.symbols."""
    )
    Symbols.pretty.assert_called_with(indent="\t")


def test_scope_str(patch):
    scope = Scope()
    assert str(scope) == "Scope()"


def test_scope_str_root(patch):
    scope = Scope.root()
    assert str(scope) == "Scope(app)"


def test_scope_str_with_symbols(patch, magic):
    scope = Scope()
    s1 = magic()
    s1.name.return_value = "s1"
    s2 = magic()
    s2.name.return_value = "s2"
    patch.object(Scope, "symbols", return_value=[s1, s2])
    assert str(scope) == "Scope(s1,s2)"


def test_scope_resolve_fail(patch, magic):
    patch.object(Symbols, "resolve", return_value=False)
    patch.object(Scope, "scopes", return_value=[Scope(), Scope()])
    scope = Scope()
    assert scope.resolve(".p.") is None
    Symbols.resolve.call_count == 2


def test_scope_resolve_sucess(patch, magic):
    patch.object(Symbols, "resolve", return_value=True)
    patch.object(Scope, "scopes", return_value=[Scope(), Scope()])
    scope = Scope()
    assert scope.resolve(".p.") == Symbols.resolve()
    Symbols.resolve.call_count == 1


def test_scope_scopes_single():
    s = Scope()
    r = list(s.scopes())
    assert len(r) == 1
    assert r[0] is s


def test_scope_scopes_multiple():
    s1 = Scope()
    s2 = Scope(parent=s1)
    s3 = Scope(parent=s2)
    r = list(s3.scopes())
    assert len(r) == 3
    assert r[0] is s3
    assert r[1] is s2
    assert r[2] is s1
