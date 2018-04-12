# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import mark

from storyscript.parser import Parser


def test_parser_values():
    parser = Parser('3')
    result = parser.parse()
    assert result.children[0].children[0].children[0] == Token('INT', 3)


@mark.parametrize('string', ["'red'", '"red"'])
def test_parser_values_string(string):
    parser = Parser(string)
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[1] == Token('WORD', 'red')


def test_parser_assignments():
    parser = Parser('var="hello"')
    result = parser.parse()
    node = result.children[0].children[0]
    assert node.children[0] == Token('WORD', 'var')
    assert node.children[1] == Token('EQUALS', '=')
    assert node.children[2].children[0].children[1] == Token('WORD', 'hello')


def test_parser_assignments_int():
    parser = Parser('var=3')
    result = parser.parse()
    node = result.children[0].children[0]
    assert node.children[0] == Token('WORD', 'var')
    assert node.children[1] == Token('EQUALS', '=')
    assert node.children[2].children[0] == Token('INT', '3')


def test_parser_if_statement():
    parser = Parser('if var')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[0] == Token('IF', 'if')
    assert node.children[2] == Token('WORD', 'var')
