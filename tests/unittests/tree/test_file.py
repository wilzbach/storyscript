from pytest import fixture

from storyscript.tree import File, String


@fixture
def file():
    return File('path')


def test_file():
    assert issubclass(File, String)


def test_file_init(patch):
    patch.init(String)
    File('path')
    String.__init__.assert_called_with('path')


def test_file_init_chunks(patch):
    patch.init(String)
    file = File(['path'])
    assert file.chunks == ['path']


def test_file_json(patch, file):
    patch.object(String, 'json', return_value={'$OBJECT': 'string'})
    result = file.json()
    assert String.json.call_count == 1
    assert result == {'$OBJECT': 'file'}


def test_file_representation(file):
    assert '{}'.format(file) == "File(['path'])"
