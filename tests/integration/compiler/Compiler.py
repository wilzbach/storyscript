# -*- coding: utf-8 -*-
from pytest import mark

from storyscript.Api import Api


def test_compiler_expression_sum():
    """
    Ensures that sums are compiled correctly
    """
    result = Api.loads('3 + 2')
    args = [
        {'$OBJECT': 'expression', 'expression': 'sum', 'values': [3, 2]}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_sum_many():
    """
    Ensures that sums of N-numbers are compiled correctly
    """
    result = Api.loads('3 + 2 + 1')
    first_sum = {'$OBJECT': 'expression', 'expression': 'sum',
                 'values': [3, 2]}
    args = [{'$OBJECT': 'expression', 'expression': 'sum',
            'values': [first_sum, 1]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_multiplication():
    """
    Ensures that multiplications are compiled correctly
    """
    result = Api.loads('3 * 2')
    args = [
        {'$OBJECT': 'expression', 'expression': 'multiplication',
         'values': [3, 2]}
    ]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_multiplication_many():
    """
    Ensures that sums of N-numbers are compiled correctly
    """
    result = Api.loads('3 * 2 * 1')
    first_node = {'$OBJECT': 'expression', 'expression': 'multiplication',
                  'values': [3, 2]}
    args = [{'$OBJECT': 'expression', 'expression': 'multiplication',
            'values': [first_node, 1]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_complex():
    result = Api.loads('3 * 2 + 1 ^ 5')
    lhs = {'$OBJECT': 'expression', 'expression': 'multiplication',
           'values': [3, 2]}
    rhs = {'$OBJECT': 'expression', 'expression': 'exponential',
           'values': [1, 5]}
    args = [{'$OBJECT': 'expression', 'expression': 'sum',
            'values': [lhs, rhs]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_sum_to_parenthesis():
    result = Api.loads('1 + (2 + 3)')
    rhs = {'$OBJECT': 'expression', 'expression': 'sum', 'values': [2, 3]}
    args = [{'$OBJECT': 'expression', 'expression': 'sum',
             'values': [1, rhs]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_expression_multiplication_to_parenthesis():
    result = Api.loads('1 * (2 + 3)')
    rhs = {'$OBJECT': 'expression', 'expression': 'sum', 'values': [2, 3]}
    args = [{'$OBJECT': 'expression', 'expression': 'multiplication',
             'values': [1, rhs]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_compiler_mutation():
    """
    Ensures that mutations are compiled correctly
    """
    result = Api.loads("'hello' length")
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
def test_compiler_mutation_chained(source):
    """
    Ensures that chained mutations are compiled correctly
    """
    result = Api.loads(source)
    args = [1,
            {'$OBJECT': 'mutation', 'mutation': 'increment', 'arguments': []},
            {'$OBJECT': 'mutation', 'mutation': 'format', 'arguments': [
                {'$OBJECT': 'argument', 'name': 'to',
                 'argument': {'$OBJECT': 'string', 'string': 'string'}}]}]
    assert result['tree']['1']['args'] == args


def test_compiler_expression_path():
    """
    Ensures that expressions with paths are compiled correctly.
    """
    result = Api.loads('x = 3\nx + 2')
    path = {'$OBJECT': 'path', 'paths': ['x']}
    assert result['tree']['2']['args'][0]['values'][0] == path


def test_compiler_foreach():
    result = Api.loads('foreach items as item\n\tx = 0')
    args = [{'$OBJECT': 'path', 'paths': ['items']}]
    assert result['tree']['1']['method'] == 'for'
    assert result['tree']['1']['output'] == ['item']
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_foreach_key_value():
    result = Api.loads('foreach items as key, value\n\tx = 0')
    assert result['tree']['1']['output'] == ['key', 'value']


def test_compiler_while():
    result = Api.loads('while cond\n\tx = 0')
    args = [{'$OBJECT': 'path', 'paths': ['cond']}]
    assert result['tree']['1']['method'] == 'while'
    assert result['tree']['1']['args'] == args
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_service():
    """
    Ensures that services are compiled correctly
    """
    result = Api.loads("alpine echo message:'hello'")
    args = [
        {'$OBJECT': 'argument', 'name': 'message', 'argument':
         {'$OBJECT': 'string', 'string': 'hello'}}
    ]
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['service'] == 'alpine'
    assert result['tree']['1']['command'] == 'echo'
    assert result['tree']['1']['args'] == args


def test_compiler_service_indented_arguments():
    """
    Ensures that services with indented arguments are compiled correctly
    """
    result = Api.loads('alpine echo message:"hello"\n\tcolour:"red"')
    args = [
        {'$OBJECT': 'argument', 'name': 'message', 'argument':
         {'$OBJECT': 'string', 'string': 'hello'}},
        {'$OBJECT': 'argument', 'name': 'colour', 'argument':
         {'string': 'red', '$OBJECT': 'string'}}
    ]
    assert result['tree']['1']['args'] == args


def test_compiler_service_streaming():
    """
    Ensures that streaming services are compiled correctly
    """
    source = 'api stream as client\n\twhen client event as e\n\t\tx=0'
    result = Api.loads(source)
    assert result['tree']['1']['output'] == ['client']
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['method'] == 'when'
    assert result['tree']['2']['output'] == ['e']
    assert result['tree']['2']['enter'] == '3'
    assert result['tree']['3']['method'] == 'expression'


def test_compiler_service_inline_expression():
    """
    Ensures that inline expressions in services are compiled correctly
    """
    source = 'alpine echo text:(random strings)'
    result = Api.loads(source)
    entry = result['entrypoint']
    name = result['tree'][entry]['name']
    assert result['tree'][entry]['method'] == 'execute'
    assert result['tree'][entry]['service'] == 'random'
    assert result['tree'][entry]['command'] == 'strings'
    assert result['tree'][entry]['next'] == '1'
    path = {'$OBJECT': 'path', 'paths': name}
    argument = {'$OBJECT': 'argument', 'name': 'text', 'argument': path}
    assert result['tree']['1']['args'] == [argument]


def test_compiler_service_inline_expression_nested():
    """
    Ensures that nested inline expressions are compiled correctly
    """
    source = 'slack message text:(twitter get id:(sql select))'
    result = Api.loads(source)
    entry = result['entrypoint']
    next = result['tree'][entry]['next']
    last = result['tree'][next]['next']
    assert result['tree'][entry]['service'] == 'sql'
    assert result['tree'][next]['service'] == 'twitter'
    assert result['tree'][last]['service'] == 'slack'


def test_compiler_inline_expression_access():
    """
    Ensures that inline expressions followed a bracket accessor are compiled
    correctly.
    """
    result = Api.loads('x = (random array)[0]')
    entry = result['entrypoint']
    name = result['tree'][entry]['name'][0]
    args = [{'$OBJECT': 'path', 'paths': [name, '0']}]
    assert result['tree']['1']['args'] == args


def test_compiler_try():
    source = 'try\n\tx=0'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'try'
    assert result['tree']['1']['enter'] == '2'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_try_catch():
    source = 'try\n\tx=0\ncatch as error\n\tx=1'
    result = Api.loads(source)
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['3']['output'] == ['error']
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['4']['parent'] == '3'


def test_compiler_try_finally():
    source = 'try\n\tx=0\nfinally\n\tx=1'
    result = Api.loads(source)
    assert result['tree']['3']['method'] == 'finally'
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['4']['parent'] == '3'


def test_compiler_try_throw():
    source = 'try\n\tx=0\ncatch as error\n\tthrow'
    result = Api.loads(source)
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['4']['method'] == 'throw'
    assert result['tree']['4']['parent'] == '3'


def test_compiler_try_throw_error():
    source = 'try\n\tx=0\ncatch as error\n\tthrow error'
    result = Api.loads(source)
    args = [{'$OBJECT': 'path', 'paths': ['error']}]
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['4']['method'] == 'throw'
    assert result['tree']['4']['parent'] == '3'
    assert result['tree']['4']['args'] == args


def test_compiler_try_nested_throw_error():
    source = 'try\n\tx=0\ncatch as error\n\tif TRUE\n\t\tthrow error'
    result = Api.loads(source)
    args = [{'$OBJECT': 'path', 'paths': ['error']}]
    assert result['tree']['1']['exit'] == '3'
    assert result['tree']['3']['method'] == 'catch'
    assert result['tree']['3']['enter'] == '4'
    assert result['tree']['5']['method'] == 'throw'
    assert result['tree']['5']['parent'] == '4'
    assert result['tree']['5']['args'] == args


def test_compiler_break():
    source = 'while true\n\tbreak'
    result = Api.loads(source)
    assert result['tree']['2']['method'] == 'break'
    assert result['tree']['2']['parent'] == '1'


def test_compiler_empty_files():
    result = Api.loads('\n\n')
    assert result['tree'] == {}
    assert result['entrypoint'] is None


def test_compiler_expression_signed_number():
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Api.loads('a = -2')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [-2]

    result = Api.loads('a = +2')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [2]


def test_compiler_expression_signed_number_complex():
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Api.loads('a = 2 + -3')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [2, -3]

    result = Api.loads('a = -2 + 3')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [-2, 3]


def test_compiler_expression_signed_number_absolute():
    """
    Ensures that absolute signed numbers are compiled correctly
    """
    result = Api.loads('-2')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [-2]

    result = Api.loads('+2')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [2]


def test_compiler_expression_signed_float():
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Api.loads('a = -5.5')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [-5.5]

    result = Api.loads('a = +5.5')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [5.5]


def test_compiler_expression_signed_float_absolute():
    """
    Ensures that absolute signed numbers are compiled correctly
    """
    result = Api.loads('-5.5')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [-5.5]

    result = Api.loads('+5.5')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [5.5]


def test_compiler_expression_signed_float_complex():
    """
    Ensures that signed numbers are compiled correctly
    """
    result = Api.loads('a = 2.5 + -3.5')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [2.5, -3.5]

    result = Api.loads('a = -2.5 + 3.5')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [-2.5, 3.5]


def test_compiler_expression_exponential_flat():
    """
    Ensures that exponential expressions are not nested
    """
    result = Api.loads('2 ^ 3')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'exponential'
    assert result['tree']['1']['args'][0]['values'] == [2, 3]


def test_compiler_complex_nested_expression():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '2 + 3 / 4'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'sum',
        'values': [
          2,
          {
            '$OBJECT': 'expression',
            'expression': 'division',
            'values': [
              3,
              4
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_2():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = 'true and 1 + 1 == 2 or 3'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'and',
            'values': [
              True,
              {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  {
                    '$OBJECT': 'expression',
                    'expression': 'sum',
                    'values': [
                      1,
                      1
                    ]
                  },
                  2
                ]
              }
            ]
          },
          3
        ]
    }]


def test_compiler_complex_nested_expression_3():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '0 + 1 * 2 - 3 / 4 % 5 == 6 ^ 2 > 7 or 8'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'greater',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  {
                    '$OBJECT': 'expression',
                    'expression': 'subtraction',
                    'values': [
                      {
                        '$OBJECT': 'expression',
                        'expression': 'sum',
                        'values': [
                          0,
                          {
                            '$OBJECT': 'expression',
                            'expression': 'multiplication',
                            'values': [
                              1,
                              2
                            ]
                          }
                        ]
                      },
                      {
                        '$OBJECT': 'expression',
                        'expression': 'modulus',
                        'values': [
                          {
                            '$OBJECT': 'expression',
                            'expression': 'division',
                            'values': [
                              3,
                              4
                            ]
                          },
                          5
                        ]
                      }
                    ]
                  },
                  {
                    '$OBJECT': 'expression',
                    'expression': 'exponential',
                    'values': [
                      6,
                      2
                    ]
                  }
                ]
              },
              7
            ]
          },
          8
        ]
    }]


def test_compiler_complex_nested_expression_4():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '1 % 2 + 3 - -4'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'subtraction',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'sum',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'modulus',
                'values': [
                  1,
                  2
                ]
              },
              3
            ]
          },
          -4
        ]
    }]


