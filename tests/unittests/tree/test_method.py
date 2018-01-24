from pytest import mark

from storyscript.tree import Method


def test_method_init():
    method = Method('method', 'parser', 1)
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
                  ['suite', 'output', 'container', 'args', 'enter', 'exit']
                  )
def test_method_init_kwargs(keyword_argument):
    kwargs = {keyword_argument: 'value'}
    method = Method('method', 'parser', 1, **kwargs)
    assert getattr(method, keyword_argument) == 'value'


def test_method_json(mocker):
    mocker.patch.object(Method, 'args_json')
    method = Method('method', 'parser', 1)
    assert method.json() == {
        'method': method.method,
        'ln': method.lineno,
        'output': method.output,
        'container': method.container,
        'args': method.args_json(),
        'enter': method.enter,
        'exit': method.exit
    }
