import pytest

from tests.parse import parse


@pytest.mark.parametrize('script,args', [
    ('if x', [{'$OBJECT': 'path', 'paths': ['x']}]),
    ('if true', [True]),
    ('if false', [False]),
])
def test_bool(script, args):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == args


@pytest.mark.parametrize('script,method', [
    ('isnt', 'is not'),
    ('is not', 'is not'),
    ('not', 'is not'),
    ('is', 'is'),
    ('contains', 'contains'),
    ('in', 'in'),
    ('isnt in', 'not in'),
    ('is not in', 'not in'),
])
def test_in_contains(script, method):
    story = parse('x = y {} z'.format(script)).json()
    print (story['script']['1'])
    assert len(story['script']['1']['args']) == 2
    arg1 = story['script']['1']['args'][1]
    assert arg1['$OBJECT'] == 'method'
    assert arg1['left'] == {'$OBJECT': 'path', 'paths': ['y']}
    assert arg1['right'] == {'$OBJECT': 'path', 'paths': ['z']}
    assert arg1['method'] == method


@pytest.mark.parametrize('script,expression', [
    ('if 1=2', '1 == 2'),
    ('if 1 == 2', '1 == 2'),
    ('if 1 is equal to 2', '1 == 2'),
    ('if 1 equals 2', '1 == 2'),
])
def test_eq(script, expression):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': []
        }
    ]


@pytest.mark.parametrize('script,expression', [
    ('if 1!=2', '1 != 2'),
    ('if 1 != 2', '1 != 2'),
    ('if 1 is not equal to 2', '1 != 2'),
    ('if 1 not equal 2', '1 != 2'),
])
def test_neq(script, expression):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': []
        }
    ]


@pytest.mark.parametrize('script,method', [
    ('if abc like /apple/', 'like'),
    ('if abc is like /apple/', 'like'),
    ('if abc isnt like /apple/', 'not like'),
])
def test_regexp(script, method):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'method',
            'method': method,
            'left': {
                '$OBJECT': 'path',
                'paths': ['abc']
            },
            'right': {
                '$OBJECT': 'regexp',
                'regexp': 'apple'
            }
        }
    ]


@pytest.mark.parametrize('script,expression', [
    ('if x and y', '{} and {}'),
    ('if x or y', '{} or {}')
])
def test_and_or(script, expression):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': [
                {'$OBJECT': 'path', 'paths': ['x']},
                {'$OBJECT': 'path', 'paths': ['y']}
            ]
        }
    ]


@pytest.mark.parametrize('script,expression', [
    ('if (x and y) or z', '( {} and {} ) or {}'),
    ('if x or (y and z)', '{} or ( {} and {} )')
])
def test_group(script, expression):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': [
                {'$OBJECT': 'path', 'paths': ['x']},
                {'$OBJECT': 'path', 'paths': ['y']},
                {'$OBJECT': 'path', 'paths': ['z']}
            ]
        }
    ]


@pytest.mark.parametrize('script,expression', [
    ('if 1>2', '1 > 2'),
    ('if 1 > 2', '1 > 2'),
    ('if 1 >= 2', '1 >= 2'),
    ('if 1>=2', '1 >= 2'),
    ('if 1 is greater then 2', '1 > 2'),
    ('if 1 is greater than or equal to 2', '1 >= 2'),
])
def test_gt(script, expression):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': []
        }
    ]


@pytest.mark.parametrize('script,expression', [
    ('if 1<2', '1 < 2'),
    ('if 1 < 2', '1 < 2'),
    ('if 1<=2', '1 <= 2'),
    ('if 1 <= 2', '1 <= 2'),
    ('if 1 is less then 2', '1 < 2'),
    ('if 1 is lesser than or equal to 2', '1 <= 2'),
    ('if 1 less than or equal to 2', '1 <= 2'),
])
def test_lt(script, expression):
    story = parse(script + '\n\tpass').json()
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': []
        }
    ]
