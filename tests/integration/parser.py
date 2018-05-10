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
def name_token():
    return Token('NAME', 'var')


def test_parser_values(parser, int_token):
    result = parser.parse('3\n')
    assert result.node('start.block.line.values.number').child(0) == int_token


def test_parser_values_single_quoted_string(parser):
    result = parser.parse("'red'\n")
    node = result.node('start.block.line.values.string')
    assert node.child(0) == Token('SINGLE_QUOTED', "'red'")


def test_parser_values_double_quoted_string(parser):
    result = parser.parse('"red"\n')
    node = result.node('start.block.line.values.string')
    assert node.child(0) == Token('DOUBLE_QUOTED', '"red"')


def test_parser_boolean_true(parser):
    result = parser.parse('true\n')
    node = result.node('start.block.line.values.boolean')
    assert node.child(0) == Token('TRUE', 'true')


def test_parser_sum(parser, int_token):
    result = parser.parse('3 + 3\n')
    node = result.node('start.block.line.operation')
    assert node.node('values.number').child(0) == int_token
    assert node.node('operator').child(0) == Token('PLUS', '+')
    assert node.child(2).node('number').child(0) == int_token


def test_parser_filepath(parser):
    result = parser.parse('`/path`\n')
    node = result.node('start.block.line.values')
    assert node.child(0) == Token('FILEPATH', '`/path`')


def test_parser_list(parser, int_token):
    result = parser.parse('[3,4]\n')
    node = result.node('start.block.line.values.list')
    assert node.node('values.number').child(0) == int_token
    assert node.child(1).node('values.number').child(0) == Token('INT', 4)


def test_parser_list_empty(parser):
    result = parser.parse('[]\n')
    assert result.node('start.block.line.values.list') == Tree('list', [])


def test_parser_object(parser):
    result = parser.parse("{'color':'red','shape':1}\n")
    node = result.node('start.block.line.values.objects.key_value')
    assert node.node('string').child(0) == Token('SINGLE_QUOTED', "'color'")
    value = node.node('values.string').child(0)
    assert value == Token('SINGLE_QUOTED', "'red'")


def test_parser_assignments(parser, name_token):
    result = parser.parse('var="hello"\n')
    node = result.node('start.block.line.assignments')
    assert node.node('path').child(0) == name_token
    assert node.child(1) == Token('EQUALS', '=')
    token = Token('DOUBLE_QUOTED', '"hello"')
    assert node.child(2).node('string').child(0) == token


def test_parser_assignments_int(parser, int_token, name_token):
    result = parser.parse('var=3\n')
    node = result.node('start.block.line.assignments')
    assert node.node('path').child(0) == name_token
    assert node.child(1) == Token('EQUALS', '=')
    assert node.child(2).node('number').child(0) == int_token


def test_parser_path_assignment(parser):
    result = parser.parse('rainbow.colors[0]="blue"\n')
    node = result.node('start.block.line.assignments.path')
    assert node.child(0) == Token('NAME', 'rainbow')
    assert node.child(1).child(0) == Token('NAME', 'colors')
    assert node.child(2).child(0) == Token('INT', 0)


def test_parser_if_statement(parser, name_token):
    result = parser.parse('if var\n')
    node = result.node('start.block.line.statements.if_statement')
    assert node.child(0) == Token('IF', 'if')
    assert node.child(1) == name_token


def test_parser_if_statement_comparison(parser, name_token):
    result = parser.parse('if var == another\n')
    node = result.node('start.block.line.statements.if_statement')
    assert node.child(0) == Token('IF', 'if')
    assert node.child(1) == name_token
    assert node.child(2).children[0] == Token('EQUAL', '==')
    assert node.child(3) == Token('NAME', 'another')


def test_parser_for_statement(parser, name_token):
    result = parser.parse('for var in items\n')
    node = result.node('start.block.line.statements.for_statement')
    assert node.child(0) == Token('FOR', 'for')
    assert node.child(1) == name_token
    assert node.child(2) == Token('IN', 'in')
    assert node.child(3) == Token('NAME', 'items')


