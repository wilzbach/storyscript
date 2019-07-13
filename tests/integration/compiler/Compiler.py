# -*- coding: utf-8 -*-
from pytest import mark

from storyscript.Api import Api


@mark.parametrize('source', [
    'a = "foo bar"\na.split(by: " ").contains(item: "foo")'
])
def test_compiler_mutation_chained(source):
    """
    Ensures that chained mutations are compiled correctly
    """
    result = Api.loads(source).result()
    args1 = [{'$OBJECT': 'string', 'string': 'foo bar'}]
    args2_1 = [{'$OBJECT': 'path', 'paths': ['a']},
               {'$OBJECT': 'mutation', 'mutation': 'split', 'args': [
                   {'$OBJECT': 'arg', 'name': 'by',
                    'arg': {'$OBJECT': 'string', 'string': ' '}}]}]
    args2_2 = [{'$OBJECT': 'path', 'paths': ['__p-2.1']},
               {'$OBJECT': 'mutation', 'mutation': 'contains', 'args': [
                   {'$OBJECT': 'arg', 'name': 'item',
                    'arg': {'$OBJECT': 'string', 'string': 'foo'}}]}]
    args2 = [{'$OBJECT': 'path', 'paths': ['__p-2.2']}]

    assert result['tree']['1']['args'] == args1
    assert result['tree']['2.1']['args'] == args2_1
    assert result['tree']['2.2']['args'] == args2_2
    assert result['tree']['2']['args'] == args2


def test_compiler_empty_files():
    result = Api.loads('\n\n').result()
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
    ('1!=2', 'not.equal', [int_(1), int_(2)]),
    ('1!=-2', 'not.equal', [int_(1), int_(-2)]),
    ('1<2', 'less', [int_(1), int_(2)]),
    ('1<-2', 'less', [int_(1), int_(-2)]),
    ('1>2', 'not.less_equal', [int_(1), int_(2)]),
    ('1>-2', 'not.less_equal', [int_(1), int_(-2)]),
    ('1<=2', 'less_equal', [int_(1), int_(2)]),
    ('1<=-2', 'less_equal', [int_(1), int_(-2)]),
    ('1>=2', 'not.less', [int_(1), int_(2)]),
    ('-1>=2', 'not.less', [int_(-1), int_(2)]),
    ('1>=-2', 'not.less', [int_(1), int_(-2)]),
    ('b+c', 'sum', [path('b'), path('c')]),
    # Currently a valid entity
    # ('b-c', 'subtraction', [path('b'), path('c')]),
    ('b*c', 'multiplication', [path('b'), path('c')]),
    # Currently a valid entity
    # ('b/c', 'divison', [path('b'), path('c')]),
    ('b%c', 'modulus', [path('b'), path('c')]),
    ('b==c', 'equal', [path('b'), path('c')]),
    ('b!=c', 'not.equal', [path('b'), path('c')]),
    ('b<c', 'less', [path('b'), path('c')]),
    ('b>c', 'not.less_equal', [path('b'), path('c')]),
    ('b<=c', 'less_equal', [path('b'), path('c')]),
    ('b>=c', 'not.less', [path('b'), path('c')]),
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
    result = Api.loads(full_source).result()
    assert result['tree'][index]['method'] == 'expression'
    assert result['tree'][index]['name'] == ['a']
    assert len(result['tree'][index]['args']) == 1
    assert result['tree'][index]['args'][0]['$OBJECT'] == 'expression'
    expression = expression.split('.')
    assert result['tree'][index]['args'][0]['expression'] == expression[0]
    if len(expression) == 1:
        assert result['tree'][index]['args'][0]['values'] == values
    else:
        # not rewrites
        args = result['tree'][index]['args'][0]['values'][0]
        assert args['expression'] == expression[1]
        assert args['values'] == values
