from pytest import fixture

from storyscript.tree import Method, Program
from storyscript.version import version


@fixture
def parser(magic):
    return magic()


@fixture
def program(parser):
    return Program(parser, 'story')


def test_program_init(parser, program):
    assert program.parser == parser
    assert program.parser.program == program
    assert program.story == 'story'


def test_program_representation(parser, program):
    assert '{}'.format(program) == 'Program({}, story)'.format(parser)


def test_program_sorted_lines(program):
    lines= {'1': {}, '2': {}, '21': {}, '3': {}}
    assert program.sorted_lines(lines) == ['1', '2', '3', '21']


def test_program_parse_item(patch, method, program):
    patch.object(Method, 'json')
    result = {}
    program.parse_item(result, method)
    assert result[method.lineno] == method.json()


def test_program_parse_item_recursion(patch, method, program):
    patch.object(Method, 'json')
    result = {}
    program.parse_item(result, [[method]])
    assert result[method.lineno] == method.json()


def test_program_parse_item_parent(patch, magic, method, program):
    patch.object(Method, 'json', return_value={})
    result = {}
    program.parse_item(result, method, parent=magic(lineno='100'))
    assert result[method.lineno]['parent'] == '100'


def test_program_parse_item_suite(patch, method, program):
    patch.object(Method, 'json')
    child = Method('method', 'parser', 2)
    method.suite = [child]
    result = {}
    program.parse_item(result, method)
    assert result['2'] == child.json()


def test_program_json(patch, program):
    patch.object(Program, 'parse_item')
    result = program.json()
    Program.parse_item.assert_called_with({}, program.story)
    assert result == {'version': version, 'script': {}}
