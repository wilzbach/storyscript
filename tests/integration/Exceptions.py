# -*- coding: utf-8 -*-
from click import unstyle

from pytest import raises

from storyscript.Story import Story
from storyscript.exceptions.StoryError import StoryError


def test_exceptions_service_name(capsys):
    with raises(StoryError) as e:
        Story('al.pine echo').process()

    message = e.value.message()
    # test with coloring once, but we representing ANSI color codes is tricky
    lines = unstyle(message).splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    al.pine echo'
    assert lines[5] == "E0002: A service name can't contain `.`"


def test_exceptions_arguments_noservice(capsys):
    with raises(StoryError) as e:
        Story('length:10').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    length:10'
    assert lines[5] == 'E0003: You have defined an argument, but not a service'


def test_exceptions_variables_backslash(capsys):
    with raises(StoryError) as e:
        Story('a/b = 0').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    a/b = 0'
    assert lines[5] == "E0005: A variable name can't contain `/`"


def test_exceptions_variables_dash(capsys):
    with raises(StoryError) as e:
        Story('a-b = 0').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    a-b = 0'
    assert lines[5] == "E0006: A variable name can't contain `-`"


def test_exceptions_return_outside(capsys):
    with raises(StoryError) as e:
        Story('return 0').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    return 0'
    assert lines[5] == 'E0004: `return` is allowed only inside functions'


def test_exceptions_missing_value(capsys):
    with raises(StoryError) as e:
        Story('a = ').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 5'
    assert lines[2] == '1|    a = '
    assert lines[5] == 'E0007: Missing value after `=`'


def test_exceptions_file_not_found(capsys):
    with raises(StoryError) as e:
        Story.from_file('this-file-does-not-exist')
    message = e.value.message()
    assert 'File "this-file-does-not-exist" not found at' in message


def test_exceptions_dollar(capsys):
    with raises(StoryError) as e:
        Story('x = $').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 5'
    assert lines[2] == '1|    x = $'
    assert lines[5] == 'E0041: `$` is not allowed here'


def test_exceptions_function_redeclared(capsys):
    with raises(StoryError) as e:
        Story('function f1\n\treturn 42\nfunction f1\n\treturn 42\n').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 3, column 10'
    assert lines[2] == '3|    function f1'
    assert lines[5] == 'E0042: `f1` has already been declared at line 1'


def test_exceptions_block_expected_before(capsys):
    with raises(StoryError) as e:
        Story('while true').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 11'
    assert lines[2] == '1|    while true'
    assert lines[5] == 'E0045: An indented block is required to follow here'


def test_exceptions_block_expected_after(capsys):
    with raises(StoryError) as e:
        Story('while true\na = 2').process()
    e.value.with_color = False
    lines = e.value.message().splitlines()
    assert lines[0] == 'Error: syntax error in story at line 2, column 1'
    assert lines[2] == '2|    a = 2'
    assert lines[5] == 'E0046: An indented block is required to be before here'
