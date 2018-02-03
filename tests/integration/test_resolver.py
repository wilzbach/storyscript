import re

import pytest

from storyscript.resolver import Resolver


@pytest.mark.parametrize('path,data,result', [
    (['a.b.c'], {'a': {'b': {'c': 1}}}, 1),
    (['a'], {'a': {'b': {}}}, {'b': {}}),
    (['a.1.b'], {'a': [1, {'b': 1}]}, 1)
])
def test_resolve_path(path, data, result):
    assert Resolver.path(path, data) == result


def test_resolve_path_undefined():
    assert Resolver.path('a.b', {}) is None


@pytest.mark.parametrize('obj,data,result', [
    ({'$OBJECT': 'path', 'paths': ['a']}, {'a': 1}, 1),
    ({'$OBJECT': 'value', 'value': 'a'}, None, 'a'),
    ({'$OBJECT': 'value', 'value': 1}, None, 1),
    ({'$OBJECT': 'expression',
      'expression': '{} == 1',
      'values': [{'$OBJECT': 'path', 'paths': ['a']}]}, {'a': 1}, True),
    ({'$OBJECT': 'expression',
      'expression': '{} > {}',
      'values': [{'$OBJECT': 'path', 'paths': ['a']},
                 {'$OBJECT': 'value', 'value': 2}]},
     {'a': 1}, False),
    ({'$OBJECT': 'method',
      'method': 'is',
      'left': {'$OBJECT': 'value', 'value': 1},
      'right': {'$OBJECT': 'path', 'paths': ['a']}},
     {'a': 1}, 1),
    (1, None, 1),
    (None, None, None),
    ('string', None, 'string'),
    ({'a': 'b'}, None, {'a': 'b'})
])
def test_resolve_resolve(obj, data, result):
    assert Resolver.resolve(obj, data) == result


def test_resolve_obj_regexp():
    result = Resolver.object({'$OBJECT': 'regexp', 'regexp': 'abc'}, None)
    assert result.pattern == 'abc'


@pytest.mark.parametrize('method, left, right, result', [
    ('like', 'abc', re.compile('^abc'), True),
    ('has', {'b': 1}, 'b', True),
    ('contains', {'b': 1}, 'b', True),
    ('contains', {}, 'c', False),
    ('has', ['b'], 'b', True),
    ('in', 'b', ['b'], True),
    ('excludes', 1, [0], True),
    ('contains', ['b'], 'b', True),
    ('isnt', 1, 1, False),
    ('is', 1, 1, True),
])
def test_resolve_method(method, left, right, result):
    assert Resolver.method(method, left, right) == result


@pytest.mark.parametrize('items_list, data, result', [
    ([{'$OBJECT': 'path', 'paths': ['a']}], {'a': 1}, [1]),
    ([{'$OBJECT': 'path', 'paths': ['a']}], {}, [None]),
    ([], None, []),
    ([{'$OBJECT': 'path', 'paths': ['abc']},
      {'$OBJECT': 'value', 'value': 1}],
     {'abc': 0, 'b': 1}, [0, 1]),
])
def test_resolve_list(items_list, data, result):
    assert Resolver.values(items_list, data=data) == result


@pytest.mark.parametrize('dictionary, data, result', [
    ({'k': {'$OBJECT': 'path', 'paths': ['a']}}, {'a': 1}, {'k': 1}),
    ({'k': {'$OBJECT': 'path', 'paths': ['a']}}, {}, {'k': None}),
    ({}, None, {}),
    ({'a': {'$OBJECT': 'path', 'paths': ['abc']},
      'b': {'$OBJECT': 'value', 'value': 1}},
     {'abc': 0, 'b': 1}, {'a': 0, 'b': 1}),
])
def test_resolve_dict(dictionary, data, result):
    assert Resolver.dictionary(dictionary, data) == result


@pytest.mark.parametrize('value,result', [
    (1, '1'),
    ('a', '"""a"""'),
    ('a"', '"""a\""""'),
])
def test_stringify(value, result):
    assert Resolver.stringify(value) == result
