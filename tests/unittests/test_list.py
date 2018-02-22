import pytest

from tests.parse import parse


@pytest.mark.parametrize('script,items', [
    ('foo = [bar]', [{'$OBJECT': 'path', 'paths': ['bar']}]),
    ('foo = ["s", 1]', [
        {'$OBJECT': 'string', 'string': 's'},
        1,
    ]),
])
def test_list(script, items):
    story = parse(script).json()
    assert story['script']['1']['method'] == 'set'
    assert story['script']['1']['args'][0] == {
        '$OBJECT': 'path', 'paths': ['foo']
    }
    assert story['script']['1']['args'][1] == {
        '$OBJECT': 'list',
        'items': items
    }
