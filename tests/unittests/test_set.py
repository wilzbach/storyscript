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
    assert story['script']['1']['args'] == args


@pytest.mark.parametrize('script,args', [
    ('x = owner/repo arg --flag foobar -n1',
     [{'$OBJECT': 'path', 'paths': ['arg']},
      '--flag',
      {'$OBJECT': 'path', 'paths': ['foobar']},
      '-n',
      1]),
    ('x = owner/repo run -s=0 --long=1',
     [{'$OBJECT': 'path', 'paths': ['run']}, '-s', 0, '--long', 1]),
    ('x = owner/repo run -s=0\n   --long=1',
     [{'$OBJECT': 'path', 'paths': ['run']}, '-s', 0, '--long', 1]),
])
def test_set_container(script, args):
    story = parse(script).json()
    assert story['script']['1']['output']['paths'] == ['x']
    assert story['script']['1']['args'] == args


@pytest.mark.parametrize('script,args', [
    ('x = foo if bar',
     {'$OBJECT': 'condition',
      'condition': {'$OBJECT': 'path', 'paths': ['bar']},
      'is': True,
      'then': {'$OBJECT': 'path', 'paths': ['foo']},
      'else': None}),
    ('x = foo unless bar',
     {'$OBJECT': 'condition',
      'condition': {'$OBJECT': 'path', 'paths': ['bar']},
      'is': False,
      'then': {'$OBJECT': 'path', 'paths': ['foo']},
      'else': None}),
    ('x = if foo then bar',
     {'$OBJECT': 'condition',
      'condition': {'$OBJECT': 'path', 'paths': ['foo']},
      'is': True,
      'then': {'$OBJECT': 'path', 'paths': ['bar']},
      'else': None}),
    ('x = if foo then bar else idk',
     {'$OBJECT': 'condition',
      'condition': {'$OBJECT': 'path', 'paths': ['foo']},
      'is': True,
      'then': {'$OBJECT': 'path', 'paths': ['bar']},
      'else': {'$OBJECT': 'path', 'paths': ['idk']}}),
    ('x = unless foo then bar else idk',
     {'$OBJECT': 'condition',
      'condition': {'$OBJECT': 'path', 'paths': ['foo']},
      'is': False,
      'then': {'$OBJECT': 'path', 'paths': ['bar']},
      'else': {'$OBJECT': 'path', 'paths': ['idk']}}),
    ('x = unless foo then bar',
     {'$OBJECT': 'condition',
      'condition': {'$OBJECT': 'path', 'paths': ['foo']},
      'is': False,
      'then': {'$OBJECT': 'path', 'paths': ['bar']},
      'else': None}),
])
def test_set_condition(script, args):
    story = parse(script).json()
    assert story['script']['1']['args'][1] == args


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
        parse(script).json()
