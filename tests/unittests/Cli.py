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
from storyscript.exceptions.CompilerError import CompilerError
from storyscript.exceptions.StoryError import StoryError


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


def test_cli_alias_parse(runner, app):
    runner.invoke(Cli.main, ['p'])
    assert app.parse.call_count == 1


def test_cli_alias_compile(runner, app):
    runner.invoke(Cli.main, ['c'])
    assert app.compile.call_count == 1


def test_cli_alias_lex(runner, app, patch):
    patch.object(App, 'lex')
    runner.invoke(Cli.main, 'l')
    assert app.lex.call_count == 1


def test_cli_alias_grammar(runner, app, patch):
    patch.object(App, 'grammar')
    runner.invoke(Cli.main, 'g')
    assert app.grammar.call_count == 1


def test_cli_alias_new(patch, runner):
    patch.object(Project, 'new')
    runner.invoke(Cli.main, ['n', 'project'])
    Project.new.assert_called_with('project')


def test_cli_alias_help(runner, echo):
    runner.invoke(Cli.main, 'h')
    click.echo.assert_called_once()


def test_cli_alias_version(runner, echo):
    runner.invoke(Cli.main, 'v')
    click.echo.assert_called_with(version)


def test_cli_alias_version_flag(runner, echo):
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
    App.compile.assert_called_with('path/fake.story', ebnf=None,
                                   ignored_path='path/sub_dir/my_fake.story',
                                   concise=False, first=False, features={})


def test_cli_parse_with_ignore_option(runner, app):
    """
    Ensures that ignore option works when parsing
    """
    runner.invoke(Cli.parse, ['path/fake.story', '--ignore',
                              'path/sub_dir/my_fake.story'])
    App.parse.assert_called_with('path/fake.story', ebnf=None,
                                 ignored_path='path/sub_dir/my_fake.story',
                                 lower=False, features={})


def test_cli_parse(runner, echo, app, tree):
    """
    Ensures the parse command produces the trees for given stories.
    """
    App.parse.return_value = {'path': tree}
    runner.invoke(Cli.parse, [])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 ignored_path=None, lower=False, features={})
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
                                 ignored_path=None, lower=False, features={})


def test_cli_parse_ebnf(runner, echo, app):
    """
    Ensures the parse command supports specifying an ebnf file.
    """
    runner.invoke(Cli.parse, ['--ebnf', 'test.ebnf'])
    App.parse.assert_called_with(os.getcwd(), ebnf='test.ebnf',
                                 ignored_path=None, lower=False, features={})


def test_cli_parse_lower(runner, echo, app):
    """
    Ensures the parse command supports lowering
    """
    runner.invoke(Cli.parse, ['--lower'])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 ignored_path=None, lower=True, features={})


def test_cli_parse_features(runner, echo, app):
    """
    Ensures the parse command accepts features
    """
    runner.invoke(Cli.parse, ['--preview=globals'])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 ignored_path=None, lower=False,
                                 features={'globals': True})


def test_cli_parse_features_positive(runner, echo, app):
    """
    Ensures the parse command accepts positive features
    """
    runner.invoke(Cli.parse, ['--preview=+globals'])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 ignored_path=None, lower=False,
                                 features={'globals': True})


def test_cli_parse_features_negative(runner, echo, app):
    """
    Ensures the parse command accepts negative features
    """
    runner.invoke(Cli.parse, ['--preview=-globals'])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 ignored_path=None, lower=False,
                                 features={'globals': False})


def test_cli_parse_features_chain(runner, echo, app):
    """
    Ensures the parse command accepts feature chains
    """
    runner.invoke(Cli.parse, ['--preview=globals', '--preview=-globals'])
    App.parse.assert_called_with(os.getcwd(), ebnf=None,
                                 ignored_path=None, lower=False,
                                 features={'globals': False})


def test_cli_parse_features_unknown(runner, echo, app):
    """
    Ensures the parse command reacts to unknown features
    """
    e = runner.invoke(Cli.parse, ['--preview=unknown'])
    App.parse.assert_not_called()
    assert e.exit_code == 1
    click.echo.assert_called_with(
        'E0078: Invalid preview flag. '
        '`unknown` is not a valid preview feature.'
    )


