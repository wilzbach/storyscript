# -*- coding: utf-8 -*-
#
from unittest import mock

from click.testing import CliRunner

from storyscript.Cli import Cli


def test_cli_exit_code():
    """
    Ensures that compiler exits with a non-zero exit code on errors
    """
    runner = CliRunner()
    m = mock.mock_open(read_data='foo =')
    e = None
    with mock.patch('io.open', m):
        e = runner.invoke(Cli.compile, ['/path'])

    assert e.exit_code == 1
    assert e.output == \
        """Error: syntax error in story at line 1, column 6

1|    foo =
           ^

E0007: Missing value after `=`
"""


def test_cli_exit_file_not_found():
    """
    Ensures that compiler exits with a non-zero exit code
    on a file not found error
    """
    runner = CliRunner()
    e = runner.invoke(Cli.compile, ['this-path-will-never-ever-exist-123456'])

    assert e.exit_code == 1
    # the error message contains the absolute path too
    assert 'File `this-path-will-never-ever-exist-123456` not found' \
        in e.output


def test_cli_parse_exit_file_not_found():
    """
    Ensures that compiler exits with a non-zero exit code
    on a file not found error
    """
    runner = CliRunner()
    e = runner.invoke(Cli.parse, ['this-path-will-never-ever-exist-123456'])

    assert e.exit_code == 1
    # the error message contains the absolute path too
    assert 'File `this-path-will-never-ever-exist-123456` not found' \
        in e.output


def test_cli_lex_exit_file_not_found():
    """
    Ensures that compiler exits with a non-zero exit code
    on a file not found error
    """
    runner = CliRunner()
    e = runner.invoke(Cli.parse, ['this-path-will-never-ever-exist-123456'])

    assert e.exit_code == 1
    # the error message contains the absolute path too
    assert 'File `this-path-will-never-ever-exist-123456` not found' \
        in e.output
