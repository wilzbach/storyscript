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


def test_parser_values_single_quoted_string():
    parser = Parser("'red'\n")
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('SINGLE_QUOTED', "'red'")


def test_parser_values_double_quoted_string():
    parser = Parser('"red"\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('DOUBLE_QUOTED', '"red"')


def test_parser_boolean_true():
    parser = Parser('true\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('TRUE', 'true')


def test_parser_filepath():
    parser = Parser('`/path`\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node == Token('FILEPATH', '`/path`')


def test_parser_list(int_token):
    parser = Parser('[3,4]\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0].children[0].children[0] == int_token
    assert node.children[1].children[0].children[0] == Token('INT', 4)


def test_parser_list_empty():
    parser = Parser('[]\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node == Tree('list', [])


def test_parser_assignments(var_token):
    parser = Parser('var="hello"\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[0] == var_token
    assert node.children[1] == Token('EQUALS', '=')
    token = Token('DOUBLE_QUOTED', '"hello"')
    assert node.children[2].children[0].children[0] ==  token


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
    assert node.children[1] == var_token


def test_parser_if_statement_comparison(var_token):
    parser = Parser('if var == another\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('IF', 'if')
    assert node.children[1] == var_token
    assert node.children[2].children[0] == Token('EQUAL', '==')
    assert node.children[3] == Token('WORD', 'another')


def test_parser_for_statement(var_token):
    parser = Parser('for var in items\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('FOR', 'for')
    assert node[1] == var_token
    assert node[2] == Token('IN', 'in')
    assert node[3] == Token('WORD', 'items')


def test_parser_foreach_statement():
    parser = Parser('foreach items as item\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('FOREACH', 'foreach')
    assert node[1] == Token('WORD', 'items')
    assert node[2] == Token('AS', 'as')
    assert node[3] == Token('WORD', 'item')


def test_parser_wait_statement():
    parser = Parser('wait time\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('WAIT', 'wait')
    assert node[1] == Token('WORD', 'time')


def test_parser_wait_statement_string():
    parser = Parser('wait "seconds"\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('WAIT', 'wait')
    assert node[1].children[0] == Token('DOUBLE_QUOTED', '"seconds"')


def test_parser_next_statement():
    parser = Parser('next word\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('NEXT', 'next')
    assert node.children[1] == Token('WORD', 'word')


def test_parser_next_statement_filepath():
    parser = Parser('next `path`\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('NEXT', 'next')
    assert node.children[1] == Token('FILEPATH', '`path`')


def test_parser_command():
    parser = Parser('run container\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[0] == Token('RUN', 'run')
    assert node.children[1] == Token('WORD', 'container')


def test_parser_command_option():
    parser = Parser('run container --awesome yes\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[2].children[0]
    assert node.children[2] == Token('WORD', 'awesome')
    assert node.children[3] == Token('WORD', 'yes')


def test_parser_command_arguments():
    parser = Parser('run container command "secret"\n')
    result = parser.parse()
    node = result.children[0].children[0].children[0]
    assert node.children[2].children[0] == Token('WORD', 'command')
    token = node.children[3].children[0].children[0].children[0]
    assert token == Token('DOUBLE_QUOTED', '"secret"')


@mark.parametrize('comment', ['# one', '#one'])
def test_parser_comment(comment):
    parser = Parser('{}\n'.format(comment))
    result = parser.parse()
    node = result.children[0].children[0].children[0].children[0]
    assert node == Token('COMMENT', comment)


def test_parser_block_if(var_token):
    parser = Parser('if expr\n\tvar=3\n')
    result = parser.parse()
    node = result.children[0].children
    assert node[0].children[0].children[0].children[0] == Token('IF', 'if')
    assert node[1].children[0].children[0].children[0] == var_token


def test_parser_block_nested_if_block(var_token):
    parser = Parser('if expr\n\tif things\n\tvar=3\n')
    result = parser.parse()
    node = result.children[0].children
    things_node = node[1].children[0].children[0].children[0].children[1]
    assert things_node == Token('WORD', 'things')
    assert node[2].children[0].children[0].children[0] == var_token


def test_parser_block_if_else():
    parser = Parser('if expr\n\tvar=3\nelse\n\tvar=4\n')
    result = parser.parse()
    node = result.children[1].children[0].children[0].children[0]
    assert node.children[0] == Token('ELSE', 'else')


def test_parser_block_if_elseif():
    parser = Parser('if expr\n\tvar=3\nelse if magic\n\tvar=4\n')
    result = parser.parse()
    node = result.children[1].children[0].children[0].children[0]
    assert node.children[0] == Token('ELSE', 'else')
    assert node.children[1] == Token('IF', 'if')
