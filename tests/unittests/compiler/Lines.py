# -*- coding: utf-8 -*-
from pytest import fixture, mark, raises

from storyscript.compiler import Lines
from storyscript.exceptions import StorySyntaxError


@fixture
def lines():
    return Lines()


def test_lines_init(lines):
    assert lines.lines == {}
    assert lines.variables == []
    assert lines.services == []
    assert lines.functions == {}
    assert lines.output_scopes == {}
    assert lines.modules == {}


def test_lines_sort(lines):
    lines.lines = {'1': '1', '2': '2', '2.1': '2'}
    assert lines.sort() == ['1', '2', '2.1']


def test_lines_first(patch, lines):
    patch.object(Lines, 'sort')
    lines.lines = {'1': '1'}
    assert lines.last() == lines.sort()[0]


def test_lines_first_none(lines):
    assert lines.last() is None


def test_lines_last(patch, lines):
    patch.object(Lines, 'sort')
    lines.lines = {'1': '1'}
    assert lines.last() == lines.sort()[-1]


def test_lines_last_no_lines(lines):
    assert lines.last() is None


def test_lines_set_name(patch, lines):
    patch.object(Lines, 'last')
    lines.lines[lines.last()] = {}
    lines.set_name('name')
    assert lines.lines[lines.last()]['name'] == 'name'


def test_lines_set_next(patch, lines):
    patch.object(Lines, 'last', return_value='1')
    lines.lines['1'] = {}
    lines.set_next('2')
    assert lines.lines['1']['next'] == '2'


@mark.parametrize('method', ['if', 'elif', 'try', 'catch'])
def test_lines_set_exit(patch, lines, method):
    patch.object(Lines, 'sort', return_value=['1', '2'])
    lines.lines = {'1': {}, '2': {'method': method}}
    lines.set_exit('3')
    assert lines.sort.call_count == 1
    assert lines.lines['2']['exit'] == '3'


def test_lines_set_scope(lines):
    lines.set_scope('2', '1', 'output')
    assert lines.output_scopes['2'] == {'parent': '1', 'output': 'output'}


def test_lines_is_output(lines):
    lines.output_scopes = {'1': {'parent': None, 'output': ['service']}}
    assert lines.is_output('1', 'service') is True


def test_lines_is_output_from_parent(lines):
    lines.output_scopes = {
        '2': {'parent': '1', 'output': []},
        '1': {'output': ['service']}
    }
    assert lines.is_output('1', 'service') is True


def test_lines_is_output_false(lines):
    assert lines.is_output('1', 'service') is False


def test_lines_make(lines):
    expected = {'1': {'method': 'method', 'ln': '1', 'output': None,
                      'name': None,
                      'function': None, 'service': None, 'command': None,
                      'enter': None, 'exit': None, 'args': None,
                      'parent': None}}
    lines.make('method', '1')
    assert lines.lines == expected


@mark.parametrize('keywords', ['service', 'command', 'function', 'output',
                               'args', 'enter', 'exit', 'parent', 'name'])
def test_lines_make_keywords(lines, keywords):
    lines.make('method', '1', **{keywords: keywords})
    assert lines.lines['1'][keywords] == keywords


def test_lines_service_method(lines):
    assert lines.service_method('alpine', '1') == 'execute'


def test_lines_service_method_call(lines):
    lines.functions['makeTea'] = '1'
    assert lines.service_method('makeTea', '1') == 'call'


def test_lines_service_method_call_from_module(lines):
    lines.modules['afternoon'] = 'afternoon.story'
    assert lines.service_method('afternoon.makeTea', '1') == 'call'


def test_lines_service_method_error(patch, lines):
    patch.init(StorySyntaxError)
    with raises(StorySyntaxError):
        lines.service_method('wrong.name', '1')
    StorySyntaxError.__init__.assert_called_with('service_name')


def test_lines_append(patch, lines):
    patch.many(Lines, ['make', 'set_next'])
    lines.append('method', 'line', extras='whatever')
    lines.set_next.assert_called_with('line')
    lines.make.assert_called_with('method', 'line', extras='whatever')


def test_lines_append_function(patch, lines):
    """
    Ensures that a function is registered properly.
    """
    patch.many(Lines, ['make', 'set_next'])
    lines.append('function', 'line', function='function')
    assert lines.functions['function'] == 'line'


def test_lines_append_set(patch, lines):
    """
    Ensures that a variable is registered properly
    """
    patch.many(Lines, ['make', 'set_next'])
    lines.append('set', 'line', name=['name'])
    assert lines.variables[-1] == ['name']


def test_compiler_append_service(patch, lines):
    """
    Ensures that a service is registed in Compiler.services
    """
    patch.many(Lines, ['make', 'set_next', 'is_output', 'service_method'])
    Lines.service_method.return_value = 'execute'
    Lines.is_output.return_value = False
    lines.append('execute', 'line', service='service', parent='parent')
    Lines.service_method.assert_called_with('service', 'line')
    lines.is_output.assert_called_with('parent', 'service')
    assert lines.services[0] == 'service'


def test_lines_append_service_block_output(patch, lines):
    """
    Ensures that a service is not registered if the current service block
    has defined it as output
    """
    patch.many(Lines, ['make', 'set_next', 'is_output', 'service_method'])
    Lines.service_method.return_value = 'execute'
    lines.outputs = {'line': ['service']}
    lines.append('execute', 'line', service='service', parent='parent')
    assert lines.services == []


def test_lines_append_function_call(patch, lines):
    """
    Ensures that a function call is registered properly.
    """
    patch.many(Lines, ['make', 'set_next', 'service_method'])
    Lines.service_method.return_value = 'call'
    lines.functions['function'] = 1
    lines.append('execute', 'line', service='function')
    lines.make.assert_called_with('call', 'line', service='function')


def test_lines_execute(patch, lines):
    patch.object(Lines, 'append')
    lines.execute('line', 'service', 'command', 'args', 'output', 'enter',
                  'parent')
    kwargs = {'service': 'service', 'command': 'command', 'args': 'args',
              'output': 'output', 'enter': 'enter', 'parent': 'parent'}
    Lines.append.assert_called_with('execute', 'line', **kwargs)


def test_compiler_get_services(lines):
    lines.services = ['one', 'one']
    assert lines.get_services() == ['one']
