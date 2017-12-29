import click
from click.testing import CliRunner

from pytest import fixture, mark

from storyscript.app import App
from storyscript.cli import Cli


@fixture
def runner():
    return CliRunner()


@fixture
def echo(mocker):
    mocker.patch.object(click, 'echo')


@fixture
def app(mocker):
    mocker.patch.object(App, 'parse')
    return App


def test_cli(mocker, runner, echo):
    runner.invoke(Cli.main, [])
    # NOTE(vesuvium): I didn't find how to get the context in testing
    click.echo.call_count == 1


def test_cli_version(mocker, runner, echo):
    """
    Ensures --version outputs the version
    """
    runner.invoke(Cli.main, ['--version'])
    click.echo.assert_called_with('StoryScript 0.0.1 - http://storyscript.org')


def test_cli_lexer(mocker, runner, app, echo):
    """
    Ensures the lexer command outputs lexer tokens
    """
    mocker.patch.object(App, 'lexer', return_value={'one.story': ['run']})
    runner.invoke(Cli.lexer, ['/path/to/story'])
    app.lexer.assert_called_with('/path/to/story')
    click.echo.assert_called_with('0 run')
    assert click.echo.call_count == 2


def test_cli_parse(runner, echo, app):
    """
    Ensures the parse command parses a story
    """
    runner.invoke(Cli.parse, ['/path/to/story'])
    App.parse.assert_called_with('/path/to/story', debug=False, as_json=False)
    click.echo.assert_called_with('Script syntax passed!', fg='green')


@mark.parametrize('debug', ['--debug', '-d'])
def test_cli_parse_debug(runner, app, debug):
    """
    Ensures --debug is passed where needed
    """
    runner.invoke(Cli.parse, ['/path/to/story', debug])
    App.parse.assert_called_with('/path/to/story', debug=True, as_json=False)


@mark.parametrize('option', ['--silent', '-s'])
def test_cli_parse_silent(runner, echo, app, option):
    """
    Ensures --silent makes everything quiet
    """
    result = runner.invoke(Cli.parse, ['/path/to/story', option])
    App.parse.assert_called_with('/path/to/story', debug=False, as_json=False)
    assert result.output == ''
    assert click.echo.call_count == 0


@mark.parametrize('option', ['--json', '-j'])
def test_cli_parse_json(mocker, runner, echo, app, option):
    """
    Ensures --json outputs json
    """
    App.parse.return_value = {'story.one': 'json'}
    result = runner.invoke(Cli.parse, ['/path/to/story', option])
    click.echo.assert_called_with('json')
    assert click.echo.call_count == 2
