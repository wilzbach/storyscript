# -*- coding: utf-8 -*-
from pytest import fixture, mark

from storyscript.parser import Ebnf


@fixture
def ebnf():
    return Ebnf()


def test_ebnf_init():
    ebnf = Ebnf()
    assert ebnf._tokens == {}
    assert ebnf._rules == {}
    assert ebnf.imports == {}
    assert ebnf.ignores == []


def test_ebnf_macro(ebnf):
    ebnf.macro('name', 'hello {}')
    assert ebnf.name('world') == 'hello world'


def test_ebnf_set_token(ebnf):
    ebnf.set_token('token', 'value')
    assert ebnf._tokens['token'] == 'value'


def test_ebnf_resolve(ebnf):
    assert ebnf.resolve('item') == 'item'


def test_ebnf_resolve_token(ebnf):
    ebnf._tokens = {'token': ('TOKEN', 'value')}
    assert ebnf.resolve('token') == 'TOKEN'


def test_ebnf_resolve_token_inline(ebnf):
    ebnf._tokens = {'token': ('_TOKEN', 'value')}
    assert ebnf.resolve('token') == '_TOKEN'


def test_ebnf_resolve_token_priority(ebnf):
    ebnf._tokens = {'token': ('TOKEN.1', 'value')}
    assert ebnf.resolve('token') == 'TOKEN'


def test_ebnf_resolve_token_maybe(ebnf):
    ebnf._tokens = {'token': ('TOKEN', 'value')}
    assert ebnf.resolve('token?') == 'TOKEN?'


def test_ebnf_resolve_imports(ebnf):
    ebnf.imports = {'token': '%import common.TOKEN'}
    assert ebnf.resolve('token') == 'TOKEN'


@mark.parametrize('token_name', ['NAME', 'name'])
def test_ebnf_token(ebnf, token_name):
    """
    Ensures the token method can create a token
    """
    ebnf.token(token_name, 'value')
    assert ebnf._tokens[token_name] == ('NAME', '"value"')


def test_ebnf_token_priority(ebnf):
    ebnf.token('NAME', 'value', priority=1)
    assert ebnf._tokens['NAME'] == ('NAME.1', '"value"')


def test_ebnf_token_insensitive(ebnf):
    ebnf.token('NAME', 'value', insensitive=True)
    assert ebnf._tokens['NAME'] == ('NAME', '"value"i')


def test_ebnf_token_inline(ebnf):
    ebnf.token('NAME', 'value', inline=True)
    assert ebnf._tokens['NAME'] == ('_NAME', '"value"')


def test_ebnf_token_regexp(ebnf):
    ebnf.token('NAME', 'regexp', regexp=True)
    assert ebnf._tokens['NAME'] == ('NAME', 'regexp')


def test_ebnf_rule(patch, ebnf):
    patch.object(Ebnf, 'resolve', return_value='resolved')
    ebnf.rule('name', ('literal', 'token'))
    ebnf.rule('name', ('literal2', ))
    assert ebnf._rules['name'] == ['resolved resolved', 'resolved']


def test_ebnf_rule_raw(patch, ebnf):
    ebnf.rule('name', 'raw definition', raw=True)
    assert ebnf._rules['name'] == ['raw definition']


def test_ebnf_ignore(ebnf):
    ebnf.ignore('terminal')
    assert ebnf.ignores == ['%ignore terminal']


def test_ebnf_load(ebnf):
    ebnf.load('token')
    assert ebnf.imports['token'] == '%import common.TOKEN'


def test_ebnf_build_tokens(patch, ebnf):
    ebnf._tokens = {'token': ('TOKEN', 'value'), 't2': ('T2', 'value')}
    assert ebnf.build_tokens() == 'TOKEN: value\nT2: value\n'


def test_ebnf_build_rules(ebnf):
    ebnf._rules = {'rule': ['definition', 'more'], 'r2': ['definition']}
    assert ebnf.build_rules() == 'rule: definition\n\t| more\nr2: definition\n'


def test_ebnf_build(patch, ebnf):
    patch.object(Ebnf, 'build_tokens', return_value='tokens')
    patch.object(Ebnf, 'build_rules', return_value='rules')
    ebnf.start_line = 'start'
    ebnf.ignores = ['ignores']
    ebnf.imports = {'key': 'imports'}
    result = ebnf.build()
    assert Ebnf.build_tokens.call_count == 1
    assert Ebnf.build_rules.call_count == 1
    assert result == 'start\nrules\ntokens\nignores\n\nimports'
