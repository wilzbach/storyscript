import re

from pytest import mark, raises

from storyscript.resolver import Resolver


def test_resolver_handside(mocker):
    mocker.patch.object(Resolver, 'object')
    result = Resolver.handside('item', 'data')
    Resolver.object.assert_called_with('item', 'data')
    assert result == Resolver.object()


def test_resolver_stringify():
    assert Resolver.stringify(1) == '1'


def test_resolver_stringify_string():
    assert Resolver.stringify('one') == '"""one"""'


def test_resolver_stringify_string_multiline():
    assert Resolver.stringify('one"') == '"""one\""""'


def test_resolver_values():
    values = [{'$OBJECT': 'path', 'paths': ['one']},
              {'$OBJECT': 'path', 'paths': ['two']}]
    assert Resolver.values(values) == ['one', 'two']


def test_resolver_values_with_data(mocker):
    mocker.patch.object(Resolver, 'object')
    result = Resolver.values(['one'], data='data')
    Resolver.object.assert_called_with('one', 'data')
    assert result == [Resolver.object()]


def test_resolver_string():
    assert Resolver.string('hello', {}) == 'hello'


def test_resolver_string_values(mocker):
    mocker.patch.object(Resolver, 'values', return_value=['one', 'two'])
    data = {'one': 'beautiful', 'two': 'world'}
    result = Resolver.string('hello {} {}', data, ['values'])
    Resolver.values.assert_called_with(['values'])
    assert result == 'hello beautiful world'


def test_resolver_string_empty_values(mocker):
    mocker.patch.object(Resolver, 'values', return_value=['one', 'two'])
    with raises(ValueError):
        Resolver.string('hello {} {}', {}, ['values'])


def test_resolver_path():
    path = ['a.b.c']
    data = {'a': {'b': {'c': 'value'}}}
    assert Resolver.path(path, data) == 'value'


def test_resolver_path_list():
    path = ['a.1.b']
    data = {'a': [0, {'b': 'value'}]}
    assert Resolver.path(path, data) == 'value'


def test_resolver_path_key_error():
    assert Resolver.path(['a.b'], {}) is None


def test_resolver_path_type_error():
    assert Resolver.path(['a.b.'], {'a': {'b': 'value'}}) is None


def test_resolver_dictionary(mocker):
    mocker.patch.object(Resolver, 'resolve')
    result = Resolver.dictionary({'key': 'value'}, 'data')
    Resolver.resolve.assert_called_with('value', 'data')
    assert result == {'key': Resolver.resolve()}


def test_resolver_dictionary_empty():
    assert Resolver.dictionary({}, 'data') == {}


@mark.parametrize('match, expectation', [
    (None, False),
    ('else', True)
])
def test_resolver_method_like(mocker, match, expectation):
    right = mocker.MagicMock(match=mocker.MagicMock(return_value=match))
    result = Resolver.method('like', 'left', right)
    right.match.assert_called_with('left')
    assert result is expectation


@mark.parametrize('match, expectation', [
    (None, True),
    ('else', False)
])
def test_resolver_method_notlike(mocker, match, expectation):
    right = mocker.MagicMock(match=mocker.MagicMock(return_value=match))
    result = Resolver.method('notlike', 'left', right)
    right.match.assert_called_with('left')
    assert result is expectation


def test_resolver_method_in():
    assert Resolver.method('in', 'left', ['left'])


@mark.parametrize('method', ['has', 'contains'])
def test_resolver_method_has(method):
    assert Resolver.method(method, ['left'], 'left')


def test_resolver_method_excludes():
    assert Resolver.method('in', 'left', ['right']) is False


def test_resolver_method_is():
    assert Resolver.method('is', 'left', 'left')


def test_resolver_method_isnt():
    assert Resolver.method('isnt', 'left', 'right')


def test_resolver_method_value_error():
    with raises(ValueError):
        Resolver.method('unknown', 'left', 'right')


def test_resolver_expression(mocker):
    mocker.patch.object(Resolver, 'values', return_value=[1])
    mocker.patch.object(Resolver, 'stringify', return_value='1')
    result = Resolver.expression('data', '{} == 1', 'values')
    Resolver.values.assert_called_with('values', data='data')
    Resolver.stringify.assert_called_with(1)
    assert result


def test_resolver_object_string(mocker):
    mocker.patch.object(Resolver, 'string')
    item = {'$OBJECT': 'string', 'string': 'message'}
    result = Resolver.object(item, 'data')
    Resolver.string.assert_called_with('message', 'data')
    assert result == Resolver.string()


def test_resolver_object_string_values(mocker):
    mocker.patch.object(Resolver, 'string')
    item = {'$OBJECT': 'string', 'string': 'message', 'values': 'values'}
    result = Resolver.object(item, 'data')
    Resolver.string.assert_called_with('message', 'data', values='values')
    assert result == Resolver.string()


def test_resolver_object_path(mocker):
    mocker.patch.object(Resolver, 'path')
    path = {'$OBJECT': 'path', 'paths': ['example']}
    result = Resolver.object(path, 'data')
    Resolver.path.assert_called_with(['example'], 'data')
    assert result == Resolver.path()


def test_resolver_object_regexp(mocker):
    mocker.patch.object(re, 'compile')
    expression = {'$OBJECT': 'regexp', 'regexp': 'regular'}
    Resolver.object(expression, 'data')
    re.compile.assert_called_with('regular')


def test_resolver_object_value():
    value = {'$OBJECT': 'value', 'value': 'x'}
    result = Resolver.object(value, 'data')
    assert result == 'x'


def test_resolver_object_dictionary(mocker):
    mocker.patch.object(Resolver, 'dictionary')
    result = Resolver.object({'$OBJECT': 'dictionary'}, 'data')
    Resolver.dictionary.assert_called_with({'$OBJECT': 'dictionary'}, 'data')
    assert result == Resolver.dictionary()


def test_resolver_object_method(mocker):
    mocker.patch.object(Resolver, 'method')
    mocker.patch.object(Resolver, 'handside', return_value='hand')
    item = {'$OBJECT': 'method', 'method': 'method', 'left': 'left',
            'right': 'right'}
    result = Resolver.object(item, 'data')
    Resolver.method.assert_called_with('method', 'hand', 'hand')
    assert result == Resolver.method()


def test_resolver_resolve_expression(mocker):
    mocker.patch.object(Resolver, 'expression')
    item = {'$OBJECT': 'expression', 'expression': '==', 'values': []}
    result = Resolver.resolve(item, 'data')
    Resolver.expression.assert_called_with('data', item['expression'],
                                           item['values'])
    assert result == Resolver.expression()


def test_resolver_list(mocker):
    mocker.patch.object(Resolver, 'resolve', return_value='done')
    result = Resolver.list(['items'], {})
    Resolver.resolve.assert_called_with('items', {})
    assert result == 'done'


def test_resolver_resolve(mocker):
    assert Resolver.resolve('whatever', 'data') == 'whatever'


def test_resolver_resolve_object(mocker):
    mocker.patch.object(Resolver, 'object')
    result = Resolver.resolve({}, 'data')
    Resolver.object.assert_called_with({}, 'data')
    assert result == Resolver.object()
