# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from storyscript.compiler import Preprocessor
from storyscript.parser import Tree


def test_preprocessor_magic_line(patch, magic, tree):
    patch.object(uuid, 'uuid4', return_value=magic(int=123456789))
    result = Preprocessor.magic_line(tree)
    assert result == '0.12345678'


def test_preprocessor_magic_path(patch):
    patch.object(uuid, 'uuid4')
    result = Preprocessor.magic_path(1)
    name = '${}'.format(uuid.uuid4().hex[:8])
    assert result == Tree('path', [Token('NAME', name, line=1)])


def test_preprocessor_inline_expressions(tree):
    assert Preprocessor.inline_expression(tree) == tree


def test_preprocessor_process(patch):
    patch.object(Preprocessor, 'inline_expression')
    result = Preprocessor.process('tree')
    Preprocessor.inline_expression.assert_called_with('tree')
    assert result == Preprocessor.inline_expression()
