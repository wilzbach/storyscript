from pytest import fixture

from storyscript.tree import Method, Path


@fixture
def path():
    return Path('parser', 'line_number', 'path')


@fixture
def method():
    return Method('method', 'parser', 1)
