from pytest import mark

from storyscript.tree import Method


def test_method_init(method):
    assert method.method == 'method'
    assert method.parser == 'parser'
    assert method.lineno == '1'
    assert method.suite is None
    assert method.output is None
    assert method.container is None
    assert method.args is None
    assert method.enter is None
    assert method.exit is None


@mark.parametrize('keyword_argument',
                  ['suite', 'output', 'container', 'args']
                  )
def test_method_init_kwargs(keyword_argument):
    kwargs = {keyword_argument: 'value'}
    method = Method('method', 'parser', 1, **kwargs)
    assert getattr(method, keyword_argument) == 'value'


@mark.parametrize('keyword_argument', ['enter', 'exit'])
def test_method_init_kwargs_stringified(keyword_argument):
    kwargs = {keyword_argument: 1}
    method = Method('method', 'parser', 1, **kwargs)
    assert getattr(method, keyword_argument) == '1'


@mark.parametrize('arg', [3, 3.4, True, False, None])
def test_method_args_json(arg, method):
    assert method.args_json(arg) == arg


def test_method_args_json_json(mocker, method):
    args = mocker.MagicMock(json=mocker.MagicMock())
    result = method.args_json(args)
    assert result == args.json()


def test_method_args_json_dict(method):
    args = {'one': 1, 'two': 2}
    assert method.args_json(args) == args


def test_method_args_json_dict_objects(mocker, method):
    item = mocker.MagicMock(json=mocker.MagicMock())
    assert method.args_json({'item': item}) == {'item': item.json()}


@mark.parametrize('arg', [['one'], ('one',)])
def test_method_args_json_others(method, arg):
    assert method.args_json(arg) == ['one']


def test_method_args_json_list_objects(mocker, method):
    item = mocker.MagicMock(json=mocker.MagicMock())
    assert method.args_json([item]) == [item.json()]


def test_method_json(mocker, method):
    mocker.patch.object(Method, 'args_json')
    result = method.json()
    method.args_json.assert_called_with(method.args)
    assert result == {
        'method': method.method,
        'ln': method.lineno,
        'output': method.output,
        'container': method.container,
        'args': method.args_json(),
        'enter': method.enter,
        'exit': method.exit
    }
