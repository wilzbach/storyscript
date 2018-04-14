# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.grammar import Grammar


@fixture
def grammar():
    return Grammar()


def test_grammar_init():
    grammar = Grammar()
    assert grammar.start_line is None
    assert grammar.terminals == []
    assert grammar.rules == []
    assert grammar.ignores == []
    assert grammar.imports == []


def test_grammar_start(grammar):
    grammar.start('rule')
    assert grammar.start_line == 'start: rule+'


def test_grammar_terminal(grammar):
    """
    Ensures the terminal method can create a terminal token
    """
    grammar.terminal('NAME', '"value"')
    assert grammar.terminals == ['NAME: "value"']


def test_grammar_terminal_priority(grammar):
    grammar.terminal('NAME', '"value"', priority=1)
    assert grammar.terminals == ['NAME.1: "value"']


def test_grammar_terminal_insensitive(grammar):
    grammar.terminal('NAME', '"value"', insensitive=True)
    assert grammar.terminals == ['NAME: "value"i']


def test_grammar_terminal_uppercase(grammar):
    grammar.terminal('name', '"value"')
    assert grammar.terminals == ['NAME: "value"']


def test_grammar_rule(grammar):
    grammar.rule('name', ['one', 'two'])
    assert grammar.rules == ['name: one|two']


def test_grammar_ignore(grammar):
    grammar.ignore('terminal')
    assert grammar.ignores == ['%ignore terminal']


def test_grammar_load(grammar):
    grammar.load('terminal')
    assert grammar.imports == ['%import common.terminal']


def test_grammar_loads(patch, grammar):
    patch.object(Grammar, 'load')
    grammar.loads(['one', 'two'])
    assert Grammar.load.call_count == 2


def test_grammar_build(grammar):
    grammar.start_line = 'start'
    grammar.rules = ['rules']
    grammar.terminals = ['terminals']
    grammar.ignores = ['ignores']
    grammar.imports = ['imports']
    result = grammar.build()
    assert result == 'start\nrules\nterminals\nignores\nimports'
