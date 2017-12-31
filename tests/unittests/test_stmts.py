from json import dumps

import pytest

import storyscript


def test_multi_stmt():
    """
    apples
    oranges
    """
    story = storyscript.parse(
        test_multi_stmt.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'apples'
    assert story['script']['2']['method'] == 'run'
    assert story['script']['2']['container'] == 'oranges'


@pytest.mark.parametrize('script,method,args', [
    ('unset arg1.arg2', 'unset', ['arg1', 'arg2']),
    ('append 1 to arg1', 'append',
     [1, {'$OBJECT': 'path', 'paths': ['arg1']}]),
    ('append 1 into arg1', 'append',
     [1, {'$OBJECT': 'path', 'paths': ['arg1']}]),

])
def test_methods(script, method, args):
    story = storyscript.parse(script).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == method
    assert story['script']['1']['args'] == args