def test_compiler_complex_nested_expression_5():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = ('1 + 0.1 < 2 - 0.2 <= 3 / 0.3 '
              '== 4 * 0.4 != 5 * 0.5 > 6 * 0.6 >= 7 * 0.7')
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'greater_equal',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'greater',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'not_equal',
                'values': [
                  {
                    '$OBJECT': 'expression',
                    'expression': 'equals',
                    'values': [
                      {
                        '$OBJECT': 'expression',
                        'expression': 'less_equal',
                        'values': [
                          {
                            '$OBJECT': 'expression',
                            'expression': 'less',
                            'values': [
                              {
                                '$OBJECT': 'expression',
                                'expression': 'sum',
                                'values': [
                                  1,
                                  0.1
                                ]
                              },
                              {
                                '$OBJECT': 'expression',
                                'expression': 'subtraction',
                                'values': [
                                  2,
                                  0.2
                                ]
                              }
                            ]
                          },
                          {
                            '$OBJECT': 'expression',
                            'expression': 'division',
                            'values': [
                              3,
                              0.3
                            ]
                          }
                        ]
                      },
                      {
                        '$OBJECT': 'expression',
                        'expression': 'multiplication',
                        'values': [
                          4,
                          0.4
                        ]
                      }
                    ]
                  },
                  {
                    '$OBJECT': 'expression',
                    'expression': 'multiplication',
                    'values': [
                      5,
                      0.5
                    ]
                  }
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'multiplication',
                'values': [
                  6,
                  0.6
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'multiplication',
            'values': [
              7,
              0.7
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_6():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '1 and 2 or 3 and 4 or 5'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'or',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'and',
                'values': [
                  1,
                  2
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'and',
                'values': [
                  3,
                  4
                ]
              }
            ]
          },
          5
        ]
    }]


