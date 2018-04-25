# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.parser import Grammar


@fixture
def grammar():
    return Grammar()


def test_grammar_init():
    grammar = Grammar()
    assert grammar.start_line is None
    assert grammar.tokens == []
    assert grammar.rules == []
    assert grammar.ignores == []
    assert grammar.imports == []


def test_grammar_start(grammar):
    grammar.start('rule')
    assert grammar.start_line == 'start: rule+'


def test_grammar_token(grammar):
    """
    Ensures the token method can create a token
    """
    grammar.token('NAME', '"value"')
    assert grammar.tokens == ['NAME: "value"']


def test_grammar_token_priority(grammar):
    grammar.token('NAME', '"value"', priority=1)
    assert grammar.tokens == ['NAME.1: "value"']


def test_grammar_token_insensitive(grammar):
    grammar.token('NAME', '"value"', insensitive=True)
    assert grammar.tokens == ['NAME: "value"i']


def test_grammar_token_inline(grammar):
    grammar.token('NAME', '"value"', inline=True)
    assert grammar.tokens == ['_NAME: "value"']


def test_grammar_token_uppercase(grammar):
    grammar.token('name', '"value"')
    assert grammar.tokens == ['NAME: "value"']


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
    grammar.tokens = ['tokens']
    grammar.ignores = ['ignores']
    grammar.imports = ['imports']
    result = grammar.build()
    assert result == 'start\nrules\n\ntokens\n\nignores\n\nimports'
