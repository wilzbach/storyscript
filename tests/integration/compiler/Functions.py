# -*- coding: utf-8 -*-
from storyscript.compiler import Compiler


def test_functions_function(parser):
    """
    Ensures that functions are compiled correctly.
    """
    tree = parser.parse('function f\n\tx = 0')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'function'
    assert result['tree']['1']['function'] == 'f'
    assert result['tree']['1']['next'] == '2'
    assert result['tree']['2']['method'] == 'set'
    assert result['tree']['2']['args'] == [0]
    assert result['tree']['2']['parent'] == '1'


def test_functions_function_argument(parser):
    """
    Ensures that functions with an argument are compiled correctly
    """
    tree = parser.parse('function echo a:string\n\tx = a')
    result = Compiler.compile(tree)
    args = [{
        '$OBJECT': 'argument',
        'argument': {'$OBJECT': 'type', 'type': 'string'}, 'name': 'a'
    }]
    assert result['tree']['1']['function'] == 'echo'
    assert result['tree']['1']['args'] == args
    assert result['tree']['2']['args'] == [{'$OBJECT': 'path', 'paths': ['a']}]


def test_functions_function_returns(parser):
    """
    Ensures that functions with a return type are compiled correctly
    """
    tree = parser.parse('function f returns int\n\tx = 0')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'function'
    assert result['tree']['1']['function'] == 'f'
    assert result['tree']['1']['output'] == ['int']


def test_functions_function_return(parser):
    """
    Ensures that return statements are compiled correctly
    """
    tree = parser.parse('function f\n\treturn 0')
    result = Compiler.compile(tree)
    assert result['tree']['2']['method'] == 'return'
    assert result['tree']['2']['args'] == [0]
    assert result['tree']['2']['parent'] == '1'


def test_functions_function_call_arguments(parser):
    """
    Ensures that functions with arguments can be called
    """
    source = 'function f n:int\n\tx = 0\nf n:1\n'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'argument', 'name': 'n', 'argument': 1}]
    assert result['tree']['3']['method'] == 'call'
    assert result['tree']['3']['service'] == 'f'
    assert result['tree']['3']['args'] == args


def test_functions_function_call_without_arguments(parser):
    """
    Ensures that functions can be called without arguments
    """
    source = 'function clap\n\tx = 0\nclap\n'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['3']['method'] == 'call'
    assert result['tree']['3']['service'] == 'clap'
    assert result['tree']['3']['args'] == []


def test_functions_nested_function_call_without_arguments(parser):
    """
    Ensures that functions in nested scopes can be called without arguments
    """
    source = 'function clap\n\tx = 0\nif 2 > 1\n\tclap\n'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    print(result)
    assert result['tree']['4']['method'] == 'call'
    assert result['tree']['4']['service'] == 'clap'
    assert result['tree']['4']['args'] == []
