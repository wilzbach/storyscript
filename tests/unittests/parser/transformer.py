# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from pytest import fixture

from storyscript.parser import Transformer


@fixture
def transformer():
    return Transformer()


def test_transformer():
    assert issubclass(Transformer, LarkTransformer)


def test_transformer_string(transformer):
    matches = ['one', 'two']
    assert transformer.string(matches) == matches
