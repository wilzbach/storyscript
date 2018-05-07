# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree

from pytest import fixture, mark

from storyscript.parser import Parser


@fixture
def parser():
    return Parser()


@fixture
def int_token():
    return Token('INT', 3)


@fixture
def var_token():
    return Token('WORD', 'var')


def test_parser_values(parser, int_token):
    result = parser.parse('3\n')
    node = result.children[0].children[0].children[0].children[0].children[0]
    assert node == int_token


def test_parser_values_single_quoted_string(parser):
    result = parser.parse("'red'\n")
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('SINGLE_QUOTED', "'red'")


def test_parser_values_double_quoted_string(parser):
    result = parser.parse('"red"\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('DOUBLE_QUOTED', '"red"')


def test_parser_boolean_true(parser):
    result = parser.parse('true\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('TRUE', 'true')


def test_parser_sum(parser, int_token):
    result = parser.parse('3 + 3\n')
    node = result.children[0].children[0]
    assert node.children[0].children[0].children[0].children[0] == int_token
    assert node.children[0].children[1].children[0] == Token('PLUS', '+')
    assert node.children[0].children[2].children[0].children[0] == int_token


def test_parser_filepath(parser):
    result = parser.parse('`/path`\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node == Token('FILEPATH', '`/path`')


def test_parser_list(parser, int_token):
    result = parser.parse('[3,4]\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0].children[0].children[0] == int_token
    assert node.children[1].children[0].children[0] == Token('INT', 4)


def test_parser_list_empty(parser):
    result = parser.parse('[]\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node == Tree('list', [])


def test_parser_object(parser):
    result = parser.parse("{'color':'red','shape':1}\n")
    node = result.children[0].children[0].children[0].children[0].children[0]
    assert node.children[0].children[0] == Token('SINGLE_QUOTED', "'color'")
    value = node.children[1].children[0].children[0]
    assert value == Token('SINGLE_QUOTED', "'red'")


def test_parser_assignments(parser, var_token):
    result = parser.parse('var="hello"\n')
    node = result.children[0].children[0].children[0]
    assert node.children[0].children[0] == var_token
    assert node.children[1] == Token('EQUALS', '=')
    token = Token('DOUBLE_QUOTED', '"hello"')
    assert node.children[2].children[0].children[0] == token


def test_parser_assignments_int(parser, int_token, var_token):
    result = parser.parse('var=3\n')
    node = result.children[0].children[0].children[0]
    assert node.children[0].children[0] == var_token
    assert node.children[1] == Token('EQUALS', '=')
    assert node.children[2].children[0].children[0] == int_token


def test_parser_path_assignment(parser):
    result = parser.parse('rainbow.colors[0]="blue"\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('WORD', 'rainbow')
    assert node.children[1].children[0] == Token('WORD', 'colors')
    assert node.children[2].children[0] == Token('INT', 0)


def test_parser_if_statement(parser, var_token):
    result = parser.parse('if var\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('IF', 'if')
    assert node.children[1] == var_token


def test_parser_if_statement_comparison(parser, var_token):
    result = parser.parse('if var == another\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('IF', 'if')
    assert node.children[1] == var_token
    assert node.children[2].children[0] == Token('EQUAL', '==')
    assert node.children[3] == Token('WORD', 'another')


def test_parser_for_statement(parser, var_token):
    result = parser.parse('for var in items\n')
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('FOR', 'for')
    assert node[1] == var_token
    assert node[2] == Token('IN', 'in')
    assert node[3] == Token('WORD', 'items')


def test_parser_foreach_statement(parser):
    result = parser.parse('foreach items as item\n')
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('FOREACH', 'foreach')
    assert node[1] == Token('WORD', 'items')
    assert node[2] == Token('AS', 'as')
    assert node[3] == Token('WORD', 'item')


def test_parser_wait_statement(parser):
    result = parser.parse('wait time\n')
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('WAIT', 'wait')
    assert node[1] == Token('WORD', 'time')


def test_parser_wait_statement_string(parser):
    result = parser.parse('wait "seconds"\n')
    node = result.children[0].children[0].children[0].children[0].children
    assert node[0] == Token('WAIT', 'wait')
    assert node[1].children[0] == Token('DOUBLE_QUOTED', '"seconds"')


def test_parser_next_statement(parser):
    result = parser.parse('next word\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('NEXT', 'next')
    assert node.children[1] == Token('WORD', 'word')


def test_parser_next_statement_filepath(parser):
    result = parser.parse('next `path`\n')
    node = result.children[0].children[0].children[0].children[0]
    assert node.children[0] == Token('NEXT', 'next')
    assert node.children[1] == Token('FILEPATH', '`path`')


def test_parser_command(parser):
    result = parser.parse('run container\n')
    node = result.children[0].children[0].children[0]
    assert node.children[0] == Token('RUN', 'run')
    assert node.children[1] == Token('WORD', 'container')


def test_parser_command_option(parser):
    result = parser.parse('run container --awesome yes\n')
    node = result.children[0].children[0].children[0].children[2].children[0]
    assert node.children[2] == Token('WORD', 'awesome')
    assert node.children[3] == Token('WORD', 'yes')


def test_parser_command_arguments(parser):
    result = parser.parse('run container command "secret"\n')
    node = result.children[0].children[0].children[0]
    assert node.children[2].children[0] == Token('WORD', 'command')
    token = node.children[3].children[0].children[0].children[0]
    assert token == Token('DOUBLE_QUOTED', '"secret"')


@mark.parametrize('comment', ['# one', '#one'])
def test_parser_comment(parser, comment):
    result = parser.parse('{}\n'.format(comment))
    node = result.children[0].children[0].children[0].children[0]
    assert node == Token('COMMENT', comment)


def test_parser_block_if(parser, var_token):
    result = parser.parse('if expr\n\tvar=3\n')
    node = result.children[0].children
    assert node[0].children[0].children[0].children[0] == Token('IF', 'if')
    assert node[1].children[0].children[0].children[0].children[0] == var_token


def test_parser_block_nested_if_block(parser, var_token):
    result = parser.parse('if expr\n\tif things\n\tvar=3\n')
    node = result.children[0].children
    things_node = node[1].children[0].children[0].children[0].children[1]
    assert things_node == Token('WORD', 'things')
    assert node[2].children[0].children[0].children[0].children[0] == var_token


def test_parser_block_if_else(parser):
    result = parser.parse('if expr\n\tvar=3\nelse\n\tvar=4\n')
    node = result.children[1].children[0].children[0].children[0]
    assert node.children[0] == Token('ELSE', 'else')


def test_parser_block_if_elseif(parser):
    result = parser.parse('if expr\n\tvar=3\nelse if magic\n\tvar=4\n')
    node = result.children[1].children[0].children[0].children[0]
    assert node.children[0] == Token('ELSE', 'else')
    assert node.children[1] == Token('IF', 'if')
