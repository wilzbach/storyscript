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
    """
    Ensures that parsing a number produces the expected tree
    """
    result = parser.parse('3\n')
    assert result.block.rules.values.number.child(0) == int_token


def test_parser_values_single_quoted_string(parser):
    result = parser.parse("'red'\n")
    expected = result.block.rules.values.string.child(0)
    assert expected == Token('SINGLE_QUOTED', "'red'")


def test_parser_values_double_quoted_string(parser):
    result = parser.parse('"red"\n')
    expected = result.block.rules.values.string.child(0)
    assert expected == Token('DOUBLE_QUOTED', '"red"')


def test_parser_boolean_true(parser):
    result = parser.parse('true\n')
    assert result.block.rules.values.boolean.child(0) == Token('TRUE', 'true')


def test_parser_sum(parser, int_token):
    result = parser.parse('3 + 3\n')
    expression = result.block.rules.absolute_expression.expression
    assert expression.values.number.child(0) == int_token
    assert expression.operator.child(0) == Token('PLUS', '+')
    assert expression.child(2).number.child(0) == int_token


def test_parser_list(parser, int_token):
    result = parser.parse('[3,4]\n')
    list = result.block.rules.values.list
    assert list.values.number.child(0) == int_token
    assert list.child(3).number.child(0) == Token('INT', 4)


def test_parser_list_empty(parser):
    result = parser.parse('[]\n')
    expected = Tree('list', [Token('_OSB', '['), Token('_CSB', ']')])
    assert result.block.rules.values.list == expected


def test_parser_object(parser):
    result = parser.parse("{'color':'red','shape':1}\n")
    key_value = result.block.rules.values.objects.key_value
    assert key_value.string.child(0) == Token('SINGLE_QUOTED', "'color'")
    assert key_value.values.string.child(0) == Token('SINGLE_QUOTED', "'red'")


def test_parser_regular_expression(parser):
    """
    Ensures regular expressions are parsed correctly
    """
    result = parser.parse('/^foo/')
    token = Token('REGEXP', '/^foo/')
    assert result.block.rules.values.regular_expression.child(0) == token


def test_parser_regular_expression_flags(parser):
    """
    Ensures regular expressions with flags are parsed correctly
    """
    result = parser.parse('/^foo/i')
    token = Token('NAME', 'i')
    assert result.block.rules.values.regular_expression.child(1) == token


@mark.parametrize('code, token', [
    ('var="hello"\n', Token('DOUBLE_QUOTED', '"hello"')),
    ('var = "hello"\n', Token('DOUBLE_QUOTED', '"hello"')),
    ('var=3\n', Token('INT', 3)),
    ('var = 3\n', Token('INT', 3))
])
def test_parser_assignment(parser, name_token, code, token):
    result = parser.parse(code)
    assignment = result.block.rules.assignment
    assert assignment.path.child(0) == name_token
    assert assignment.assignment_fragment.child(0) == Token('EQUALS', '=')
    assert assignment.assignment_fragment.values.child(0).child(0) == token


def test_parser_assignment_path(parser):
    result = parser.parse('rainbow.colors[0]="blue"\n')
    path = result.block.rules.assignment.path
    assert path.child(0) == Token('NAME', 'rainbow')
    assert path.path_fragment.child(0) == Token('NAME', 'colors')
    assert path.child(2).child(0) == Token('INT', 0)


def test_parser_assignment_indented_arguments(parser):
    """
    Ensures that assignments to a service with indented arguments are parsed
    correctly
    """
    result = parser.parse('x = alpine echo\n\tmessage:"hello"')
    argument = result.child(1).indented_arguments.arguments.values.string
    assert argument.child(0) == Token('DOUBLE_QUOTED', '"hello"')


def test_parser_foreach_block(parser):
    result = parser.parse('foreach items as one, two\n\tvar=3\n')
    block = result.block.foreach_block
    foreach = block.foreach_statement
    assert foreach.child(0) == Token('NAME', 'items')
    assert foreach.output.child(0) == Token('NAME', 'one')
    assert foreach.output.child(1) == Token('NAME', 'two')
    assert block.nested_block.data == 'nested_block'


