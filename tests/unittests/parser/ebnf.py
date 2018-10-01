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
    assert ebnf._imports == {}
    assert ebnf._ignores == []


def test_ebnf_macro(ebnf):
    ebnf.macro('name', '{} {}!')
    assert ebnf.name('hello', 'world') == 'hello world!'


def test_ebnf_set_token(ebnf):
    ebnf.set_token('TOKEN', 'value')
    expected = {'name': 'TOKEN', 'value': '"value"', 'token': 'TOKEN'}
    assert ebnf._tokens['token'] == expected


def test_ebnf_set_token_inline(ebnf):
    ebnf.set_token('_TOKEN', 'value')
    assert ebnf._tokens['token']['name'] == '_TOKEN'


def test_ebnf_set_token_priority(ebnf):
    ebnf.set_token('TOKEN.1', 'value')
    assert ebnf._tokens['token']['name'] == 'TOKEN.1'
    assert ebnf._tokens['token']['token'] == 'TOKEN'


def test_ebnf_set_token_expression(ebnf):
    ebnf.set_token('TOKEN', '/regexp/')
    assert ebnf._tokens['token']['value'] == '/regexp/'


def test_ebnf_set_token_expression_false_positive(ebnf):
    ebnf.set_token('TOKEN', '/')
    assert ebnf._tokens['token']['value'] == '"/"'


def test_ebnf_set_token_already_quoted(ebnf):
    ebnf.set_token('TOKEN', '"quoted"')
    assert ebnf._tokens['token']['value'] == '"quoted"'


def test_ebnf_resolve(ebnf):
    result = ebnf.resolve('(something)*')
    assert result == '(something)*'


def test_ebnf_resolve_token(ebnf):
    ebnf._tokens['token'] = {'token': '_TOKEN'}
    result = ebnf.resolve('(token)?')
    assert result == '(_TOKEN)?'


def test_ebnf_resolve_comma(patch, ebnf):
    ebnf._tokens['token'] = {'token': 'TOKEN'}
    assert ebnf.resolve('token,') == 'TOKEN|'


def test_ebnf_set_rule(patch, ebnf):
    """
    Ensures that rules are registered correctly
    """
    patch.object(Ebnf, 'resolve', return_value='name')
    ebnf.set_rule('rule', 'value')
    Ebnf.resolve.assert_called_with('value')
    assert ebnf._rules['rule'] == 'name'


def test_ebnf_ignore(ebnf):
    ebnf.ignore('terminal')
    assert ebnf._ignores == ['%ignore terminal']


def test_ebnf_load(ebnf):
    ebnf.load('token')
    assert ebnf._imports['token'] == '%import common.TOKEN'


def test_ebnf_build_tokens(ebnf):
    """
    Ensures tokens are built correctly.
    """
    ebnf._tokens['token'] = {'name': 'TOKEN', 'value': '"hello"'}
    assert ebnf.build_tokens() == 'TOKEN: "hello"\n'


def test_ebnf_build_rules(ebnf):
    """
    Ensures rules are built correctly.
    """
    ebnf._rules['rule'] = 'value'
    assert ebnf.build_rules() == 'rule: value\n'


def test_ebnf_build(patch, ebnf):
    """
    Ensures the grammar is built correctly.
    """
    patch.object(Ebnf, 'build_tokens', return_value='tokens')
    patch.object(Ebnf, 'build_rules', return_value='rules')
    ebnf._ignores = ['ignores']
    ebnf._imports = {'token': 'imports'}
    result = ebnf.build()
    assert Ebnf.build_tokens.call_count == 1
    assert Ebnf.build_rules.call_count == 1
    assert result == 'rules\ntokens\nignores\n\nimports'


def test_ebnf_setattr(ebnf):
    ebnf.value = 1
    assert ebnf.value == 1


def test_ebnf_setattr_token(patch, ebnf):
    patch.object(Ebnf, 'set_token')
    ebnf.TOKEN = 'value'
    Ebnf.set_token.assert_called_with('TOKEN', 'value')


def test_ebnf_setattr_rule(patch, ebnf):
    patch.object(Ebnf, 'set_rule')
    ebnf.rule = 'value'
    Ebnf.set_rule.assert_called_with('rule', 'value')