def test_compiler_complex_nested_expression_7():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '1 and (2 or 3) and (4 or 5)'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'and',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'and',
            'values': [
              1,
              {
                '$OBJECT': 'expression',
                'expression': 'or',
                'values': [
                  2,
                  3
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'or',
            'values': [
              4,
              5
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_8():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '(1 + 2) == (0 - -3) and -4 - (-5 + -6)'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'and',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'equals',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'sum',
                'values': [
                  1,
                  2
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'subtraction',
                'values': [
                  0,
                  -3
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'subtraction',
            'values': [
              -4,
              {
                '$OBJECT': 'expression',
                'expression': 'sum',
                'values': [
                  -5,
                  -6
                ]
              }
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_9():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = 'foo[0] > 5 + foo[1] and foo[1]'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'and',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'greater',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'foo',
                  '0'
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'sum',
                'values': [
                  5,
                  {
                    '$OBJECT': 'path',
                    'paths': [
                      'foo',
                      '1'
                    ]
                  }
                ]
              }
            ]
          },
          {
            '$OBJECT': 'path',
            'paths': [
              'foo',
              '1'
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_10():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = """d['a'] + list[0] / list[1] * d['a'] % d['b']"""
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'sum',
        'values': [
          {
            '$OBJECT': 'path',
            'paths': [
              'd',
              {
                '$OBJECT': 'string',
                'string': 'a'
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'modulus',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'multiplication',
                'values': [
                  {
                    '$OBJECT': 'expression',
                    'expression': 'division',
                    'values': [
                      {
                        '$OBJECT': 'path',
                        'paths': [
                          'list',
                          '0'
                        ]
                      },
                      {
                        '$OBJECT': 'path',
                        'paths': [
                          'list',
                          '1'
                        ]
                      }
                    ]
                  },
                  {
                    '$OBJECT': 'path',
                    'paths': [
                      'd',
                      {
                        '$OBJECT': 'string',
                        'string': 'a'
                      }
                    ]
                  }
                ]
              },
              {
                '$OBJECT': 'path',
                'paths': [
                  'd',
                  {
                    '$OBJECT': 'string',
                    'string': 'b'
                  }
                ]
              }
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_11():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '1 == 2 != 3 < 4 == 5 + 6 - 7 * 8 > 9 <= 10'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'less_equal',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'greater',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  {
                    '$OBJECT': 'expression',
                    'expression': 'less',
                    'values': [
                      {
                        '$OBJECT': 'expression',
                        'expression': 'not_equal',
                        'values': [
                          {
                            '$OBJECT': 'expression',
                            'expression': 'equals',
                            'values': [
                              1,
                              2
                            ]
                          },
                          3
                        ]
                      },
                      4
                    ]
                  },
                  {
                    '$OBJECT': 'expression',
                    'expression': 'subtraction',
                    'values': [
                      {
                        '$OBJECT': 'expression',
                        'expression': 'sum',
                        'values': [
                          5,
                          6
                        ]
                      },
                      {
                        '$OBJECT': 'expression',
                        'expression': 'multiplication',
                        'values': [
                          7,
                          8
                        ]
                      }
                    ]
                  }
                ]
              },
              9
            ]
          },
          10
        ]
    }]


def test_compiler_complex_nested_expression_12():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '1 == (foo contains)'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1.1']['service'] == 'foo'
    assert result['tree']['1.1']['name'] == ['p-1.1']
    assert result['tree']['1.1']['command'] == 'contains'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'equals',
        'values': [
          1,
          {
            '$OBJECT': 'path',
            'paths': [
              'p-1.1'
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_13():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = 'a + b -c / d'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'subtraction',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'sum',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'a'
                ]
              },
              {
                '$OBJECT': 'path',
                'paths': [
                  'b'
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'division',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'c'
                ]
              },
              {
                '$OBJECT': 'path',
                'paths': [
                  'd'
                ]
              }
            ]
          }
        ]
    }]


