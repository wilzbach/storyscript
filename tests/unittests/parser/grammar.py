# -*- coding: utf-8 -*-
from pytest import fixture, mark

from storyscript.parser import Grammar


@fixture
def grammar():
    return Grammar()


def test_grammar_init():
    grammar = Grammar()
    assert grammar.start_line is None
    assert grammar._tokens == {}
    assert grammar._rules == {}
    assert grammar.imports == {}
    assert grammar.ignores == []


def test_grammar_resolve(grammar):
    assert grammar.resolve('item') == 'item'


def test_grammar_resolve_token(grammar):
    grammar._tokens = {'token': ('TOKEN', 'value')}
    assert grammar.resolve('token') == 'TOKEN'


def test_grammar_start(grammar):
    grammar.start('rule')
    assert grammar.start_line == 'start: rule+'


@mark.parametrize('token_name', ['NAME', 'name'])
def test_grammar_token(grammar, token_name):
    """
    Ensures the token method can create a token
    """
    grammar.token(token_name, 'value')
    assert grammar._tokens[token_name] == ('NAME', '"value"')


def test_grammar_token_priority(grammar):
    grammar.token('NAME', 'value', priority=1)
    assert grammar._tokens['NAME'] == ('NAME.1', '"value"')


def test_grammar_token_insensitive(grammar):
    grammar.token('NAME', 'value', insensitive=True)
    assert grammar._tokens['NAME'] == ('NAME', '"value"i')


def test_grammar_token_inline(grammar):
    grammar.token('NAME', 'value', inline=True)
    assert grammar._tokens['NAME'] == ('_NAME', '"value"')


def test_grammar_token_regexp(grammar):
    grammar.token('NAME', 'regexp', regexp=True)
    assert grammar._tokens['NAME'] == ('NAME', 'regexp')


def test_grammar_tokens(patch, grammar):
    patch.object(Grammar, 'token')
    grammar.tokens(('token', 'value'), kwargs='yes')
    Grammar.token.assert_called_with('token', 'value', kwargs='yes')


def test_grammar_rule(patch, grammar):
    patch.object(Grammar, 'resolve', return_value='resolved')
    grammar.rule('name', ('literal', 'token'))
    grammar.rule('name', ('literal2', ))
    assert grammar._rules['name'] == ['resolved resolved', 'resolved']


def test_grammar_rules(patch, grammar):
    patch.object(Grammar, 'rule')
    grammar.rules('name', ('literal', ), ('literal2', ))
    Grammar.rule.assert_called_with('name', ('literal2', ))
    assert Grammar.rule.call_count == 2


def test_grammar_ignore(grammar):
    grammar.ignore('terminal')
    assert grammar.ignores == ['%ignore terminal']


def test_grammar_load(grammar):
    grammar.load('token')
    assert grammar.imports['token'] == '%import common.TOKEN'


def test_grammar_loads(patch, grammar):
    patch.object(Grammar, 'load')
    grammar.loads(['one'])
    Grammar.load.assert_called_with('one')


def test_grammar_build_tokens(patch, grammar):
    grammar._tokens = {'token': ('TOKEN', 'value'), 't2': ('T2', 'value')}
    assert grammar.build_tokens() == 'TOKEN: value\nT2: value\n'


def test_grammar_build_rules(grammar):
    grammar._rules = {'rule': ['definition', 'more'], 'r2': ['definition']}
    assert grammar.build_rules() == 'rule: definition | more\nr2: definition\n'


def test_grammar_build(patch, grammar):
    patch.object(Grammar, 'build_tokens', return_value='tokens')
    patch.object(Grammar, 'build_rules', return_value='rules')
    grammar.start_line = 'start'
    grammar.ignores = ['ignores']
    grammar.imports = ['imports']
    result = grammar.build()
    assert Grammar.build_tokens.call_count == 1
    assert Grammar.build_rules.call_count == 1
    assert result == 'start\nrules\ntokens\nignores\n\nimports'