def test_parser_service(parser):
    result = parser.parse('org/container-name command\n')
    service = result.block.service_block.service
    assert service.path.child(0) == 'org/container-name'
    assert service.service_fragment.command.child(0) == 'command'


def test_parser_service_arguments(parser):
    result = parser.parse('container key:"value"\n')
    args = result.block.service_block.service.service_fragment.arguments
    assert args.child(0) == Token('NAME', 'key')
    assert args.values.string.child(0) == Token('DOUBLE_QUOTED', '"value"')


def test_parser_service_output(parser):
    result = parser.parse('container command as request, response\n')
    node = result.block.service_block.service.service_fragment.output
    assert node.child(0) == Token('NAME', 'request')
    assert node.child(1) == Token('NAME', 'response')


def test_parser_if_block(parser, name_token):
    result = parser.parse('if expr\n\tvar=3\n')
    if_block = result.block.if_block
    path = if_block.if_statement.path_value.path
    assignment = if_block.nested_block.block.rules.assignment
    assert path.child(0) == Token('NAME', 'expr')
    assert assignment.path.child(0) == name_token


def test_parser_if_block_nested(parser, name_token):
    result = parser.parse('if expr\n\tif things\n\t\tvar=3\n')
    if_block = result.block.if_block.nested_block.block.if_block
    path = if_block.if_statement.path_value.path
    assignment = if_block.nested_block.block.rules.assignment
    assert path.child(0) == Token('NAME', 'things')
    assert assignment.path.child(0) == name_token


def test_parser_if_block_else(parser):
    result = parser.parse('if expr\n\tvar=3\nelse\n\tvar=4\n')
    node = result.block.if_block.else_block.nested_block.block.rules
    assert node.assignment.path.child(0) == Token('NAME', 'var')


def test_parser_if_block_elseif(parser):
    result = parser.parse('if expr\n\tvar=3\nelse if magic\n\tvar=4\n')
    node = result.block.if_block.elseif_block.nested_block.block.rules
    assert node.assignment.path.child(0) == Token('NAME', 'var')


def test_parser_function(parser):
    result = parser.parse('function test\n\tvar = 3\n')
    node = result.block.function_block
    path = node.nested_block.block.rules.assignment.path
    assert node.function_statement.child(1) == Token('NAME', 'test')
    assert path.child(0) == Token('NAME', 'var')


def test_parser_function_arguments(parser):
    result = parser.parse('function test n:int\n\tvar = 3\n')
    typed_argument = result.block.function_block.find('typed_argument')[0]
    assert typed_argument.child(0) == Token('NAME', 'n')
    assert typed_argument.types.child(0) == Token('INT_TYPE', 'int')


def test_parser_function_output(parser):
    result = parser.parse('function test n:string returns int\n\tvar = 1\n')
    statement = result.block.function_block.function_statement
    assert statement.function_output.types.child(0) == Token('INT_TYPE', 'int')


def test_parser_try(parser):
    result = parser.parse('try\n\tx=0')
    try_block = result.block.try_block
    assert try_block.try_statement.child(0) == Token('TRY', 'try')
    path = try_block.nested_block.block.rules.assignment.path
    assert path.child(0) == Token('NAME', 'x')


def test_parser_try_catch(parser):
    result = parser.parse('try\n\tx=0\ncatch as error\n\tx=1')
    catch_block = result.block.try_block.catch_block
    assert catch_block.catch_statement.child(0) == Token('NAME', 'error')
    path = catch_block.nested_block.block.rules.assignment.path
    assert path.child(0) == Token('NAME', 'x')


def test_parser_try_finally(parser):
    result = parser.parse('try\n\tx=0\nfinally\n\tx=1')
    finally_block = result.block.try_block.finally_block
    token = Token('FINALLY', 'finally')
    assert finally_block.finally_statement.child(0) == token
    path = finally_block.nested_block.block.rules.assignment.path
    assert path.child(0) == Token('NAME', 'x')
