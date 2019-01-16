# -*- coding: utf-8 -*-
from pytest import mark

from storyscript.compiler import Compiler


def test_compiler_expression_sum(parser):
    """
    Ensures that sums are compiled correctly
    """
    tree = parser.parse('3 + 2')
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'expression', 'expression': 'sum', 'values': [3, 2]}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_sum_many(parser):
    """
    Ensures that sums of N-numbers are compiled correctly
    """
    tree = parser.parse('3 + 2 + 1')
    result = Compiler.compile(tree)
    first_sum = {'$OBJECT': 'expression', 'expression': 'sum',
                 'values': [3, 2]}
    args = [{'$OBJECT': 'expression', 'expression': 'sum',
            'values': [first_sum, 1]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_multiplication(parser):
    """
    Ensures that multiplications are compiled correctly
    """
    tree = parser.parse('3 * 2')
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'expression', 'expression': 'multiplication',
         'values': [3, 2]}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_multiplication_many(parser):
    """
    Ensures that sums of N-numbers are compiled correctly
    """
    tree = parser.parse('3 * 2 * 1')
    result = Compiler.compile(tree)
    first_node = {'$OBJECT': 'expression', 'expression': 'multiplication',
                  'values': [3, 2]}
    args = [{'$OBJECT': 'expression', 'expression': 'multiplication',
            'values': [first_node, 1]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_complex(parser):
    tree = parser.parse('3 * 2 + 1 ^ 5')
    result = Compiler.compile(tree)
    lhs = {'$OBJECT': 'expression', 'expression': 'multiplication',
           'values': [3, 2]}
    rhs = {'$OBJECT': 'expression', 'expression': 'exponential',
           'values': [1, 5]}
    args = [{'$OBJECT': 'expression', 'expression': 'sum',
            'values': [lhs, rhs]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_sum_to_parenthesis(parser):
    tree = parser.parse('1 + (2 + 3)')
    result = Compiler.compile(tree)
    rhs = {'$OBJECT': 'expression', 'expression': 'sum', 'values': [2, 3]}
    args = [{'$OBJECT': 'expression', 'expression': 'sum',
             'values': [1, rhs]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_multiplication_to_parenthesis(parser):
    tree = parser.parse('1 * (2 + 3)')
    result = Compiler.compile(tree)
    rhs = {'$OBJECT': 'expression', 'expression': 'sum', 'values': [2, 3]}
    args = [{'$OBJECT': 'expression', 'expression': 'multiplication',
             'values': [1, rhs]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_mutation(parser):
    """
    Ensures that mutations are compiled correctly
    """
    tree = parser.parse("'hello' length")
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'string', 'string': 'hello'},
        {'$OBJECT': 'mutation', 'mutation': 'length', 'arguments': []}
    ]
    assert result['tree']['1']['method'] == 'mutation'
    assert result['tree']['1']['args'] == args


@mark.parametrize('source', [
    '1 increment then format to:"string"',
    '1 increment\n\tthen format to:"string"'
])
def test_compiler_mutation_chained(parser, source):
    """
    Ensures that chained mutations are compiled correctly
    """
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    args = [1,
            {'$OBJECT': 'mutation', 'mutation': 'increment', 'arguments': []},
            {'$OBJECT': 'mutation', 'mutation': 'format', 'arguments': [
                {'$OBJECT': 'argument', 'name': 'to',
                 'argument': {'$OBJECT': 'string', 'string': 'string'}}]}]
    assert result['tree']['1']['args'] == args


def test_compiler_expression_path(parser):
    """
    Ensures that expressions with paths are compiled correctly.
    """
    tree = parser.parse('x = 3\nx + 2')
    result = Compiler.compile(tree)
    path = {'$OBJECT': 'path', 'paths': ['x']}
    assert result['tree']['2']['args'][0]['values'][0] == path


def test_compiler_if(parser):
    tree = parser.parse('if colour == "red"\n\tx = 0')
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'assertion', 'assertion': 'equals',
         'values': [{'$OBJECT': 'path', 'paths': ['colour']},
                    {'$OBJECT': 'string', 'string': 'red'}]}
    ]
    assert result['tree']['1']['method'] == 'if'
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_if_inline_expression(parser):
    tree = parser.parse('if (random numbers)\n\tx = 0')
    result = Compiler.compile(tree)
    entry = result['entrypoint']
    name = result['tree'][entry]['name']
    assert result['tree']['1']['method'] == 'if'
    assert result['tree']['1']['args'] == [{'$OBJECT': 'path', 'paths': name}]


def test_compiler_if_elseif(parser):
    source = 'if colour == "red"\n\tx = 0\nelse if colour == "blue"\n\tx = 1'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'assertion', 'assertion': 'equals',
         'values': [{'$OBJECT': 'path', 'paths': ['colour']},
                    {'$OBJECT': 'string', 'string': 'blue'}]}]
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'elif'
    assert result['tree']['3']['args'] == args
    assert result['tree']['4']['parent'] == '3'


def test_compiler_if_else(parser):
    source = 'if colour == "red"\n\tx = 0\nelse\n\tx = 1'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'else'
    assert result['tree']['4']['parent'] == '3'


def test_compiler_foreach(parser):
    tree = parser.parse('foreach items as item\n\tx = 0')
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'path', 'paths': ['items']}]
    assert result['tree']['1']['method'] == 'for'
    assert result['tree']['1']['output'] == ['item']
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_foreach_key_value(parser):
    tree = parser.parse('foreach items as key, value\n\tx = 0')
    result = Compiler.compile(tree)
    assert result['tree']['1']['output'] == ['key', 'value']


def test_compiler_while(parser):
    tree = parser.parse('while cond\n\tx = 0')
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'path', 'paths': ['cond']}]
    assert result['tree']['1']['method'] == 'while'
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_service(parser):
    """
    Ensures that services are compiled correctly
    """
    tree = parser.parse("alpine echo message:'hello'")
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'argument', 'name': 'message', 'argument':
         {'$OBJECT': 'string', 'string': 'hello'}}
    ]
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['service'] == 'alpine'
    assert result['tree']['1']['command'] == 'echo'
    assert result['tree']['1']['args'] == args


