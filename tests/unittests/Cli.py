# -*- coding: utf-8 -*-
import io
import os

import click
from click.testing import CliRunner

from pytest import fixture, mark

from storyscript.App import App
from storyscript.Cli import Cli
from storyscript.Project import Project
from storyscript.Version import version


@fixture
def runner():
    return CliRunner()


@fixture
def echo(patch):
    patch.object(click, 'echo')


@fixture
def app(patch):
    patch.many(App, ['compile', 'parse'])
    return App


def test_cli(runner, echo):
    runner.invoke(Cli.main, [])
    # NOTE(vesuvium): I didn't find how to get the context in testing
    assert click.echo.call_count == 1


def test_cli_alais_parse(runner, app):
    runner.invoke(Cli.main, ['p'])
    assert app.parse.call_count == 1


def test_cli_alais_compile(runner, app):
    runner.invoke(Cli.main, ['c'])
    assert app.compile.call_count == 1


def test_cli_alais_lex(runner, app, patch):
    patch.object(App, 'lex')
    runner.invoke(Cli.main, 'l')
    assert app.lex.call_count == 1


def test_cli_alais_grammar(runner, app, patch):
    patch.object(App, 'grammar')
    runner.invoke(Cli.main, 'g')
    assert app.grammar.call_count == 1


def test_cli_alais_new(patch, runner):
    patch.object(Project, 'new')
    runner.invoke(Cli.main, ['n', 'project'])
    Project.new.assert_called_with('project')


def test_cli_alias_help(runner, echo):
    runner.invoke(Cli.main, 'h')
    click.echo.assert_called_once()


def test_cli_alais_version(runner, echo):
    runner.invoke(Cli.main, 'v')
    click.echo.assert_called_with(version)


def test_cli_alais_version_flag(runner, echo):
    runner.invoke(Cli.main, '-v')
    message = 'StoryScript {} - http://storyscript.org'.format(version)
    click.echo.assert_called_with(message)


def test_cli_version_flag(runner, echo):
    """
    Ensures --version outputs the version
    """
    runner.invoke(Cli.main, ['--version'])
    message = 'StoryScript {} - http://storyscript.org'.format(version)
    click.echo.assert_called_with(message)


def test_cli_compile_with_ignore_option(runner, app):
    """
    Ensures that ignore option works when compiling
    """
    runner.invoke(Cli.compile, ['path/fake.story',
                                '--ignore', 'path/sub_dir/my_fake.story'])
    App.compile.assert_called_with('path/fake.story', ebnf=None, debug=False,
                                   ignored_path='path/sub_dir/my_fake.story')


def test_cli_parse_with_ignore_option(runner, app):
    """
    Ensures that ignore option works when parsing
    """
    runner.invoke(Cli.parse, ['path/fake.story', '--ignore',
                              'path/sub_dir/my_fake.story'])
    App.parse.assert_called_with('path/fake.story', ebnf=None, debug=False,
                                 ignored_path='path/sub_dir/my_fake.story')


def test_cli_parse(runner, echo, app, tree):
    """
    Ensures the parse command produces the trees for given stories.
    """
    App.parse.return_value = {'path': tree}
    runner.invoke(Cli.parse, [])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 debug=False, ignored_path=None)
    click.echo.assert_called_with(tree.pretty())


def test_cli_parse_raw(runner, echo, app, tree):
    """
    Ensures the parse command supports raw trees
    """
    App.parse.return_value = {'path': tree}
    runner.invoke(Cli.parse, ['--raw'])
    click.echo.assert_called_with(tree)


def test_cli_parse_path(runner, echo, app):
    """
    Ensures the parse command supports specifying a path.
    """
    runner.invoke(Cli.parse, ['/path'])
    App.parse.assert_called_with('/path', ebnf=None,
                                 debug=False, ignored_path=None)


def test_cli_parse_ebnf(runner, echo, app):
    """
    Ensures the parse command supports specifying an ebnf file.
    """
    runner.invoke(Cli.parse, ['--ebnf', 'test.ebnf'])
    App.parse.assert_called_with(os.getcwd(), ebnf='test.ebnf',
                                 debug=False, ignored_path=None)


