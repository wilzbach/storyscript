# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.compiler import Compiler
from storyscript.parser import Tree


def test_compiler_expression_sum():
    """
    Ensures that numbers are compiled correctly
    """
    expression = [
        {'values.number': Token('INT', 3, line=1)},
        {'operator': Token('PLUS', '+')},
        {'values.number': Token('INT', 2)}
    ]
    dict = {'start.block.rules.absolute_expression.expression': expression}
    result = Compiler.compile(Tree.from_dict(dict))
    args = [
        {'$OBJECT': 'expression', 'expression': '{} + {}', 'values': [3, 2]}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_mutation():
    """
    Ensures that mutation expressions are compiled correctly
    """
    expression = [
        {'values.string': Token('SINGLE_QUOTED', "'hello'", line=1)},
        {'mutation': Token('NAME', 'length')}
    ]
    dict = {'start.block.rules.absolute_expression.expression': expression}
    result = Compiler.compile(Tree.from_dict(dict))
    args = [
        {'$OBJECT': 'string', 'string': 'hello'},
        {'$OBJECT': 'mutation', 'mutation': 'length', 'arguments': []}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_set():
    """
    Ensures that assignments are compiled correctly
    """
    assignment = [
        {'path': Token('NAME', 'a', line=1)},
        {'assignment_fragment': [Token('EQUALS', '='),
         {'values.number': Token('INT', 0)}]}
    ]
    dict = {'start.block.rules.assignment': assignment}
    result = Compiler.compile(Tree.from_dict(dict))
    assert result['tree']['1']['method'] == 'set'
    assert result['tree']['1']['args'] == [0]


def test_compiler_set_service():
    """
    Ensures that service assignments are compiled correctly
    """
    service = [
        {'path': Token('NAME', 'alpine', line=1)},
        {'service_fragment.command': Token('NAME', 'echo')}
    ]
    assignment = [
        {'path': Token('NAME', 'a', line=1)},
        {'assignment_fragment': [Token('EQUALS', '='), {'service': service}]}
    ]
    dict = {'start.block.rules.assignment': assignment}
    result = Compiler.compile(Tree.from_dict(dict))
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['name'] == ['a']


def test_compiler_service():
    """
    Ensures that services are compiled correctly
    """
    service = [
        {'path': Token('NAME', 'alpine', line=1)},
        {'service_fragment': [
            {'command': Token('NAME', 'echo')},
            {'arguments': [Token('NAME', 'message'),
             {'values.string': Token('SINGLE_QUOTED', "'hello'")}]}
        ]}
    ]
    dict = {'start.block.service_block.service': service}
    result = Compiler.compile(Tree.from_dict(dict))
    args = [
        {'$OBJECT': 'argument', 'name': 'message', 'argument':
         {'$OBJECT': 'string', 'string': 'hello'}}
    ]
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['service'] == 'alpine'
    assert result['tree']['1']['command'] == 'echo'
    assert result['tree']['1']['args'] == args