def test_cli_parse_debug(runner, echo, app):
    """
    Ensures the parse command supports raises errors with debug=True
    """
    runner.invoke(Cli.parse, ['--debug'])
    ce = CompilerError(None)
    app.parse.side_effect = StoryError(ce, None)
    e = runner.invoke(Cli.parse, ['--debug', '/a/non/existent/file'])
    assert e.exit_code == 1
    assert isinstance(e.exception, CompilerError)
    assert e.exception.message() == 'Unknown compiler error'


def test_cli_parse_ice(runner, echo, app):
    """
    Ensures the parse command prints unknown errors
    """
    app.parse.side_effect = Exception('ICE')
    e = runner.invoke(Cli.parse, ['/a/non/existent/file'])
    assert e.exit_code == 1
    click.echo.assert_called_with((
        'E0001: Internal error occured: ICE\n'
        'Please report at https://github.com/storyscript/storyscript/issues'))


def test_cli_parse_debug_ice(runner, echo, app):
    """
    Ensures the parse command supports raises unknown errors with debug=True
    """
    app.parse.side_effect = Exception('ICE')
    e = runner.invoke(Cli.parse, ['--debug', '/a/non/existent/file'])
    assert e.exit_code == 1
    assert isinstance(e.exception, Exception)
    assert str(e.exception) == 'ICE'


def test_cli_parse_not_found(runner, echo, app, patch):
    """
    Ensures the parse command catches errors
    """
    patch.object(StoryError, 'message')
    ce = CompilerError(None)
    app.parse.side_effect = StoryError(ce, None)
    e = runner.invoke(Cli.parse, ['/a/non/existent/file'])
    assert e.exit_code == 1
    click.echo.assert_called_with(StoryError.message())


def test_cli_compile(patch, runner, echo, app):
    """
    Ensures the compile command compiles a story.
    """
    patch.object(click, 'style')
    runner.invoke(Cli.compile, [])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   ignored_path=None, concise=False,
                                   first=False, features={})
    click.style.assert_called_with('Script syntax passed!', fg='green')
    click.echo.assert_called_with(click.style())


def test_cli_compile_path(patch, runner, app):
    """
    Ensures the compile command supports specifying a path
    """
    runner.invoke(Cli.compile, ['/path'])
    App.compile.assert_called_with('/path', ebnf=None,
                                   ignored_path=None, concise=False,
                                   first=False, features={})


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
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   ignored_path=None, concise=False,
                                   first=False, features={})
    assert result.output == ''
    assert click.echo.call_count == 0


@mark.parametrize('option', ['--concise', '-c'])
def test_cli_compile_concise(runner, echo, app, option):
    """
    Ensures --concise makes everything concise
    """
    runner.invoke(Cli.compile, [option])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   ignored_path=None, concise=True,
                                   first=False, features={})


@mark.parametrize('option', ['--first', '-f'])
def test_cli_compile_first(runner, echo, app, option):
    """
    Ensures --first only yields the first story
    """
    runner.invoke(Cli.compile, [option])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   ignored_path=None, concise=False,
                                   first=True, features={})


def test_cli_compile_debug(runner, echo, app):
    runner.invoke(Cli.compile, ['--debug'])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   ignored_path=None, concise=False,
                                   first=False, features={})


def test_cli_compile_features(runner, echo, app):
    runner.invoke(Cli.compile, ['--preview=globals'])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   ignored_path=None, concise=False,
                                   first=False, features={'globals': True})


@mark.parametrize('option', ['--json', '-j'])
def test_cli_compile_json(runner, echo, app, option):
    """
    Ensures --json outputs json
    """
    runner.invoke(Cli.compile, [option])
    App.compile.assert_called_with(os.getcwd(), ebnf=None,
                                   ignored_path=None, concise=False,
                                   first=False, features={})
    click.echo.assert_called_with(App.compile())


def test_cli_compile_ebnf(runner, echo, app):
    runner.invoke(Cli.compile, ['--ebnf', 'test.ebnf'])
    App.compile.assert_called_with(os.getcwd(), ebnf='test.ebnf',
                                   ignored_path=None, concise=False,
                                   first=False, features={})


def test_cli_compile_ice(runner, echo, app):
    """
    Ensures the compile command prints unknown errors
    """
    app.compile.side_effect = Exception('ICE')
    e = runner.invoke(Cli.compile, ['/a/non/existent/file'])
    assert e.exit_code == 1
    click.echo.assert_called_with((
        'E0001: Internal error occured: ICE\n'
        'Please report at https://github.com/storyscript/storyscript/issues'))


