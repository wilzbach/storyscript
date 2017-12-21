import pytest
import re

from storyscript import resolver


@pytest.mark.parametrize('path,data,result', [
    ('a.b.c', {'a': {'b': {'c': 1}}}, 1),
    ('a', {'a': {'b': {}}}, {'b': {}}),
    ('a.1.b', {'a': [1, {'b': 1}]}, 1)
])
def test_resolve_path(path, data, result):
    assert resolver.resolve_path(data, path) == result


def test_resolve_path_undefined():
    assert resolver.resolve_path({}, 'a.b') is None


@pytest.mark.parametrize('obj,data,result', [
    ({'path': 'a'}, {'a': 1}, 1),
    ({'value': 'a'}, None, 'a'),
    ({'value': 1}, None, 1),
    ({'regexp': 'abc'}, None, re.compile('abc')),
    ({'expression': '{} == 1', 'values': [{'path': 'a'}]}, {'a': 1}, True),
    ({'expression': '{} > {}', 'values': [{'path': 'a'}, {'value': 2}]},
     {'a': 1}, False),
    ({'method': 'is', 'left': {'value': 1}, 'right': {'path': 'a'}},
     {'a': 1}, 1),
])
def test_resolve_obj(obj, data, result):
    assert resolver.resolve_obj(data, obj) == result


@pytest.mark.parametrize('method,left,right,data,result', [
    ('like', {'value': 'abc'}, {'regexp': '^abc'}, None, True),
    ('has', {'path': 'a'}, {'value': 'b'}, {'a': {'b': 1}}, True),
    ('contains', {'path': 'a'}, {'value': 'b'}, {'a': {'b': 1}}, True),
    ('contains', {'path': 'a'}, {'value': 'c'}, {'a': {}}, False),
    ('has', {'path': 'a'}, {'value': 'b'}, {'a': ['b']}, True),
    ('contains', {'path': 'a'}, {'value': 'b'}, {'a': ['b']}, True),
    ('isnt', {'path': 'a'}, {'value': 1}, {'a': 1}, False),
    ('is', {'path': 'a'}, {'value': 1}, {'a': 1}, True),
])
def test_resolve_method(method, left, right, data, result):
    assert resolver.resolve_method(data, left, right, method) == result


def test_resolve_expression():
    # [TODO]
    pass


@pytest.mark.parametrize('lst,data,result', [
    ([{'path': 'a'}], {'a': 1}, [1]),
    ([{'path': 'a'}], {}, [None]),
    ([], None, []),
    ([{'path': 'abc'}, {'value': 1}],
     {'abc': 0, 'b': 1}, [0, 1]),
])
def test_resolve_list(lst, data, result):
    assert resolver.resolve_list(data, lst) == result


@pytest.mark.parametrize('dct,data,result', [
    ({'k': {'path': 'a'}}, {'a': 1}, {'k': 1}),
    ({'k': {'path': 'a'}}, {}, {'k': None}),
    ({}, None, {}),
    ({'a': {'path': 'abc'}, 'b': {'value': 1}},
     {'abc': 0, 'b': 1}, {'a': 0, 'b': 1}),
])
def test_resolve_dict(dct, data, result):
    assert resolver.resolve_dict(data, dct) == result


@pytest.mark.parametrize('value,result', [
    (1, '1'),
    ('a', '"""a"""'),
    ('a"', '"""a\""""'),
])
def test_stringify(value, result):
    assert resolver.stringify(value) == result