def test_compiler_complex_nested_expression_14():
    """
    Ensures that complex nested expressions are compiled correctly
    """
    source = '((0 == 1)) + (d[\'a\'])'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'sum',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'equals',
            'values': [
              0,
              1
            ]
          },
          {
            '$OBJECT': 'path',
            'paths': [
              'd',
              {
                '$OBJECT': 'string',
                'string': 'a'
              }
            ]
          }
        ]
    }]


def test_compiler_list_expression():
    """
    Ensures that list accept arbitrary expressions
    """
    result = Api.loads('a = [b + c, 1 / 2 + 3]')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'list',
        'items': [
          {
            '$OBJECT': 'expression',
            'expression': 'sum',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'b'
                ]
              },
              {
                '$OBJECT': 'path',
                'paths': [
                  'c'
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'sum',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'division',
                'values': [
                  1,
                  2
                ]
              },
              3
            ]
          }
        ]
    }]


def test_compiler_object_expression():
    """
    Ensures that objects accept arbitrary expressions
    """
    source = 'a = {"1": b - c, "2": 1 % 2 - 3}'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'dict',
        'items': [
          [
            {
              '$OBJECT': 'string',
              'string': '1'
            },
            {
              '$OBJECT': 'expression',
              'expression': 'subtraction',
              'values': [
                {
                  '$OBJECT': 'path',
                  'paths': [
                    'b'
                  ]
                },
                {
                  '$OBJECT': 'path',
                  'paths': [
                    'c'
                  ]
                }
              ]
            }
          ],
          [
            {
              '$OBJECT': 'string',
              'string': '2'
            },
            {
              '$OBJECT': 'expression',
              'expression': 'subtraction',
              'values': [
                {
                  '$OBJECT': 'expression',
                  'expression': 'modulus',
                  'values': [
                    1,
                    2
                  ]
                },
                3
              ]
            }
          ]
        ]
    }]