def test_cli_compile_debug_ice(runner, echo, app):
    """
    Ensures the compile command supports raises unknown errors with debug=True
    """
    app.compile.side_effect = Exception('ICE')
    e = runner.invoke(Cli.compile, ['--debug', '/a/non/existent/file'])
    assert e.exit_code == 1
    assert isinstance(e.exception, Exception)
    assert str(e.exception) == 'ICE'


def test_cli_compile_not_found(patch, runner, echo, app):
    """
    Ensures the compile command catches errors
    """
    ce = CompilerError(None)
    app.compile.side_effect = StoryError(ce, None)
    e = runner.invoke(Cli.compile, ['/a/non/existent/file'])
    assert e.exit_code == 1
    click.echo.assert_called_with(f'E0001: {StoryError._internal_error(ce)}')


def test_cli_compile_not_found_debug(runner, echo, app):
    """
    Ensures the compile command raises errors with debug=True
    """
    ce = CompilerError(None)
    app.compile.side_effect = StoryError(ce, None)
    e = runner.invoke(Cli.compile, ['--debug', '/a/non/existent/file'])
    assert e.exit_code == 1
    assert isinstance(e.exception, CompilerError)
    assert e.exception.message() == 'Unknown compiler error'


def test_cli_lex(patch, magic, runner, app, echo):
    """
    Ensures the lex command outputs lexer tokens
    """
    token = magic(type='token', value='value')
    patch.object(App, 'lex', return_value={'one.story': [token]})
    runner.invoke(Cli.lex, [])
    App.lex.assert_called_with(os.getcwd(), ebnf=None, features={})
    click.echo.assert_called_with('0 token value')
    assert click.echo.call_count == 2


def test_cli_lex_path(patch, magic, runner, app):
    """
    Ensures the lex command path defaults to cwd
    """
    patch.object(App, 'lex', return_value={'one.story': [magic()]})
    runner.invoke(Cli.lex, ['/path'])
    App.lex.assert_called_with('/path', ebnf=None, features={})


def test_cli_lex_ebnf(patch, runner):
    """
    Ensures the lex command allows specifying an ebnf file.
    """
    patch.object(App, 'lex')
    runner.invoke(Cli.lex, ['--ebnf', 'my.ebnf'])
    App.lex.assert_called_with(os.getcwd(), ebnf='my.ebnf', features={})


def test_cli_lex_features(patch, runner):
    """
    Ensures the lex command allows specifying features
    """
    patch.object(App, 'lex')
    runner.invoke(Cli.lex, ['--preview=globals'])
    App.lex.assert_called_with(os.getcwd(), ebnf=None,
                               features={'globals': True})


def test_cli_lex_ice(patch, runner, echo, app):
    """
    Ensures the lex command prints unknown errors
    """
    patch.object(App, 'lex', side_effect=Exception('ICE'))
    e = runner.invoke(Cli.lex, ['/a/non/existent/file'])
    assert e.exit_code == 1
    click.echo.assert_called_with((
        'E0001: Internal error occured: ICE\n'
        'Please report at https://github.com/storyscript/storyscript/issues'))


def test_cli_lex_debug_ice(patch, runner, echo, app):
    """
    Ensures the lex command supports raises unknown errors with debug=True
    """
    patch.object(App, 'lex', side_effect=Exception('ICE'))
    e = runner.invoke(Cli.lex, ['--debug', '/a/non/existent/file'])
    assert e.exit_code == 1
    assert isinstance(e.exception, Exception)
    assert str(e.exception) == 'ICE'


def test_cli_lex_not_found(patch, runner, echo, app):
    """
    Ensures the lex command catches errors
    """
    patch.object(StoryError, 'message')
    ce = CompilerError(None)
    patch.object(App, 'lex')
    App.lex.side_effect = StoryError(ce, None)
    e = runner.invoke(Cli.lex, ['/a/non/existent/file'])
    assert e.exit_code == 1
    click.echo.assert_called_with(StoryError.message())


def test_cli_lex_not_found_debug(patch, runner, echo, app):
    """
    Ensures the lex command raises errors with debug=True
    """
    ce = CompilerError(None)
    patch.object(App, 'lex')
    App.lex.side_effect = StoryError(ce, None)
    e = runner.invoke(Cli.lex, ['--debug', '/a/non/existent/file'])
    assert e.exit_code == 1
    assert isinstance(e.exception, CompilerError)
    assert e.exception.message() == 'Unknown compiler error'


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
