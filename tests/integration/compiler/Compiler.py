# -*- coding: utf-8 -*-
from pytest import mark

from storyscript.Api import Api


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


def test_compiler_empty_files():
    result = Api.loads('\n\n')
    assert result['tree'] == {}
    assert result['entrypoint'] is None


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
