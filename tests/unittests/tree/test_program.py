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
    assert program.lines == {}


def test_program_representation(parser, program):
    assert '{}'.format(program) == 'Program({}, story)'.format(parser)


def test_program_sorted_lines():
    lines = {'1': {}, '2': {}, '21': {}, '3': {}}
    assert Program.sorted_lines(lines) == ['1', '2', '3', '21']


def test_program_last_line(patch, program):
    patch.object(Program, 'sorted_lines')
    program.lines = 'lines'
    result = program.last_line()
    Program.sorted_lines.assert_called_with('lines')
    assert result == Program.sorted_lines()[-1]


def test_program_last_line_none(program):
    assert program.last_line() is None


def test_program_set_as_next_line(patch, program):
    patch.object(Program, 'last_line', return_value='1')
    program.lines = {'1': {}}
    program.set_as_next_line('2')
    assert Program.last_line.call_count == 1
    assert program.lines['1']['next'] == '2'


def test_program_set_as_next_line_none(patch, program):
    patch.object(Program, 'last_line', return_value=None)
    program.set_as_next_line('1')


def test_program_parse_suite(patch, magic, program):
    patch.object(Program, 'set_as_next_line')
    item = magic(lineno='2', json=magic(return_value={}))
    result = program.parse_suite([item], {'ln': '1'})
    Program.set_as_next_line.assert_called_with(item.lineno)
    assert item.json.call_count == 1
    assert program.lines == {'2': {'parent': '1'}}


def test_program_generate(patch, magic, program):
    patch.many(Program, ['set_as_next_line', 'parse_suite'])
    Program.last_line.return_value = None
    item = magic(lineno='1', json=magic(return_value={}, suite=None))
    program.story = [item]
    result = program.generate()
    Program.set_as_next_line.assert_called_with(item.lineno)
    assert item.json.call_count == 1
    assert result == {'1': {}}


def test_program_generate_suite(patch, magic, program):
    patch.many(Program, ['last_line', 'parse_suite'])
    Program.last_line.return_value = None
    Program.parse_suite.return_value = {'2': {}}
    item = magic(lineno='1', json=magic(return_value={}, suite='suite'))
    program.story = [item]
    result = program.generate()
    Program.parse_suite.assert_called_with(item.suite, {})
    assert '1' in result
    assert result['2'] == {}


def test_program_json(patch, program):
    patch.object(Program, 'generate')
    result = program.json()
    assert Program.generate.call_count == 1
    assert result == {'version': version, 'script': program.generate()}
