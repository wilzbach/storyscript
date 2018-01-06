from json import dumps

import pytest

from tests.parse import parse


def test_try():
    """
    try
      pass
    """
    story = parse(
        test_try.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'try'
    assert story['script']['1']['enter'] == '2'
    assert story['script']['1']['exit'] is None


def test_try_catch():
    """
    try
      pass
    catch
      pass
    """
    story = parse(
        test_try_catch.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'try'
    assert story['script']['1']['enter'] == '2'
    assert story['script']['1']['exit'] == '4'
    assert story['script']['3']['method'] == 'catch'
