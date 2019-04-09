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
    args = [{'$OBJECT': 'int', 'int': 1},
            {'$OBJECT': 'mutation', 'mutation': 'increment', 'args': []},
            {'$OBJECT': 'mutation', 'mutation': 'format', 'args': [
                {'$OBJECT': 'arg', 'name': 'to',
                 'arg': {'$OBJECT': 'string', 'string': 'string'}}]}]
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


def int_(value):
    """
    Generate an int object
    """
    return {'$OBJECT': 'int', 'int': value}


@mark.parametrize('source_pair', [
    ('1+2', 'sum', [int_(1), int_(2)]),
    ('1+-2', 'sum', [int_(1), int_(-2)]),
    ('1-3', 'subtraction', [int_(1), int_(3)]),
    ('1--3', 'subtraction', [int_(1), int_(-3)]),
    ('0*2', 'multiplication', [int_(0), int_(2)]),
    ('0*-2', 'multiplication', [int_(0), int_(-2)]),
    ('1/6', 'division', [int_(1), int_(6)]),
    ('1/-6', 'division', [int_(1), int_(-6)]),
    ('0%2', 'modulus', [int_(0), int_(2)]),
    ('0%-2', 'modulus', [int_(0), int_(-2)]),
    ('1==2', 'equal', [int_(1), int_(2)]),
    ('1==-2', 'equal', [int_(1), int_(-2)]),
    ('1!=2', 'not_equal', [int_(1), int_(2)]),
    ('1!=-2', 'not_equal', [int_(1), int_(-2)]),
    ('1<2', 'less', [int_(1), int_(2)]),
    ('1<-2', 'less', [int_(1), int_(-2)]),
    ('1>2', 'greater', [int_(1), int_(2)]),
    ('1>-2', 'greater', [int_(1), int_(-2)]),
    ('1<=2', 'less_equal', [int_(1), int_(2)]),
    ('1<=-2', 'less_equal', [int_(1), int_(-2)]),
    ('1>=2', 'greater_equal', [int_(1), int_(2)]),
    ('-1>=2', 'greater_equal', [int_(-1), int_(2)]),
    ('1>=-2', 'greater_equal', [int_(1), int_(-2)]),
    ('b+c', 'sum', [path('b'), path('c')]),
    # Currently a valid entity
    # ('b-c', 'subtraction', [path('b'), path('c')]),
    ('b*c', 'multiplication', [path('b'), path('c')]),
    # Currently a valid entity
    # ('b/c', 'divison', [path('b'), path('c')]),
    ('b%c', 'modulus', [path('b'), path('c')]),
    ('b==c', 'equal', [path('b'), path('c')]),
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
    full_source = 'a=' + source
    index = '1'
    if source.startswith('b'):
        full_source = 'b=0\nc=0\n' + full_source
        index = '3'
    result = Api.loads(full_source)
    assert result['tree'][index]['method'] == 'expression'
    assert result['tree'][index]['name'] == ['a']
    assert len(result['tree'][index]['args']) == 1
    assert result['tree'][index]['args'][0]['$OBJECT'] == 'expression'
    assert result['tree'][index]['args'][0]['expression'] == expression
    assert result['tree'][index]['args'][0]['values'] == values
