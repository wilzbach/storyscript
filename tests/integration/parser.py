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


@mark.parametrize('code, token', [
    ('var="hello"\n', Token('DOUBLE_QUOTED', '"hello"')),
    ('var = "hello"\n', Token('DOUBLE_QUOTED', '"hello"')),
    ('var=3\n', Token('INT', 3)),
    ('var = 3\n', Token('INT', 3))
])
def test_parser_assignment(parser, name_token, code, token):
    result = parser.parse(code)
    node = result.node('start.block.line.assignment')
    assert node.node('path').child(0) == name_token
    assert node.child(1).child(0) == Token('EQUALS', '=')
    assert node.child(1).child(1).child(0).child(0) == token


def test_parser_assignment_path(parser):
    result = parser.parse('rainbow.colors[0]="blue"\n')
    node = result.node('start.block.line.assignment.path')
    assert node.child(0) == Token('NAME', 'rainbow')
    assert node.child(1).child(0) == Token('NAME', 'colors')
    assert node.child(2).child(0) == Token('INT', 0)


def test_parser_foreach_block(parser):
    result = parser.parse('foreach items as one, two\n\tvar=3\n')
    node = result.node('start.block.foreach_block')
    foreach = node.node('foreach_statement')
    assert foreach.child(0) == Token('NAME', 'items')
    assert foreach.node('output').child(0) == Token('NAME', 'one')
    assert foreach.node('output').child(1) == Token('NAME', 'two')
    assert node.node('nested_block').data == 'nested_block'


def test_parser_service(parser):
    result = parser.parse('org/container-name command\n')
    node = result.node('start.block.line.service')
    assert node.node('path').child(0) == 'org/container-name'
    assert node.node('service_fragment.command').child(0) == 'command'


def test_parser_service_arguments(parser):
    result = parser.parse('container key:"value"\n')
    node = result.node('start.block.line.service.service_fragment.arguments')
    assert node.child(0) == Token('NAME', 'key')
    token = node.child(1).node('string').child(0)
    assert token == Token('DOUBLE_QUOTED', '"value"')


def test_parser_service_output(parser):
    result = parser.parse('container command as request, response\n')
    node = result.node('start.block.line.service.service_fragment.output')
    assert node.child(0) == Token('NAME', 'request')
    assert node.child(1) == Token('NAME', 'response')


@mark.parametrize('comment', ['# one', '#one'])
def test_parser_comment(parser, comment):
    result = parser.parse('{}\n'.format(comment))
    node = result.node('start.block.line.comment')
    assert node.child(0) == Token('COMMENT', comment)


def test_parser_if_block(parser, name_token):
    result = parser.parse('if expr\n\tvar=3\n')
    node = result.node('block.if_block')
    assert node.node('if_statement').child(0) == Token('IF', 'if')
    assert node.node('if_statement').child(1) == Token('NAME', 'expr')
    path = node.node('nested_block.block.line.assignment.path')
    assert path.child(0) == name_token


def test_parser_if_block_nested(parser, name_token):
    result = parser.parse('if expr\n\tif things\n\t\tvar=3\n')
    node = result.node('block.if_block.nested_block.block.if_block')
    assert node.node('if_statement').child(0) == Token('IF', 'if')
    assert node.node('if_statement').child(1) == Token('NAME', 'things')
    path = node.node('nested_block.block.line.assignment.path')
    assert path.child(0) == name_token


def test_parser_if_block_else(parser):
    result = parser.parse('if expr\n\tvar=3\nelse\n\tvar=4\n')
    node = result.node('block.if_block')
    assert node.child(2).child(0).child(0) == Token('ELSE', 'else')
    path = node.child(2).child(1).node('block.line.assignment.path')
    assert path.child(0) == Token('NAME', 'var')


def test_parser_if_block_elseif(parser):
    result = parser.parse('if expr\n\tvar=3\nelse if magic\n\tvar=4\n')
    node = result.node('block.if_block')
    assert node.child(2).child(0).child(0) == Token('ELSE', 'else')
    assert node.child(2).child(0).child(1) == Token('IF', 'if')
    path = node.child(2).child(1).node('block.line.assignment.path')
    assert path.child(0) == Token('NAME', 'var')


def test_parser_function(parser):
    result = parser.parse('function test\n\tvar = 3\n')
    node = result.node('block.function_block')
    assert node.node('function_statement').child(1) == Token('NAME', 'test')
    path = node.node('nested_block.block.line.assignment.path')
    assert path.child(0) == Token('NAME', 'var')


def test_parser_function_arguments(parser):
    result = parser.parse('function test n:int x:float\n\tvar = 3\n')
    node = result.node('block.function_block')
    arguments = list(node.find_data('function_argument'))
    typed_argument = arguments[0].node('typed_argument')
    assert typed_argument.child(0) == Token('NAME', 'n')
    assert typed_argument.node('types').child(0) == Token('INT_TYPE', 'int')


def test_parser_function_output(parser):
    result = parser.parse('function test n:string -> name:int\n\tvar = 1\n')
    statement = result.node('block.function_block.function_statement')
    node = statement.node('function_output.typed_argument')
    assert node.child(0) == Token('NAME', 'name')
    assert node.node('types').child(0) == Token('INT_TYPE', 'int')
