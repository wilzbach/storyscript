from storyscript.tree import Path


def test_path_init(mocker):
    mocker.patch.object(Path, 'split')
    path = Path('parser', 'line_number', 'path')
    Path.split.assert_called_with('path')
    assert path.parser == 'parser'
    assert path.lineno == 'line_number'
    assert path.paths == Path.split()


def test_path_split(path):
    assert path.split("a.b['c']") == ['a', 'b', 'c']


def test_path_json(path):
    assert path.json() == {'$OBJECT': 'path', 'paths': path.paths}
