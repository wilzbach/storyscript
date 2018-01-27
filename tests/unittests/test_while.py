from json import dumps

import pytest

from tests.parse import parse


def test_while_container():
    """
    while http server as request
      exit
    """
    story = parse(
        test_while_container.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'while'
    assert story['script']['1']['container'] == 'http'
    assert story['script']['1']['output'] == {
        '$OBJECT': 'path',
        'paths': ['request']
    }
    assert story['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['server']},
    ]


def test_while_path():
    """
    while foo.bar
      exit
    """
    story = parse(
        test_while_path.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'while'
    assert story['script']['1']['container'] is None
    assert story['script']['1']['output'] is None
    assert story['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['foo', 'bar']},
    ]
