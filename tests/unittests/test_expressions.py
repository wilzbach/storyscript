from json import dumps

import pytest

import storyscript


@pytest.mark.parametrize('script,args', [
    ('if x\n\tpass', [{'$OBJECT': 'path', 'paths': ['x']}]),
    ('if true\n\tpass', [True]),
    ('if false\n\tpass', [False]),
])
def test_bool(script, args):
    story = storyscript.parse(script).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['args'] == args


@pytest.mark.parametrize('script,expression', [
    ('if 1=2\n\tpass', '1 == 2'),
    ('if 1 == 2\n\tpass', '1 == 2'),
    ('if 1 is equal to 2\n\tpass', '1 == 2'),
    ('if 1 equals 2\n\tpass', '1 == 2'),
])
def test_eq(script, expression):
    story = storyscript.parse(script).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': []
        }
    ]


                'regexp': 'apple'
@pytest.mark.parametrize('script,expression', [
    ('if x and y\n\tpass', '{} and {}'),
    ('if x or y\n\tpass', '{} or {}')
])
def test_and_or(script, expression):
    story = storyscript.parse(script).json()
    print(dumps(story['script'], indent=2))
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
    ('if (x and y) or z\n\tpass', '( {} and {} ) or {}'),
    ('if x or (y and z)\n\tpass', '{} or ( {} and {} )')
])
def test_group(script, expression):
    story = storyscript.parse(script).json()
    print(dumps(story['script'], indent=2))
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
    ('if 1>2\n\tpass', '1 > 2'),
    ('if 1 > 2\n\tpass', '1 > 2'),
    ('if 1 is greater then 2\n\tpass', '1 > 2'),
    ('if 1 is greater than or equal to 2\n\tpass', '1 >= 2'),
    ('if 1>=2\n\tpass', '1 >= 2'),
    ('if 1 >= 2\n\tpass', '1 >= 2'),
    ('if 1<2\n\tpass', '1 < 2'),
    ('if 1 < 2\n\tpass', '1 < 2'),
    ('if 1 is less than 2\n\tpass', '1 < 2'),
    ('if 1 is less then 2\n\tpass', '1 < 2'),
    ('if 1 less than or equal to 2\n\tpass', '1 <= 2'),

])
def test_gtlt(script, expression):
    story = storyscript.parse(script).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['args'] == [
        {
            '$OBJECT': 'expression',
            'expression': expression,
            'values': []
        }
    ]
