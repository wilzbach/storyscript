# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from pytest import fixture

from storyscript.parser import Transformer, Tree


@fixture
def transformer():
    return Transformer()


def test_transformer():
    assert issubclass(Transformer, LarkTransformer)


def test_transformer_start(patch, transformer):
    patch.init(Tree)
    result = transformer.start(['matches'])
    Tree.__init__.assert_called_with('line', ['matches'])
    assert isinstance(result, Tree)


def test_transformer_string(transformer):
    matches = ['one', 'two']
    assert transformer.string(matches) == matches
