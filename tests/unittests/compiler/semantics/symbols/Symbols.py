# -*- coding: utf-8 -*-
from storyscript.compiler.semantics.symbols.SymbolTypes import IntType, \
    StringType
from storyscript.compiler.semantics.symbols.Symbols import Symbol, Symbols


def test_symbol_pretty_int():
    sym = Symbol('foo', IntType.instance())
    assert sym.pretty() == 'int'


def test_symbol_pretty_string():
    sym = Symbol('foo', StringType.instance())
    assert sym.pretty() == 'string'


def test_symbols_pretty():
    int_sym = Symbol('foo', IntType.instance())
    string_sym = Symbol('bar', StringType.instance())
    symbols = Symbols()
    symbols.insert('foo', int_sym)
    symbols.insert('bar', string_sym)
    assert symbols.pretty() == 'foo: int\nbar: string\n'
    assert symbols.pretty(indent='  ') == '  foo: int\n  bar: string\n'
