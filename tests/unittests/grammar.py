# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.grammar import Grammar


@fixture
def grammar():
    return Grammar()


def test_grammar_init():
    grammar = Grammar()
    assert grammar.terminals == []


def test_grammar_start(grammar):
    assert grammar.start() == 'start:'


def test_grammar_build(patch, grammar):
    patch.object(Grammar, 'start')
    assert grammar.build() == grammar.start()