def test_cli_parse_debug(runner, echo, app):
    """
    Ensures the parse command supports a debug flag.
    """
    runner.invoke(Cli.parse, ['--debug'])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 debug=True, ignored_path=None)


def test_cli_compile(patch, runner, echo, app):
    """
    Ensures the compile command compiles a story.
    """
    patch.object(click, 'style')
    runner.invoke(Cli.compile, [])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   debug=False, ignored_path=None)
    click.style.assert_called_with('Script syntax passed!', fg='green')
    click.echo.assert_called_with(click.style())


def test_cli_compile_path(patch, runner, app):
    """
    Ensures the compile command supports specifying a path
    """
    runner.invoke(Cli.compile, ['/path'])
    App.compile.assert_called_with('/path', ebnf=None,
                                   debug=False, ignored_path=None)


def test_cli_compile_output_file(patch, runner, app):
    """
    Ensures the compile command supports specifying an output file.
    """
    patch.object(io, 'open')
    runner.invoke(Cli.compile, ['/path', 'hello.story', '-j'])
    io.open.assert_called_with('hello.story', 'w')
    io.open().__enter__().write.assert_called_with(App.compile())


@mark.parametrize('option', ['--silent', '-s'])
def test_cli_compile_silent(runner, echo, app, option):
    """
    Ensures --silent makes everything quiet
    """
    result = runner.invoke(Cli.compile, [option])
    App.compile.assert_called_with(os.getcwd(), ebnf=None, debug=False,
                                   ignored_path=None)
    assert result.output == ''
    assert click.echo.call_count == 0


def test_cli_compile_debug(runner, echo, app):
    runner.invoke(Cli.compile, ['--debug'])
    App.compile.assert_called_with(os.getcwd(), ebnf=None, debug=True,
                                   ignored_path=None)


@mark.parametrize('option', ['--json', '-j'])
def test_cli_compile_json(runner, echo, app, option):
    """
    Ensures --json outputs json
    """
    runner.invoke(Cli.compile, [option])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   debug=False, ignored_path=None)
    click.echo.assert_called_with(App.compile())


def test_cli_compile_ebnf(runner, echo, app):
    runner.invoke(Cli.compile, ['--ebnf', 'test.ebnf'])
    App.compile.assert_called_with(os.getcwd(), ebnf='test.ebnf',
                                   debug=False, ignored_path=None)


def test_cli_lex(patch, magic, runner, app, echo):
    """
    Ensures the lex command outputs lexer tokens
    """
    token = magic(type='token', value='value')
    patch.object(App, 'lex', return_value={'one.story': [token]})
    runner.invoke(Cli.lex, [])
    App.lex.assert_called_with(os.getcwd(), ebnf=None)
    click.echo.assert_called_with('0 token value')
    assert click.echo.call_count == 2


def test_cli_lex_path(patch, magic, runner, app):
    """
    Ensures the lex command path defaults to cwd
    """
    patch.object(App, 'lex', return_value={'one.story': [magic()]})
    runner.invoke(Cli.lex, ['/path'])
    App.lex.assert_called_with('/path', ebnf=None)


def test_cli_lex_ebnf(patch, runner):
    """
    Ensures the lex command allows specifying an ebnf file.
    """
    patch.object(App, 'lex')
    runner.invoke(Cli.lex, ['--ebnf', 'my.ebnf'])
    App.lex.assert_called_with(os.getcwd(), ebnf='my.ebnf')


def test_cli_grammar(patch, runner, app, echo):
    patch.object(App, 'grammar')
    runner.invoke(Cli.grammar, [])
    assert app.grammar.call_count == 1
    click.echo.assert_called_with(app.grammar())


def test_cli_new(patch, runner):
    """
    Ensures Cli.new uses Project.new
    """
    patch.object(Project, 'new')
    runner.invoke(Cli.new, 'project')
    Project.new.assert_called_with('project')


def test_cli_help(patch, runner, echo):
    runner.invoke(Cli.help, [])
    # NOTE(vesuvium): another weird click thing. The context.parent.get_help
    # seems to mess up with mock, registering no call on click.echo
    assert click.echo.call_count == 0


def test_cli_version(patch, runner, echo):
    runner.invoke(Cli.version, [])
    click.echo.assert_called_with(version)
