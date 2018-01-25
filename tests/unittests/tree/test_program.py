from pytest import fixture

from storyscript.tree import Method, Program
from storyscript.version import version


@fixture
def parser(mocker):
    return mocker.MagicMock()


@fixture
def program(parser):
    return Program(parser, 'story')


def test_program_init(parser, program):
    assert program.parser == parser
    assert program.parser.program == program
    assert program.story == 'story'


def test_program_parse_item(mocker, method, program):
    mocker.patch.object(Method, 'json')
    result = {}
    program.parse_item(result, method)
    assert result[method.lineno] == method.json()


def test_program_parse_item_recursion(mocker, method, program):
    mocker.patch.object(Method, 'json')
    result = {}
    program.parse_item(result, [[method]])
    assert result[method.lineno] == method.json()


def test_program_parse_item_parent(mocker, method, program):
    mocker.patch.object(Method, 'json', return_value={})
    result = {}
    program.parse_item(result, method, parent=mocker.MagicMock(lineno='100'))
    assert result[method.lineno]['parent'] == '100'


def test_program_parse_item_suite(mocker, method, program):
    mocker.patch.object(Method, 'json')
    child = Method('method', 'parser', 2)
    method.suite = [child]
    result = {}
    program.parse_item(result, method)
    assert result['2'] == child.json()


def test_program_json(mocker, program):
    mocker.patch.object(Program, 'parse_item')
    result = program.json()
    Program.parse_item.assert_called_with({}, program.story)
    assert result == {'version': version, 'script': {}}
