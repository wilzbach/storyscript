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


def test_parser_list():
    parser = Parser('[3,4]')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[1].children[0] == Token('INT', 3)
    assert node.children[3].children[0] == Token('INT', 4)


def test_parser_list_empty():
    parser = Parser('[]')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[0] == Token('OSB', '[')
    assert node.children[1] == Token('CSB', ']')


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


def test_parser_for_statement():
    parser = Parser('for var in items')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children
    assert node[0] == Token('FOR', 'for')
    assert node[2] == Token('WORD', 'var')
    assert node[4] == Token('IN', 'in')
    assert node[6] == Token('WORD', 'items')


def test_parser_foreach_statement():
    parser = Parser('foreach items as item')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children
    assert node[0] == Token('FOREACH', 'foreach')
    assert node[2] == Token('WORD', 'items')
    assert node[4] == Token('AS', 'as')
    assert node[6] == Token('WORD', 'item')
