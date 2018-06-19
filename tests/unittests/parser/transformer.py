# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from pytest import mark, raises

from storyscript.exceptions import StoryscriptSyntaxError
from storyscript.parser import Transformer, Tree


def test_transformer():
    assert issubclass(Transformer, LarkTransformer)


def test_transformer_arguments():
    assert Transformer().arguments('matches') == Tree('arguments', 'matches')


def test_transformer_service(magic):
    matches = [magic()]
    assert Transformer().service(matches) == Tree('service', matches)


def test_transformer_service_error(magic):
    matches = [magic(children=[magic(), magic()])]
    with raises(StoryscriptSyntaxError):
        Transformer().service(matches)


def test_transformer_assignment(magic):
    matches = [magic()]
    assert Transformer().assignment(matches) == Tree('assignment', matches)


def test_transformer_assignment_error_backslash(magic):
    matches = [magic(children=[magic(value='/')])]
    with raises(StoryscriptSyntaxError):
        Transformer().assignment(matches)


def test_transformer_assignment_error_dash(magic):
    matches = [magic(children=[magic(value='-')])]
    with raises(StoryscriptSyntaxError):
        Transformer().assignment(matches)


@mark.parametrize('rule', ['start', 'line', 'block', 'command', 'statement'])
def test_transformer_rules(rule):
    transformer = Transformer()
    result = getattr(transformer, rule)(['matches'])
    assert isinstance(result, Tree)
    assert result.data == rule
    assert result.children == ['matches']
