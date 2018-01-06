import re

import pytest

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
    ({'$OBJECT': 'path', 'path': 'a'}, {'a': 1}, 1),
    ({'$OBJECT': 'value', 'value': 'a'}, None, 'a'),
    ({'$OBJECT': 'value', 'value': 1}, None, 1),
    ({'$OBJECT': 'expression',
      'expression': '{} == 1',
      'values': [{'$OBJECT': 'path', 'path': 'a'}]}, {'a': 1}, True),
    ({'$OBJECT': 'expression',
      'expression': '{} > {}',
      'values': [{'$OBJECT': 'path', 'path': 'a'},
                 {'$OBJECT': 'value', 'value': 2}]},
     {'a': 1}, False),
    ({'$OBJECT': 'method',
      'method': 'is',
      'left': {'$OBJECT': 'value', 'value': 1},
      'right': {'$OBJECT': 'path', 'path': 'a'}},
     {'a': 1}, 1),
    (1, None, 1),
    (None, None, None),
    ('string', None, 'string'),
    ({'a': 'b'}, None, {'a': 'b'})
])
def test_resolve_obj(obj, data, result):
    assert resolver.resolve_obj(data, obj) == result


def test_resolve_obj_regexp():
    assert resolver.resolve_obj(
        None,
        {'$OBJECT': 'regexp', 'regexp': 'abc'}
    ).pattern == 'abc'


@pytest.mark.parametrize('method,left,right,data,result', [
    ('like', {'$OBJECT': 'value', 'value': 'abc'},
     {'$OBJECT': 'regexp', 'regexp': '^abc'}, None, True),
    ('has', {'$OBJECT': 'path', 'path': 'a'},
     {'$OBJECT': 'value', 'value': 'b'}, {'a': {'b': 1}}, True),
    ('contains', {'$OBJECT': 'path', 'path': 'a'},
     {'$OBJECT': 'value', 'value': 'b'}, {'a': {'b': 1}}, True),
    ('contains', {'$OBJECT': 'path', 'path': 'a'},
     {'$OBJECT': 'value', 'value': 'c'}, {'a': {}}, False),
    ('has', {'$OBJECT': 'path', 'path': 'a'},
     {'$OBJECT': 'value', 'value': 'b'}, {'a': ['b']}, True),
    ('in', {'$OBJECT': 'value', 'value': 'b'},
     {'$OBJECT': 'path', 'path': 'a'}, {'a': ['b']}, True),
    ('excludes', {'$OBJECT': 'value', 'value': 1},
     {'$OBJECT': 'path', 'path': 'a'}, {'a': [0]}, True),
    ('contains', {'$OBJECT': 'path', 'path': 'a'},
     {'$OBJECT': 'value', 'value': 'b'}, {'a': ['b']}, True),
    ('isnt', {'$OBJECT': 'path', 'path': 'a'},
     {'$OBJECT': 'value', 'value': 1}, {'a': 1}, False),
    ('is', {'$OBJECT': 'path', 'path': 'a'},
     {'$OBJECT': 'value', 'value': 1}, {'a': 1}, True),
])
def test_resolve_method(method, left, right, data, result):
    assert resolver.resolve_method(data, left, right, method) == result


def test_resolve_expression():
    # [TODO]
    pass


@pytest.mark.parametrize('lst,data,result', [
    ([{'$OBJECT': 'path', 'path': 'a'}], {'a': 1}, [1]),
    ([{'$OBJECT': 'path', 'path': 'a'}], {}, [None]),
    ([], None, []),
    ([{'$OBJECT': 'path', 'path': 'abc'},
      {'$OBJECT': 'value', 'value': 1}],
     {'abc': 0, 'b': 1}, [0, 1]),
])
def test_resolve_list(lst, data, result):
    assert resolver.resolve_list(data, lst) == result


@pytest.mark.parametrize('dct,data,result', [
    ({'k': {'$OBJECT': 'path', 'path': 'a'}}, {'a': 1}, {'k': 1}),
    ({'k': {'$OBJECT': 'path', 'path': 'a'}}, {}, {'k': None}),
    ({}, None, {}),
    ({'a': {'$OBJECT': 'path', 'path': 'abc'},
      'b': {'$OBJECT': 'value', 'value': 1}},
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