def test_parser_foreach_statement(parser):
    result = parser.parse('foreach items as item\n')
    node = result.node('start.block.line.statements.foreach_statement')
    assert node.child(0) == Token('FOREACH', 'foreach')
    assert node.child(1) == Token('NAME', 'items')
    assert node.child(2) == Token('AS', 'as')
    assert node.child(3) == Token('NAME', 'item')


def test_parser_wait_statement(parser):
    result = parser.parse('wait time\n')
    node = result.node('start.block.line.statements.wait_statement')
    assert node.child(0) == Token('WAIT', 'wait')
    assert node.child(1) == Token('NAME', 'time')


def test_parser_wait_statement_string(parser):
    result = parser.parse('wait "seconds"\n')
    node = result.node('start.block.line.statements.wait_statement')
    assert node.child(0) == Token('WAIT', 'wait')
    assert node.child(1).child(0) == Token('DOUBLE_QUOTED', '"seconds"')


def test_parser_next_statement(parser):
    result = parser.parse('next word\n')
    node = result.node('start.block.line.statements.next_statement')
    assert node.child(0) == Token('NEXT', 'next')
    assert node.child(1) == Token('NAME', 'word')


def test_parser_next_statement_filepath(parser):
    result = parser.parse('next `path`\n')
    node = result.node('start.block.line.statements.next_statement')
    assert node.child(0) == Token('NEXT', 'next')
    assert node.child(1) == Token('FILEPATH', '`path`')


def test_parser_command(parser):
    result = parser.parse('org/container-name\n')
    node = result.node('start.block.line.command')
    assert node.child(0).child(0) == Token('NAME', 'org')
    assert node.child(1).child(0) == Token('BSLASH', '/')
    assert node.child(2).child(0) == Token('NAME', 'container')
    assert node.child(3).child(0) == Token('DASH', '-')
    assert node.child(4).child(0) == Token('NAME', 'name')


def test_parser_command_option(parser):
    result = parser.parse('container --awesome yes\n')
    node = result.node('start.block.line.command').child(1).node('options')
    assert node.child(2) == Token('NAME', 'awesome')
    assert node.child(3) == Token('NAME', 'yes')


def test_parser_command_arguments(parser):
    result = parser.parse('container command "secret"\n')
    print(result.pretty())
    node = result.node('start.block.line.command')
    assert node.child(1).child(0) == Token('NAME', 'command')
    token = node.child(2).node('values.string').child(0)
    assert token == Token('DOUBLE_QUOTED', '"secret"')


@mark.parametrize('comment', ['# one', '#one'])
def test_parser_comment(parser, comment):
    result = parser.parse('{}\n'.format(comment))
    node = result.node('start.block.line.comment')
    assert node.child(0) == Token('COMMENT', comment)


def test_parser_block_if(parser, name_token):
    result = parser.parse('if expr\n\tvar=3\n')
    node = result.node('block')
    if_token = node.node('line.statements.if_statement').child(0)
    assert if_token == Token('IF', 'if')
    token = node.child(1).node('block.line.assignments.path').child(0)
    assert token == name_token


def test_parser_block_nested_if_block(parser, name_token):
    result = parser.parse('if expr\n\tif things\n\tvar=3\n')
    node = result.node('block')
    things_node = node.child(1).node('line.statements.if_statement').child(1)
    assert things_node == Token('NAME', 'things')
    assert node.child(2).node('line.assignments.path').child(0) == name_token


def test_parser_block_if_else(parser):
    result = parser.parse('if expr\n\tvar=3\nelse\n\tvar=4\n')
    node = result.child(1).node('line.statements.else_statement')
    assert node.child(0) == Token('ELSE', 'else')


def test_parser_block_if_elseif(parser):
    result = parser.parse('if expr\n\tvar=3\nelse if magic\n\tvar=4\n')
    node = result.child(1).node('line.statements.elseif_statement')
    assert node.child(0) == Token('ELSE', 'else')
    assert node.child(1) == Token('IF', 'if')
