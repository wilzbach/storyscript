# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.grammar import Grammar


@fixture
def grammar():
    return Grammar()


def test_grammar_init():
    grammar = Grammar()
    assert grammar.terminals == []
    assert grammar.rules == []
    assert grammar.ignores == []
    assert grammar.imports == []


def test_grammar_start(grammar):
    assert grammar.start() == 'start:'


def test_grammar_terminal(grammar):
    """
    Ensures the terminal method can create a terminal token
    """
    grammar.terminal('NAME', 'value')
    assert grammar.terminals == ['NAME: value']


def test_grammar_terminal_priority(grammar):
    grammar.terminal('NAME', 'value', priority=1)
    assert grammar.terminals == ['NAME.1: value']


def test_grammar_terminal_uppercase(grammar):
    grammar.terminal('name', 'value')
    assert grammar.terminals == ['NAME: value']


def test_grammar_rule(grammar):
    grammar.rule('name', ['one', 'two'])
    assert grammar.rules == ['name: one|two']


def test_grammar_ignore(grammar):
    grammar.ignore('terminal')
    assert grammar.ignores == ['%ignore terminal']


def test_grammar_load(grammar):
    grammar.load('terminal')
    assert grammar.imports == ['%import terminal']


def test_grammar_build(patch, grammar):
    patch.object(Grammar, 'start')
    assert grammar.build() == grammar.start()