def test_compiler_mutation_assignment():
    """
    Ensures that mutation assignments compile correctly
    """
    source = 'a = "hello world"\nb = a uppercase'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['2']['method'] == 'mutation'
    assert result['tree']['2']['name'] == ['b']
    assert result['tree']['2']['args'] == [
        {
          '$OBJECT': 'path',
          'paths': [
            'a'
          ]
        },
        {
          '$OBJECT': 'mutation',
          'mutation': 'uppercase',
          'arguments': []
        }
    ]


def path(name):
    """
    Generate a path object
    """
    return {'$OBJECT': 'path', 'paths': [name]}


@mark.parametrize('source_pair', [
    ('1+2', 'sum', [1, 2]),
    ('1+-2', 'sum', [1, -2]),
    ('1-3', 'subtraction', [1, 3]),
    ('1--3', 'subtraction', [1, -3]),
    ('0*2', 'multiplication', [0, 2]),
    ('0*-2', 'multiplication', [0, -2]),
    ('1/6', 'division', [1, 6]),
    ('1/-6', 'division', [1, -6]),
    ('0%2', 'modulus', [0, 2]),
    ('0%-2', 'modulus', [0, -2]),
    ('1==2', 'equals', [1, 2]),
    ('1==-2', 'equals', [1, -2]),
    ('1!=2', 'not_equal', [1, 2]),
    ('1!=-2', 'not_equal', [1, -2]),
    ('1<2', 'less', [1, 2]),
    ('1<-2', 'less', [1, -2]),
    ('1>2', 'greater', [1, 2]),
    ('1>-2', 'greater', [1, -2]),
    ('1<=2', 'less_equal', [1, 2]),
    ('1<=-2', 'less_equal', [1, -2]),
    ('1>=2', 'greater_equal', [1, 2]),
    ('-1>=2', 'greater_equal', [-1, 2]),
    ('1>=-2', 'greater_equal', [1, -2]),
    ('b+c', 'sum', [path('b'), path('c')]),
    # Currently a valid entity
    # ('b-c', 'subtraction', [path('b'), path('c')]),
    ('b*c', 'multiplication', [path('b'), path('c')]),
    # Currently a valid entity
    # ('b/c', 'divison', [path('b'), path('c')]),
    ('b%c', 'modulus', [path('b'), path('c')]),
    ('b==c', 'equals', [path('b'), path('c')]),
    ('b!=c', 'not_equal', [path('b'), path('c')]),
    ('b<c', 'less', [path('b'), path('c')]),
    ('b>c', 'greater', [path('b'), path('c')]),
    ('b<=c', 'less_equal', [path('b'), path('c')]),
    ('b>=c', 'greater_equal', [path('b'), path('c')]),
])
def test_compiler_expression_whitespace(source_pair):
    """
    Ensures that expression isn't whitespace sensitive
    """
    source, expression, values = source_pair
    source = 'a=' + source
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert len(result['tree']['1']['args']) == 1
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == expression
    assert result['tree']['1']['args'][0]['values'] == values


