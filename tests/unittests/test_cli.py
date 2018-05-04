import click
from click.testing import CliRunner

from pytest import fixture, mark

from storyscript.app import App
from storyscript.cli import Cli
from storyscript.version import version


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
    message = 'StoryScript {} - http://storyscript.org'.format(version)
    click.echo.assert_called_with(message)


def test_cli_parse(mocker, runner, echo, app):
    """
    Ensures the parse command parses a story
    """
    mocker.patch.object(click, 'style')
    runner.invoke(Cli.parse, ['/path/to/story'])
    App.parse.assert_called_with('/path/to/story', debug=False, as_json=False)
    click.style.assert_called_with('Script syntax passed!', fg='green')
    click.echo.assert_called_with(click.style())


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
    runner.invoke(Cli.parse, ['/path/to/story', option])
    click.echo.assert_called_with('json')
    assert click.echo.call_count == 2


def test_cli_lexer(patch, magic, runner, app, echo):
    """
    Ensures the lex command outputs lexer tokens
    """
    token = magic(type='token', value='value')
    patch.object(App, 'lex', return_value={'one.story': [token]})
    runner.invoke(Cli.lex, ['/path'])
    app.lex.assert_called_with('/path')
    click.echo.assert_called_with('0 token value')
    assert click.echo.call_count == 2
