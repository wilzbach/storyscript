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
