# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from storyscript.parser import Transformer


def test_transformer():
    assert issubclass(Transformer, LarkTransformer)