def test_compiler_complex_while():
    """
    Ensures that while statements with an expression are compiled correctly
    """
    result = Api.loads('while i < 10\n\ti = i + 1')
    assert result['tree']['1']['method'] == 'while'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'less'
    assert result['tree']['1']['args'][0]['values'] == [
        {
          '$OBJECT': 'path',
          'paths': [
            'i'
          ]
        }, 10
    ]


def test_compiler_complex_while_2():
    """
    Ensures that while statements with an expression are compiled correctly
    """
    source = 'while a + b == c or d\n\ti = i + 1'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'while'
    assert result['tree']['1']['args'] == [{
          '$OBJECT': 'expression',
          'expression': 'or',
          'values': [
            {
              '$OBJECT': 'expression',
              'expression': 'equals',
              'values': [
                {
                  '$OBJECT': 'expression',
                  'expression': 'sum',
                  'values': [
                    {
                      '$OBJECT': 'path',
                      'paths': [
                        'a'
                      ]
                    },
                    {
                      '$OBJECT': 'path',
                      'paths': [
                        'b'
                      ]
                    }
                  ]
                },
                {
                  '$OBJECT': 'path',
                  'paths': [
                    'c'
                  ]
                }
              ]
            },
            {
              '$OBJECT': 'path',
              'paths': [
                'd'
              ]
            }
          ]
    }]


def test_compiler_mutation_expression():
    """
    Ensures that mutations with expressions are compiled correctly
    """
    source = ('a = ["opened", "labeled"]\n'
              'a contains item: req.body["action"] == false')
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['2']['method'] == 'mutation'
    assert result['tree']['2']['args'] == [
        {
          '$OBJECT': 'path',
          'paths': [
            'a'
          ]
        },
        {
          '$OBJECT': 'mutation',
          'mutation': 'contains',
          'arguments': [
            {
              '$OBJECT': 'argument',
              'name': 'item',
              'argument': {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  {
                    '$OBJECT': 'path',
                    'paths': [
                      'req',
                      'body',
                      {
                        '$OBJECT': 'string',
                        'string': 'action'
                      }
                    ]
                  },
                  False
                ]
              }
            }
          ]
        }
    ]


def test_compiler_service_expression():
    """
    Ensures that mutations with expressions are compiled correctly
    """
    source = 'my_service my_command k1: 2 + 2 k2: a == b'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['command'] == 'my_command'
    assert result['tree']['1']['service'] == 'my_service'
    assert result['tree']['1']['args'] == [
        {
          '$OBJECT': 'argument',
          'name': 'k1',
          'argument': {
            '$OBJECT': 'expression',
            'expression': 'sum',
            'values': [
              2,
              2
            ]
          }
        },
        {
          '$OBJECT': 'argument',
          'name': 'k2',
          'argument': {
            '$OBJECT': 'expression',
            'expression': 'equals',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'a'
                ]
              },
              {
                '$OBJECT': 'path',
                'paths': [
                  'b'
                ]
              }
            ]
          }
        }
    ]


