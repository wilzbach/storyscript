# -*- coding: utf-8 -*-
from pytest import raises

from storyscript.Story import Story


def test_exception_service_name(capsys):
    with raises(SystemExit):
        Story('al.pine echo').process()
    output, error = capsys.readouterr()
    lines = output.splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    al.pine echo'
    assert lines[5] == "A service name can't contain `.`"


def test_exception_arguments_noservice(capsys):
    with raises(SystemExit):
        Story('length:10').process()
    output, error = capsys.readouterr()
    lines = output.splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    length:10'
    assert lines[5] == 'You have defined an argument, but not a service'


def test_exception_variables_backslash(capsys):
    with raises(SystemExit):
        Story('a/b = 0').process()
    output, error = capsys.readouterr()
    lines = output.splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    a/b = 0'
    assert lines[5] == "A variable name can't contain `/`"


def test_exception_variables_dash(capsys):
    with raises(SystemExit):
        Story('a-b = 0').process()
    output, error = capsys.readouterr()
    lines = output.splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 1'
    assert lines[2] == '1|    a-b = 0'
    assert lines[5] == "A variable name can't contain `-`"


def test_exception_return_outside(capsys):
    with raises(SystemExit):
        Story('return 0').process()
    output, error = capsys.readouterr()
    lines = output.splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 8'
    assert lines[2] == '1|    return 0'
    assert lines[5] == '`return` is allowed only inside functions'


def test_exception_missing_value(capsys):
    with raises(SystemExit):
        Story('a = ').process()
    output, error = capsys.readouterr()
    lines = output.splitlines()
    assert lines[0] == 'Error: syntax error in story at line 1, column 5'
    assert lines[2] == '1|    a = '
    assert lines[5] == 'Missing value after `=`'
