from pytest import fixture

from storyscript.tree import String


@fixture
def string():
    return String('data')


def test_string_init(string):
    assert string.chunks == ['data']


def test_string_add(string):
    string.add('bit')
    assert string.chunks[-1] == 'bit'


def test_string_json(string):
    string.chunks = [' one', ' two ']
    result = string.json()
    assert result == {'$OBJECT': 'string', 'string': 'one two'}
