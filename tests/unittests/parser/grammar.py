# -*- coding: utf-8 -*-
from pytest import fixture, mark

from storyscript.parser import Grammar


@fixture
def grammar():
    return Grammar()


def test_grammar_init():
    grammar = Grammar()
    assert grammar.start_line is None
    assert grammar.tokens_list == []
    assert grammar.rules == []
    assert grammar.ignores == []
    assert grammar.imports == []


def test_grammar_start(grammar):
    grammar.start('rule')
    assert grammar.start_line == 'start: rule+'


@mark.parametrize('token_name', ['NAME', 'name'])
def test_grammar_token(grammar, token_name):
    """
    Ensures the token method can create a token
    """
    grammar.token(token_name, 'value')
    assert grammar.tokens_list == ['NAME: "value"']


def test_grammar_token_priority(grammar):
    grammar.token('NAME', 'value', priority=1)
    assert grammar.tokens_list == ['NAME.1: "value"']


def test_grammar_token_insensitive(grammar):
    grammar.token('NAME', 'value', insensitive=True)
    assert grammar.tokens_list == ['NAME: "value"i']


def test_grammar_token_inline(grammar):
    grammar.token('NAME', 'value', inline=True)
    assert grammar.tokens_list == ['_NAME: "value"']


def test_grammar_tokens(patch, grammar):
    patch.object(Grammar, 'token')
    grammar.tokens(('token', 'value'), kwargs='yes')
    Grammar.token.assert_called_with('token', 'value', kwargs='yes')


def test_grammar_rule(grammar):
    grammar.rule('name', ['one', 'two'])
    assert grammar.rules == ['name: one|two']


def test_grammar_ignore(grammar):
    grammar.ignore('terminal')
    assert grammar.ignores == ['%ignore terminal']


def test_grammar_load(grammar):
    grammar.load('token')
    assert grammar.imports == ['%import common.token']


def test_grammar_loads(patch, grammar):
    patch.object(Grammar, 'load')
    grammar.loads(['one'])
    Grammar.load.assert_called_with('one')


def test_grammar_build(grammar):
    grammar.start_line = 'start'
    grammar.rules = ['rules']
    grammar.tokens_list = ['tokens']
    grammar.ignores = ['ignores']
    grammar.imports = ['imports']
    result = grammar.build()
    assert result == 'start\nrules\n\ntokens\n\nignores\n\nimports'