def test_compiler_mutation_expression_list():
    """
    Ensures that mutations on lists work
    """
    source = '["opened", "labeled"] contains item: "opened"'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'mutation'
    assert result['tree']['1']['args'] == [
        {
          '$OBJECT': 'list',
          'items': [
            {
              '$OBJECT': 'string',
              'string': 'opened'
            },
            {
              '$OBJECT': 'string',
              'string': 'labeled'
            }
          ]
        },
        {
          '$OBJECT': 'mutation',
          'mutation': 'contains',
          'arguments': [
            {
              '$OBJECT': 'argument',
              'name': 'item',
              'argument': {
                '$OBJECT': 'string',
                'string': 'opened'
              }
            }
          ]
        }
    ]


def test_compiler_mutation_expression_object():
    """
    Ensures that mutations on objects work
    """
    source = '{"opened":1, "labeled":1} has key: "opened"'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'mutation'
    assert result['tree']['1']['args'] == [
        {
          '$OBJECT': 'dict',
          'items': [
            [
              {
                '$OBJECT': 'string',
                'string': 'opened'
              },
              1
            ],
            [
              {
                '$OBJECT': 'string',
                'string': 'labeled'
              },
              1
            ]
          ]
        },
        {
          '$OBJECT': 'mutation',
          'mutation': 'has',
          'arguments': [
            {
              '$OBJECT': 'argument',
              'name': 'key',
              'argument': {
                '$OBJECT': 'string',
                'string': 'opened'
              }
            }
          ]
        }
    ]


def test_compiler_return_complex_expression():
    """
    Ensures that return accepts arbitrary expressions
    """
    source = 'function name key:int\n\treturn 2 + 2'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'function'
    assert result['tree']['1']['function'] == 'name'
    assert result['tree']['2']['method'] == 'return'
    assert result['tree']['2']['args'] == [{
      '$OBJECT': 'expression',
      'expression': 'sum',
      'values': [
        2,
        2
      ]
    }]


def test_compiler_return_complex_expression_2():
    """
    Ensures that return accepts arbitrary expressions
    """
    source = 'function name key:int\n\treturn a / b + c or d'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'function'
    assert result['tree']['1']['function'] == 'name'
    assert result['tree']['2']['method'] == 'return'
    assert result['tree']['2']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'sum',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'division',
                'values': [
                  {
                    '$OBJECT': 'path',
                    'paths': [
                      'a'
                    ]
                  },
                  {
                    '$OBJECT': 'path',
                    'paths': [
                      'b'
                    ]
                  }
                ]
              },
              {
                '$OBJECT': 'path',
                'paths': [
                  'c'
                ]
              }
            ]
          },
          {
            '$OBJECT': 'path',
            'paths': [
              'd'
            ]
          }
        ]
    }]


def test_compiler_unary_not():
    """
    Ensures that unary expressions are compiled correctly
    """
    source = 'a = !b'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'not',
        'values': [
          {
            '$OBJECT': 'path',
            'paths': [
              'b'
            ]
          }
        ]
    }]


def test_compiler_unary_double():
    """
    Ensures that double unary expressions are compiled correctly
    """
    source = 'a = !!b'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'not',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'not',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'b'
                ]
              }
            ]
          }
        ]
    }]


def test_compiler_unary_complex():
    """
    Ensures that complex unary expressions are compiled correctly
    """
    source = 'a = b and !c'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'and',
        'values': [
          {
            '$OBJECT': 'path',
            'paths': [
              'b'
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'not',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'c'
                ]
              }
            ]
          }
        ]
    }]


def test_compiler_unary_complex_2():
    """
    Ensures that complex unary expressions are compiled correctly
    """
    source = 'a = ! 2 == !3 or ! 4'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'equals',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'not',
                'values': [
                  2
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'not',
                'values': [
                  3
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'not',
            'values': [
              4
            ]
          }
        ]
    }]


