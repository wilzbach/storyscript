# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.parser import Parser


def test_parser_values():
    parser = Parser('3')
    result = parser.parse()
    assert result.children[0].children[0].children[0] == Token('INT', 3)


def test_parser_values_string():
    parser = Parser("'red'")
    result = parser.parse()
    assert result.children[0].children[0].children[1] == Token('WORD', 'red')
