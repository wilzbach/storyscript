from json import dumps

import pytest

import storyscript
from storyscript import exceptions


@pytest.mark.parametrize('script,args', [
    ('set x to a.b.c',
     ['x', {'$OBJECT': 'path', 'paths': ['a', 'b', 'c']}]),
    ('set c to 1', ['c', 1]),
    ('set c to true', ['c', True]),
    ('set c to false', ['c', False]),
    ('set c to false', ['c', False]),
    ('set c to apple.orange[1]',
     ['c', {'$OBJECT': 'path',
            'paths': ['apple', 'orange', '1']}]),
    ('set c to apple.orange[\'foobar\']',
     ['c', {'$OBJECT': 'path',
            'paths': ['apple', 'orange', 'foobar']}]),
    ('set c to apple.orange["foobar"]',
     ['c', {'$OBJECT': 'path',
            'paths': ['apple', 'orange', 'foobar']}]),
    ('set c to apple.orange[1..2]',
     ['c', {'$OBJECT': 'path',
            'paths': ['apple', 'orange', '1..2']}]),
    ('set x to y',
     ['x', {'$OBJECT': 'path', 'paths': ['y']}]),
    ('set x to y',
     ['x', {'$OBJECT': 'path', 'paths': ['y']}]),
    ('x = y',
     ['x', {'$OBJECT': 'path', 'paths': ['y']}]),
    ('x is y',
     ['x', {'$OBJECT': 'path', 'paths': ['y']}]),
    ('set x to y',
     ['x', {'$OBJECT': 'path', 'paths': ['y']}]),
])
def test_set(script, args):
    story = storyscript.parse(script).json()
    print(dumps(story['script']['1'], indent=2))
    assert story['script']['1']['args'] == args


@pytest.mark.parametrize('script,exception', [
    ("set x to 'a {{b '", SyntaxError),
    ("set x to 'a", SyntaxError),
    ('if "a < 10', SyntaxError),
    ('set x to "a {{b "', SyntaxError),
    ("set x to '''a''", SyntaxError),
    ("set x to '''a\n", SyntaxError),
    ("set x to '''{{black-n-white**'''", SyntaxError),
    ('set x to """a""', SyntaxError),
    ('if this; that', SyntaxError),
])
def test_errors(script, exception):
    with pytest.raises(exception):
        print(storyscript.parse(script).json())