def test_compiler_service_indented_arguments(parser):
    """
    Ensures that services with indented arguments are compiled correctly
    """
    tree = parser.parse('alpine echo message:"hello"\n\tcolour:"red"')
    result = Compiler.compile(tree)
    args = [
        {'$OBJECT': 'argument', 'name': 'message', 'argument':
         {'$OBJECT': 'string', 'string': 'hello'}},
        {'$OBJECT': 'argument', 'name': 'colour', 'argument':
         {'string': 'red', '$OBJECT': 'string'}}
    ]
    assert result['tree']['1']['args'] == args


def test_compiler_service_streaming(parser):
    """
    Ensures that streaming services are compiled correctly
    """
    source = 'api stream as client\n\twhen client event as e\n\t\tx=0'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['1']['output'] == ['client']
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['method'] == 'when'
    assert result['tree']['2']['output'] == ['e']
    assert result['tree']['2']['enter'] == '3'
    assert result['tree']['3']['method'] == 'set'


def test_compiler_service_inline_expression(parser):
    """
    Ensures that inline expressions in services are compiled correctly
    """
    source = 'alpine echo text:(random strings)'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    entry = result['entrypoint']
    name = result['tree'][entry]['name']
    assert result['tree'][entry]['method'] == 'execute'
    assert result['tree'][entry]['service'] == 'random'
    assert result['tree'][entry]['command'] == 'strings'
    assert result['tree'][entry]['next'] == '1'
    path = {'$OBJECT': 'path', 'paths': name}
    argument = {'$OBJECT': 'argument', 'name': 'text', 'argument': path}
    assert result['tree']['1']['args'] == [argument]


def test_compiler_service_inline_expression_nested(parser):
    """
    Ensures that nested inline expressions are compiled correctly
    """
    source = 'slack message text:(twitter get id:(sql select))'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    entry = result['entrypoint']
    next = result['tree'][entry]['next']
    last = result['tree'][next]['next']
    assert result['tree'][entry]['service'] == 'sql'
    assert result['tree'][next]['service'] == 'twitter'
    assert result['tree'][last]['service'] == 'slack'


