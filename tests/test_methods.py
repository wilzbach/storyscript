import pytest
from json import dumps
from ddt import ddt, data

import storyscript
from storyscript import exceptions


@pytest.mark.parametrize('script,result', [
    ('set x to a.b.c',
     {'args': ['x', {'$OBJECT': 'path', 'path': 'a.b.c'}]}),
    ('set c to 1',
     {'args': ['c', 1]}),
    ('set c to true',
     {'args': ['c', True]}),
    ('set c to false',
     {'args': ['c', False]}),
    ('set c to false',
     {'args': ['c', False]}),
    ('set c to apple.orange[1]',
     {'args': ['c', {'$OBJECT': 'path', 'path': 'apple.orange[1]'}]}),
    ('set c to apple.orange[\'foobar\']',
     {'args': ['c', {'$OBJECT': 'path', 'path': 'apple.orange.foobar'}]}),
    ('set c to apple.orange["foobar"]',
     {'args': ['c', {'$OBJECT': 'path', 'path': 'apple.orange.foobar'}]}),
    ('set c to apple.orange[1..2]',
     {'args': ['c', {'$OBJECT': 'path', 'path': 'apple.orange[1..2]'}]}),
    ('set x to y',
     {'args': ['x', {'$OBJECT': 'path', 'path': 'y'}]}),
    ('set x to y',
     {'args': ['x', {'$OBJECT': 'path', 'path': 'y'}]}),
    ('x = y',
     {'args': ['x', {'$OBJECT': 'path', 'path': 'y'}]}),
    ('x is y',
     {'args': ['x', {'$OBJECT': 'path', 'path': 'y'}]}),
    ('set x to y',
     {'args': ['x', {'$OBJECT': 'path', 'path': 'y'}]}),
])
def test_set(script, result):
    story = storyscript.parse(script).json()
    print(dumps(story['script']['1'], indent=2))
    obj = {
        'output': None,
        'method': 'set',
        'parent': None,
        'kwargs': None,
        'linenum': '1'
    }
    obj.update(result)
    assert story['script']['1'] == obj


@pytest.mark.parametrize('script,exception', [
    ("set x to 'a {{b '", SyntaxError),
    ("set x to 'a", SyntaxError),
    ("if \"a < 10", SyntaxError),
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
