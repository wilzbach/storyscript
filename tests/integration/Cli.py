# -*- coding: utf-8 -*-
import io
from unittest import mock

from click.testing import CliRunner

from pytest import fixture

from storyscript.Cli import Cli


@fixture
def runner():
    return CliRunner()


def test_cli_exit_code(mocker):
    """
    Ensures that compiler exits with a non-zero exit code on errors
    """
    runner = CliRunner()
    m = mock.mock_open(read_data='foo =')
    mocker.patch.object(io, 'open', m)
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


def test_cli_parse_file(mocker, runner):
    """
    Ensures that parser command works properly
    """
    m = mock.mock_open(read_data='foo')
    mocker.patch.object(io, 'open', m)
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


def test_cli_parse_preprocess_file(mocker, runner):
    """
    Ensures that parser with proprocess works properly
    """
    m = mock.mock_open(read_data='".{a}"')
    mocker.patch.object(io, 'open', m)
    e = runner.invoke(Cli.parse, ['--preprocess', '/parse/path'])

    assert e.output == """File: /parse/path
start
  block
    rules
      absolute_expression
        expression
          or_expression
            and_expression
              cmp_expression
                arith_expression
                  arith_expression
                    mul_expression
                      unary_expression
                        pow_expression
                          primary_expression
                            entity
                              values
                                string	"."
                  arith_operator	+
                  mul_expression
                    unary_expression
                      pow_expression
                        primary_expression
                          entity
                            path	a

"""
    assert e.exit_code == 0


def test_cli_lex(mocker, runner):
    """
    Ensures that lexer command works properly
    """
    m = mock.mock_open(read_data='foo')
    mocker.patch('io.open', m)
    e = runner.invoke(Cli.lex, ['/lex/path'])
    assert e.output == """File: /lex/path
0 NAME foo
"""
    assert e.exit_code == 0