def test_compiler_unary_complex_3():
    """
    Ensures that complex unary expressions are compiled correctly
    """
    source = 'a = [! b, !2] <= ! t + t'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'less_equal',
        'values': [
          {
            '$OBJECT': 'list',
            'items': [
              {
                '$OBJECT': 'expression',
                'expression': 'not',
                'values': [
                  {
                    '$OBJECT': 'path',
                    'paths': [
                      'b'
                    ]
                  }
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'not',
                'values': [
                  2
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'sum',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'not',
                'values': [
                  {
                    '$OBJECT': 'path',
                    'paths': [
                      't'
                    ]
                  }
                ]
              },
              {
                '$OBJECT': 'path',
                'paths': [
                  't'
                ]
              }
            ]
          }
        ]
    }]


def test_compiler_unary_complex_5():
    """
    Ensures that complex unary expressions are compiled correctly
    """
    source = ('a = ! (my_service command k1: !b) or '
              '!(my_service2 command k2: ! !c)')
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'not',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'p-1.1'
                ]
              }
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'not',
            'values': [
              {
                '$OBJECT': 'path',
                'paths': [
                  'p-1.2'
                ]
              }
            ]
          }
        ]
    }]
    assert result['tree']['1.1']['args'] == [{
        '$OBJECT': 'argument',
        'name': 'k1',
        'argument': {
          '$OBJECT': 'expression',
          'expression': 'not',
          'values': [
            {
              '$OBJECT': 'path',
              'paths': [
                'b'
              ]
            }
          ]
        }
    }]
    assert result['tree']['1.2']['args'] == [{
        '$OBJECT': 'argument',
        'name': 'k2',
        'argument': {
          '$OBJECT': 'expression',
          'expression': 'not',
          'values': [
            {
              '$OBJECT': 'expression',
              'expression': 'not',
              'values': [
                {
                  '$OBJECT': 'path',
                  'paths': [
                    'c'
                  ]
                }
              ]
            }
          ]
        }
    }]


def test_compiler_unary_complex_6():
    """
    Ensures that complex unary expressions are compiled correctly
    """
    source = 'a = !-2 or ! -3 - -4'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'not',
            'values': [
              -2
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'subtraction',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'not',
                'values': [
                  -3
                ]
              },
              -4
            ]
          }
        ]
    }]


def test_compiler_expression_is():
    """
    Ensures that 'is' expressions compile correctly
    """
    source = 'a = 1 == 2'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'equals',
        'values': [
          1,
          2
        ]
    }]


def test_compiler_expression_is_nested():
    """
    Ensures that nested 'is' expressions compile correctly
    """
    source = 'a = 1 + 2 == 3/4 == 5*6 == 7%8 or 9'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'equals',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  {
                    '$OBJECT': 'expression',
                    'expression': 'equals',
                    'values': [
                      {
                        '$OBJECT': 'expression',
                        'expression': 'sum',
                        'values': [
                          1,
                          2
                        ]
                      },
                      {
                        '$OBJECT': 'expression',
                        'expression': 'division',
                        'values': [
                          3,
                          4
                        ]
                      }
                    ]
                  },
                  {
                    '$OBJECT': 'expression',
                    'expression': 'multiplication',
                    'values': [
                      5,
                      6
                    ]
                  }
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'modulus',
                'values': [
                  7,
                  8
                ]
              }
            ]
          },
          9
        ]
    }]


def test_compiler_expression_is_nested_2():
    """
    Ensures that nested 'is' expressions compile correctly
    """
    source = 'a = 1 == 2 < 3 or 4 > 0.5+5 == -6 and 7 == 8'
    result = Api.loads(source)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{
        '$OBJECT': 'expression',
        'expression': 'or',
        'values': [
          {
            '$OBJECT': 'expression',
            'expression': 'less',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  1,
                  2
                ]
              },
              3
            ]
          },
          {
            '$OBJECT': 'expression',
            'expression': 'and',
            'values': [
              {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  {
                    '$OBJECT': 'expression',
                    'expression': 'greater',
                    'values': [
                      4,
                      {
                        '$OBJECT': 'expression',
                        'expression': 'sum',
                        'values': [
                          0.5,
                          5
                        ]
                      }
                    ]
                  },
                  -6
                ]
              },
              {
                '$OBJECT': 'expression',
                'expression': 'equals',
                'values': [
                  7,
                  8
                ]
              }
            ]
          }
        ]
    }]
