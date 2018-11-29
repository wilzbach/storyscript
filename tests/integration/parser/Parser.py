# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import mark


def test_parser_sum(parser):
    result = parser.parse('3 + 3\n')
    expression = result.block.rules.absolute_expression.expression
    fragment = expression.expression_fragment
    assert expression.values.number.child(0) == Token('INT', 3)
    assert fragment.operator.child(0) == Token('PLUS', '+')
    assert fragment.values.number.child(0) == Token('INT', 3)


def test_parser_list_path(parser):
    """
    Ensures that paths in lists can be parsed.
    """
    result = parser.parse('x = 0\n[3, x]\n')
    list = result.child(1).rules.values.list
    assert list.child(3).child(0) == Token('NAME', 'x')


@mark.parametrize('code, token', [
    ('var="hello"\n', Token('DOUBLE_QUOTED', '"hello"')),
    ('var = "hello"\n', Token('DOUBLE_QUOTED', '"hello"')),
    ('var=3\n', Token('INT', 3)),
    ('var = 3\n', Token('INT', 3))
])
def test_parser_assignment(parser, code, token):
    result = parser.parse(code)
    assignment = result.block.rules.assignment
    assert assignment.path.child(0) == Token('NAME', 'var')
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


def test_parser_if_block(parser):
    result = parser.parse('if expr\n\tvar=3\n')
    if_block = result.block.if_block
    path = if_block.if_statement.path_value.path
    assignment = if_block.nested_block.block.rules.assignment
    assert path.child(0) == Token('NAME', 'expr')
    assert assignment.path.child(0) == Token('NAME', 'var')


def test_parser_if_block_nested(parser):
    result = parser.parse('if expr\n\tif things\n\t\tvar=3\n')
    if_block = result.block.if_block.nested_block.block.if_block
    path = if_block.if_statement.path_value.path
    assignment = if_block.nested_block.block.rules.assignment
    assert path.child(0) == Token('NAME', 'things')
    assert assignment.path.child(0) == Token('NAME', 'var')


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
