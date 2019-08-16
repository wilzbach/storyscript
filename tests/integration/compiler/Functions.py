# -*- coding: utf-8 -*-
from storyscript.Api import Api


def test_functions_function():
    """
    Ensures that functions are compiled correctly.
    """
    result = Api.loads('function f\n    x = 0').result().output()
    assert result['tree']['1']['method'] == 'function'
    assert result['tree']['1']['function'] == 'f'
    assert result['tree']['1']['next'] == '2'
    assert result['tree']['2']['method'] == 'expression'
    assert result['tree']['2']['args'] == [{'$OBJECT': 'int', 'int': 0}]
    assert result['tree']['2']['parent'] == '1'


def test_functions_function_argument():
    """
    Ensures that functions with an argument are compiled correctly
    """
    result = Api.loads('function echo a:string\n    x = a').result().output()
    args = [{
        '$OBJECT': 'arg',
        'arg': {'$OBJECT': 'type', 'type': 'string'}, 'name': 'a'
    }]
    assert result['tree']['1']['function'] == 'echo'
    assert result['tree']['1']['args'] == args
    assert result['tree']['2']['args'] == [{'$OBJECT': 'path', 'paths': ['a']}]


def test_functions_function_returns():
    """
    Ensures that functions with a return type are compiled correctly
    """
    result = Api.loads('function f returns int\n    return 0').result() \
        .output()
    assert result['tree']['1']['method'] == 'function'
    assert result['tree']['1']['function'] == 'f'
    assert result['tree']['1']['output'] == ['int']


def test_functions_function_return():
    """
    Ensures that return statements are compiled correctly
    """
    result = Api.loads('function f returns int\n    return 0').result() \
        .output()
    assert result['tree']['2']['method'] == 'return'
    assert result['tree']['2']['args'] == [{'$OBJECT': 'int', 'int': 0}]
    assert result['tree']['2']['parent'] == '1'
