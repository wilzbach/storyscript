import pytest

from tests.parse import parse


def test_file_simple():
    story = parse(
        'container arg1 `path/to/here.ext`'
    ).json()
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'container'
    assert story['script']['1']['args'][1] == {
        '$OBJECT': 'string',
        'type': 'file',
        'string': 'path/to/here.ext'
    }
