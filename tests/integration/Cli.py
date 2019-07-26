# -*- coding: utf-8 -*-
from unittest import mock

from click.testing import CliRunner

from pytest import fixture

import storyscript.Story as StoryModule
from storyscript.Cli import Cli


@fixture
def runner():
    return CliRunner()


@fixture
def open_mock(mocker):
    m = mocker.patch.object(StoryModule, 'bom_open')
    return m


def test_cli_exit_code(open_mock):
    """
    Ensures that compiler exits with a non-zero exit code on errors
    """
    runner = CliRunner()
    mock.mock_open(open_mock, read_data='foo =')
    e = runner.invoke(Cli.compile, ['/compile/path'])

    assert e.exit_code == 1
    assert e.output == \
        """Error: syntax error in story at line 1, column 6

1|    foo =
           ^

E0007: Missing value after `=`
"""


def test_cli_exit_file_not_found(runner):
    """
    Ensures that compiler exits with a non-zero exit code
    on a file not found error
    """
    e = runner.invoke(Cli.compile, ['this-path-will-never-ever-exist-123456'])

    assert e.exit_code == 1
    # the error message contains the absolute path too
    assert 'File `this-path-will-never-ever-exist-123456` not found' \
        in e.output


def test_cli_parse_exit_file_not_found(runner):
    """
    Ensures that compiler exits with a non-zero exit code
    on a file not found error
    """
    e = runner.invoke(Cli.parse, ['this-path-will-never-ever-exist-123456'])

    assert e.exit_code == 1
    # the error message contains the absolute path too
    assert 'File `this-path-will-never-ever-exist-123456` not found' \
        in e.output


def test_cli_lex_exit_file_not_found(runner):
    """
    Ensures that compiler exits with a non-zero exit code
    on a file not found error
    """
    e = runner.invoke(Cli.parse, ['this-path-will-never-ever-exist-123456'])

    assert e.exit_code == 1
    # the error message contains the absolute path too
    assert 'File `this-path-will-never-ever-exist-123456` not found' \
        in e.output


def test_cli_parse_file(open_mock, runner):
    """
    Ensures that parser command works properly
    """
    mock.mock_open(open_mock, read_data='foo')
    e = runner.invoke(Cli.parse, ['/parse/path'])

    assert e.output == """File: /parse/path
start
  block
    rules
      service_block
        service
          path	foo
          service_fragment

"""
    assert e.exit_code == 0


def test_cli_parse_lower_file(open_mock, runner):
    """
    Ensures that parser with --lower works properly
    """
    mock.mock_open(open_mock, read_data='".{a}"')
    e = runner.invoke(Cli.parse, ['--lower', '/parse/path'])

    assert e.output == """File: /parse/path
start
  block
    rules
      absolute_expression
        expression
          expression
            entity
              values
                string	.
          arith_operator	+
          expression
            expression
              entity
                path	a
            as_operator
              types
                base_type	string

"""
    assert e.exit_code == 0


def test_cli_lex(open_mock, runner):
    """
    Ensures that lexer command works properly
    """
    mock.mock_open(open_mock, read_data='foo')
    e = runner.invoke(Cli.lex, ['/lex/path'])
    assert e.output == """File: /lex/path
0 NAME foo
"""
    assert e.exit_code == 0
