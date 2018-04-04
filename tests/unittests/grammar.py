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


def test_grammar_start(grammar):
    assert grammar.start() == 'start:'


def test_grammar_terminal(grammar):
    grammar.terminal('name', 'value')
    assert grammar.terminals == ['name: value']


def test_grammar_rule(grammar):
    grammar.rule('name', ['one', 'two'])
    assert grammar.rules == ['name: one|two']


def test_grammar_build(patch, grammar):
    patch.object(Grammar, 'start')
    assert grammar.build() == grammar.start()
