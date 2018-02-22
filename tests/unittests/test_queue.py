import pytest

from tests.parse import parse


@pytest.mark.parametrize('script,arg', [
    ('wait foobar\n\tdo this', {'$OBJECT': 'path', 'paths': ['foobar']}),
    ('wait "3 days"', {'$OBJECT': 'string', 'string': '3 days'}),
])
def test_in(script, arg):
    story = parse(script).json()
    assert story['script']['1']['method'] == 'wait'
    assert story['script']['1']['args'][0] == arg
    assert story['script']['1']['exit'] is None
    if 'do this' in script:
        assert story['script']['2']['method'] == 'run'
