# -*- coding: utf-8 -*-
from storyscript.compiler.semantics.symbols.Symbols import StorageClass, \
    Symbol, Symbols
from storyscript.compiler.semantics.types.Types import IntType, \
    StringType


def test_symbol_pretty_int():
    sym = Symbol('foo', IntType.instance())
    assert sym.pretty() == 'int'


def test_symbol_str_string():
    sym = Symbol('foo', StringType.instance())
    assert str(sym) == "Symbol('foo', string, wa)"


def test_symbol_str_int():
    sym = Symbol('bar', IntType.instance())
    assert str(sym) == "Symbol('bar', int, wa)"


def test_symbol_pretty_string():
    sym = Symbol('foo', StringType.instance())
    assert sym.pretty() == 'string'


def test_symbol_str_ro_string():
    sym = Symbol('foo', StringType.instance(),
                 storage_class=StorageClass.read())
    assert str(sym) == "Symbol('foo', string, r-)"


def test_symbols_pretty():
    int_sym = Symbol('foo', IntType.instance())
    string_sym = Symbol('bar', StringType.instance())
    symbols = Symbols()
    symbols.insert(int_sym)
    symbols.insert(string_sym)
    assert symbols.pretty() == 'foo: int\nbar: string\n'
    assert symbols.pretty(indent='  ') == '  foo: int\n  bar: string\n'


def test_storage_class_readonly():
    assert str(StorageClass.read()) == 'r-'


def test_storage_class_write():
    assert str(StorageClass.write()) == 'wa'


def test_storage_class_rebindable():
    assert str(StorageClass.rebindable()) == 'ra'
