# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture

from storyscript.compiler import Compiler
from storyscript.parser import Parser


@fixture
def parser():
    return Parser()


def test_compiler_expression_sum(parser):
    """
    Ensures that numbers are compiled correctly
    """
    result = Compiler.compile(parser.parse('3 + 2'))
    args = [
        {'$OBJECT': 'expression', 'expression': '{} + {}', 'values': [3, 2]}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_mutation(parser):
    """
    Ensures that mutation expressions are compiled correctly
    """
    result = Compiler.compile(parser.parse("'hello' length"))
    args = [
        {'$OBJECT': 'string', 'string': 'hello'},
        {'$OBJECT': 'mutation', 'mutation': 'length', 'arguments': []}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_set(parser):
    """
    Ensures that assignments are compiled correctly
    """
    result = Compiler.compile(parser.parse('a = 0'))
    assert result['tree']['1']['method'] == 'set'
    assert result['tree']['1']['args'] == [0]


def test_compiler_set_service(parser):
    """
    Ensures that service assignments are compiled correctly
    """
    result = Compiler.compile(parser.parse('a = alpine echo'))
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['name'] == ['a']


def test_compiler_service(parser):
    """
    Ensures that services are compiled correctly
    """
    result = Compiler.compile(parser.parse("alpine echo message:'hello'"))
    args = [
        {'$OBJECT': 'argument', 'name': 'message', 'argument':
         {'$OBJECT': 'string', 'string': 'hello'}}
    ]
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['service'] == 'alpine'
    assert result['tree']['1']['command'] == 'echo'
    assert result['tree']['1']['args'] == args
