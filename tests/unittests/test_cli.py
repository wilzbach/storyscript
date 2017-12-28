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


def test_cli_version(mocker, runner, echo):
    """
    Ensures --version outputs the version
    """
    runner.invoke(Cli.main, ['--version'])
    click.echo.assert_called_with('StoryScript 0.0.1 - http://storyscript.org')


def test_cli_story(runner, echo, app):
    """
    Ensures passing a path results in a story being parsed and outputted
    """
    runner.invoke(Cli.main, ['/path/to/story'])
    App.parse.assert_called_with('/path/to/story', debug=False)
    click.echo.assert_called_with(App.parse())


@mark.parametrize('debug', ['--debug', '-v'])
def test_cli_story_debug(runner, app, debug):
    """
    Ensures --debug is passed where needed
    """
    runner.invoke(Cli.main, ['/path/to/story', debug])
    App.parse.assert_called_with('/path/to/story', debug=True)


@mark.parametrize('option', ['--silent', '-s'])
def test_cli_story_silent(runner, echo, app, option):
    """
    Ensures --silent makes everything quiet
    """
    result = runner.invoke(Cli.main, ['/path/to/story', option])
    assert result.output == ''
    assert click.echo.call_count == 0


@mark.parametrize('option', ['--parse', '-p'])
def test_cli_story_parse(runner, echo, app, option):
    """
    Ensures --parse outputs the final state and not the entire result
    """
    runner.invoke(Cli.main, ['/path/to/story', option])
    click.echo.assert_called_with('Script syntax passed!', fg='green')


@mark.parametrize('lexer', ['--lexer', '-l'])
def test_cli_story_lexer(mocker, runner, app, echo, lexer):
    """
    Ensures --lexer outputs lexer tokens
    """
    mocker.patch.object(App, 'lexer', return_value=['one'])
    runner.invoke(Cli.main, ['/path/to/story', lexer])
    app.lexer.assert_called_with('/path/to/story')
    click.echo.assert_called_with('0 one')
