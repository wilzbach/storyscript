from pytest import fixture

from storyscript.tree import Path


@fixture
def path():
    return Path('parser', 'line_number', 'path')
