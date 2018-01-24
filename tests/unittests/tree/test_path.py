
def test_path_init(path):
    assert path.parser == 'parser'
    assert path.lineno == 'line_number'
    assert path.paths == 'path'


def test_path_split(path):
    assert path.split("a.b['c']") == ['a', 'b', 'c']


def test_path_json(path):
    assert path.json() == {'$OBJECT': 'path', 'paths': path.paths}