def test_compiler_inline_expression_access(parser):
    """
    Ensures that inline expressions followed a bracket accessor are compiled
    correctly.
    """
    tree = parser.parse('x = (random array)[0]')
    result = Compiler.compile(tree)
    entry = result['entrypoint']
    name = result['tree'][entry]['name'][0]
    args = [{'$OBJECT': 'path', 'paths': [name, '0']}]
    assert result['tree']['1']['args'] == args


def test_compiler_try(parser):
    source = 'try\n\tx=0'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'try'
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_try_catch(parser):
    source = 'try\n\tx=0\ncatch as error\n\tx=1'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['3']['output'] == ['error']
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['4']['parent'] == '3'


def test_compiler_try_finally(parser):
    source = 'try\n\tx=0\nfinally\n\tx=1'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['3']['method'] == 'finally'
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['4']['parent'] == '3'


def test_compiler_try_raise(parser):
    source = 'try\n\tx=0\ncatch as error\n\traise'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['4']['method'] == 'raise'
    assert result['tree']['4']['parent'] == '3'


def test_compiler_try_raise_error(parser):
    source = 'try\n\tx=0\ncatch as error\n\traise error'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'path', 'paths': ['error']}]
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['4']['method'] == 'raise'
    assert result['tree']['4']['parent'] == '3'
    assert result['tree']['4']['args'] == args


def test_compiler_try_nested_raise_error(parser):
    source = 'try\n\tx=0\ncatch as error\n\tif TRUE\n\t\traise error'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'path', 'paths': ['error']}]
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['5']['method'] == 'raise'
    assert result['tree']['5']['parent'] == '4'
    assert result['tree']['5']['args'] == args


def test_compiler_service_with_zero_args(parser):
    source = 'foo'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['service'] == 'foo'
    assert result['tree']['1']['args'] == []
    assert result['services'] == ['foo']


def test_compiler_break(parser):
    source = 'while true\n\tbreak'
    tree = parser.parse(source)
    result = Compiler.compile(tree)
    assert result['tree']['2']['method'] == 'break'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_empty_files(parser):
    tree = parser.parse('\n\n')
    result = Compiler.compile(tree)
    assert result['tree'] == {}
    assert result['entrypoint'] is None


def test_compiler_expression_signed_number(parser):
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Compiler.compile(parser.parse('a = -2'))
    assert result['tree']['1']['method'] == 'set'
    assert result['tree']['1']['args'] == [-2]

    result = Compiler.compile(parser.parse('a = +2'))
    assert result['tree']['1']['method'] == 'set'
    assert result['tree']['1']['args'] == [2]


def test_compiler_expression_signed_number_complex(parser):
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Compiler.compile(parser.parse('a = 2 + -3'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [2, -3]

    result = Compiler.compile(parser.parse('a = -2 + 3'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [-2, 3]


def test_compiler_expression_signed_number_absolute(parser):
    """
    Ensures that absolute signed numbers are compiled correctly
    """
    result = Compiler.compile(parser.parse('-2'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [-2]

    result = Compiler.compile(parser.parse('+2'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [2]


def test_compiler_expression_signed_float(parser):
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Compiler.compile(parser.parse('a = -5.5'))
    assert result['tree']['1']['method'] == 'set'
    assert result['tree']['1']['args'] == [-5.5]

    result = Compiler.compile(parser.parse('a = +5.5'))
    assert result['tree']['1']['method'] == 'set'
    assert result['tree']['1']['args'] == [5.5]


def test_compiler_expression_signed_float_absolute(parser):
    """
    Ensures that absolute signed numbers are compiled correctly
    """
    result = Compiler.compile(parser.parse('-5.5'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [-5.5]

    result = Compiler.compile(parser.parse('+5.5'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [5.5]


def test_compiler_expression_signed_float_complex(parser):
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Compiler.compile(parser.parse('a = 2.5 + -3.5'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [2.5, -3.5]

    result = Compiler.compile(parser.parse('a = -2.5 + 3.5'))
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [-2.5, 3.5]
