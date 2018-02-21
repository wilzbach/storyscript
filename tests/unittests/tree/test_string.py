from pytest import fixture

from storyscript.tree import Path, String


@fixture
def string():
    return String('data')


def test_string_init(string):
    assert string.chunks == ['data']


def test_string_representation(string):
    assert '{}'.format(string) == "String(['data'])"


def test_string_add(string):
    string.add('bit')
    assert string.chunks[-1] == 'bit'


def test_string_complex(path, string):
    string.chunks = [path]
    assert string.complex()


def test_string_json(string):
    string.chunks = [' one', ' two ']
    result = string.json()
    assert result == {'$OBJECT': 'string', 'string': 'one two'}


def test_string_json_complex(mocker, path, string):
    mocker.patch.object(String, 'complex', return_value=True)
    mocker.patch.object(Path, 'json')
    string.chunks = [path, ' one ']
    result = string.json()
    assert String.complex.call_count == 1
    assert result == {'$OBJECT': 'string', 'string': '{} one',
                      'values': [path.json()]}
