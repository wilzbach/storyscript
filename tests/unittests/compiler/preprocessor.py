# -*- coding: utf-8 -*-
from storyscript.compiler import Preprocessor


def test_preprocessor_inline_expressions(tree):
    assert Preprocessor.inline_expression(tree) == tree


def test_preprocessor_process(patch):
    patch.object(Preprocessor, 'inline_expression')
    result = Preprocessor.process('tree')
    Preprocessor.inline_expression.assert_called_with('tree')
    assert result == Preprocessor.inline_expression()
