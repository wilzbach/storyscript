import pytest

from tests.parse import parse


def test_multi_stmt():
    """
    apples
    oranges
    """
    story = parse(
        test_multi_stmt.__doc__.strip().replace('\n    ', '\n')
    ).json()
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'apples'
    assert story['script']['2']['method'] == 'run'
    assert story['script']['2']['container'] == 'oranges'
