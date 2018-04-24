# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree

from pytest import fixture, mark

from storyscript.parser import Parser


@fixture
def int_token():
    return Token('INT', 3)


@fixture
def var_token():
    return Token('WORD', 'var')


def test_parser_values(int_token):
    parser = Parser('3\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children[0]
    assert node == int_token


@mark.parametrize('string', ["'red'\n", '"red"\n'])
def test_parser_values_string(string):
    parser = Parser(string)
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[1] == Token('WORD', 'red')


def test_parser_list(int_token):
    parser = Parser('[3,4]\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0].children[0].children[0] == int_token
    assert node.children[1].children[0].children[0] == Token('INT', 4)


def test_parser_list_empty():
    parser = Parser('[]\n')
    result = parser.parse()
    print(result.pretty())
    node = result.children[0].children[0].children[0].children[0]
    assert node == Tree('list', [])


def test_parser_assignments(var_token):
    parser = Parser('var="hello"\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[0] == var_token
    assert node.children[1] == Token('EQUALS', '=')
    assert node.children[2].children[0].children[1] == Token('WORD', 'hello')


def test_parser_assignments_int(int_token, var_token):
    parser = Parser('var=3\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[0] == var_token
    assert node.children[1] == Token('EQUALS', '=')
    assert node.children[2].children[0].children[0] == int_token


def test_parser_if_statement(var_token):
    parser = Parser('if var\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('IF', 'if')
    assert node.children[2] == var_token


def test_parser_for_statement(var_token):
    parser = Parser('for var in items\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('FOR', 'for')
    assert node[2] == var_token
    assert node[4] == Token('IN', 'in')
    assert node[6] == Token('WORD', 'items')


def test_parser_foreach_statement():
    parser = Parser('foreach items as item\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('FOREACH', 'foreach')
    assert node[2] == Token('WORD', 'items')
    assert node[4] == Token('AS', 'as')
    assert node[6] == Token('WORD', 'item')


def test_parser_wait_statement():
    parser = Parser('wait time\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('WAIT', 'wait')
    assert node[2] == Token('WORD', 'time')


def test_parser_wait_statement_string():
    parser = Parser('wait "seconds"\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('WAIT', 'wait')
    assert node[2].children[1] == Token('WORD', 'seconds')


@mark.parametrize('comment', ['# one', '#one'])
def test_parser_comment(comment):
    parser = Parser('{}\n'.format(comment))
    result = parser.parse()
    print(result)
    node = result.children[0].children[0].children[0].children[0]
    assert node == Token('COMMENT', comment)


def test_parser_suite(var_token):
    parser = Parser('if expr\n\tvar=3\n')
    result = parser.parse()
    node = result.children[0].children
    assert node[0].children[0].children[0].children[0] == Token('IF', 'if')
    assert node[1].children[0].children[0].children[0] == var_token


def test_parser_suite_double(var_token):
    parser = Parser('if expr\n\tif things\n\tvar=3\n')
    result = parser.parse()
    node = result.children[0].children
    things_node = node[1].children[0].children[0].children[0].children[2]
    assert things_node == Token('WORD', 'things')
    assert node[2].children[0].children[0].children[0] == var_token
