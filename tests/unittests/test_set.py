from json import dumps

import pytest

from storyscript import exceptions

from tests.parse import parse


@pytest.mark.parametrize('script,args', [
    ('set x to a.b.c',
     [{'$OBJECT': 'path', 'paths': ['x']},
      {'$OBJECT': 'path', 'paths': ['a', 'b', 'c']}]),
    ('set c to 1', [{'$OBJECT': 'path', 'paths': ['c']}, 1]),
    ('set c to true', [{'$OBJECT': 'path', 'paths': ['c']}, True]),
    ('set c to false', [{'$OBJECT': 'path', 'paths': ['c']}, False]),
    ('set c to false', [{'$OBJECT': 'path', 'paths': ['c']}, False]),
    ('set c to apple.orange[1]',
     [{'$OBJECT': 'path', 'paths': ['c']},
      {'$OBJECT': 'path', 'paths': ['apple', 'orange', '1']}]),
    ('set c to apple.orange[\'foobar\']',
     [{'$OBJECT': 'path', 'paths': ['c']},
      {'$OBJECT': 'path', 'paths': ['apple', 'orange', 'foobar']}]),
    ('set c to apple.orange["foobar"]',
     [{'$OBJECT': 'path', 'paths': ['c']},
      {'$OBJECT': 'path', 'paths': ['apple', 'orange', 'foobar']}]),
    ('set c to apple.orange[1..2]',
     [{'$OBJECT': 'path', 'paths': ['c']},
      {'$OBJECT': 'path', 'paths': ['apple', 'orange', '1..2']}]),
    ('set x to y',
     [{'$OBJECT': 'path', 'paths': ['x']},
      {'$OBJECT': 'path', 'paths': ['y']}]),
    ('set x to y',
     [{'$OBJECT': 'path', 'paths': ['x']},
      {'$OBJECT': 'path', 'paths': ['y']}]),
    ('x = y',
     [{'$OBJECT': 'path', 'paths': ['x']},
      {'$OBJECT': 'path', 'paths': ['y']}]),
    ('x is y',
     [{'$OBJECT': 'path', 'paths': ['x']},
      {'$OBJECT': 'path', 'paths': ['y']}]),
    ('set x to y',
     [{'$OBJECT': 'path', 'paths': ['x']},
      {'$OBJECT': 'path', 'paths': ['y']}]),
])
def test_set(script, args):
    story = parse(script).json()
    print(dumps(story['script'], indent=2))
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
        print(parse(script).json())
