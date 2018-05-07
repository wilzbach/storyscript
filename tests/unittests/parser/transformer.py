# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from pytest import mark

from storyscript.parser import Transformer, Tree


def test_transformer():
    assert issubclass(Transformer, LarkTransformer)


@mark.parametrize('rule', ['start', 'line', 'block', 'command', 'statements'])
def test_transformer_rules(rule):
    transformer = Transformer()
    result = getattr(transformer, rule)(['matches'])
    assert isinstance(result, Tree)
    assert result.data == rule
    assert result.children == ['matches']
