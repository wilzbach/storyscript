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
    lines = {'1': {}, '2': {}, '21': {}, '3': {}}
    assert program.sorted_lines(lines) == ['1', '2', '3', '21']


def test_program_next_line(patch, program):
    patch.object(Program, 'sorted_lines', return_value=['1', '2'])
    lines = {'1': {'ln': '1'}, '2': {'ln': '2'}}
    result = program.next_line(lines, '1')
    Program.sorted_lines.assert_called_with(lines)
    assert result == lines['2']


def test_program_next_line_jump(patch, program):
    patch.object(Program, 'sorted_lines', return_value=['1', '3'])
    lines = {'1': {'ln': '1'}, '3': {'ln': '3'}}
    assert program.next_line(lines, '1') == lines['3']


def test_program_next_line_none(patch, program):
    patch.object(Program, 'sorted_lines', return_value=['1'])
    lines = {'1': {'ln': '1'}}
    assert program.next_line(lines, '1') is None


def test_program_last_line(patch, program):
    patch.object(Program, 'sorted_lines')
    result = program.last_line('lines')
    Program.sorted_lines.assert_called_with('lines')
    assert result == Program.sorted_lines()[-1]


def test_program_children(patch, program):
    patch.object(Program, 'parse_item')
    program.children({}, ['child'], parent=None)
    Program.parse_item.assert_called_with({}, 'child', parent=None)


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


def test_program_parse_suite(magic, program):
    item = magic(lineno='2', json=magic(return_value={}))
    result = program.parse_suite([item], '1')
    assert item.json.call_count == 1
    assert result == {'2': {'parent': '1'}}


def test_program_generate(patch, magic, program):
    line = magic(lineno='1')
    program.story = [line]
    patch.object(Program, 'nparse_item')
    result = program.generate()
    Program.nparse_item.assert_called_with(line)
    assert result == {'1': Program.nparse_item()}


def test_program_json(patch, program):
    patch.object(Program, 'generate')
    result = program.json()
    assert Program.generate.call_count == 1
    assert result == {'version': version, 'script': program.generate()}
