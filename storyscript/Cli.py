# -*- coding: utf-8 -*-
import io
import os

import click

from click_alias import ClickAliasedGroup

from .App import App
from .Project import Project
from .Version import version as app_version
from .exceptions import StoryError


class Cli:

    version_help = 'Prints Storyscript version'
    silent_help = 'Silent mode. Return syntax errors only.'
    ebnf_help = 'Load the grammar from a file. Useful for development'

    @click.group(invoke_without_command=True, cls=ClickAliasedGroup)
    @click.option('--version', '-v', is_flag=True, help=version_help)
    @click.pass_context
    def main(context, version):  # noqa N805
        """
        Learn more at http://storyscript.org
        """
        if version:
            message = 'StoryScript {} - http://storyscript.org'
            click.echo(message.format(app_version))
            exit()

        if context.invoked_subcommand is None:
            click.echo(context.get_help())

    @staticmethod
    @main.command(aliases=['p'])
    @click.argument('path', default=os.getcwd())
    @click.option('--debug', is_flag=True)
    @click.option('--ebnf', help=ebnf_help)
    @click.option('--raw', is_flag=True)
    @click.option('--lower', is_flag=True)
    @click.option('--ignore', default=None,
                  help='Specify path of ignored files')
    def parse(path, debug, ebnf, raw, ignore, lower):
        """
        Parses stories, producing the abstract syntax tree.
        """
        try:
            trees = App.parse(path, ignored_path=ignore, ebnf=ebnf,
                              lower=lower)
            for story, tree in trees.items():
                click.echo('File: {}'.format(story))
                if raw:
                    click.echo(tree)
                else:
                    click.echo(tree.pretty())
        except StoryError as e:
            if debug:
                raise e.error
            else:
                e.echo()
                exit(1)
        except Exception as e:
            if debug:
                raise e
            else:
                StoryError.internal_error(e).echo()
                exit(1)

    @staticmethod
    @main.command(aliases=['c'])
    @click.argument('path', default=os.getcwd())
    @click.argument('output', required=False)
    @click.option('--json', '-j', is_flag=True)
    @click.option('--silent', '-s', is_flag=True, help=silent_help)
    @click.option('--debug', is_flag=True)
    @click.option('--concise', '-c', is_flag=True)
    @click.option('--first', '-f', is_flag=True)
    @click.option('--ebnf', help=ebnf_help)
    @click.option('--ignore', default=None,
                  help='Specify path of ignored files')
    def compile(path, output, json, silent, debug, ebnf, ignore, concise,
                first):
        """
        Compiles stories and prints the resulting json
        """
        try:
            results = App.compile(path, ignored_path=ignore,
                                  ebnf=ebnf, concise=concise, first=first)
            if not silent:
                if json:
                    if output:
                        with io.open(output, 'w') as f:
                            f.write(results)
                        exit()
                    click.echo(results)
                else:
                    msg = 'Script syntax passed!'
                    click.echo(click.style(msg, fg='green'))
        except StoryError as e:
            if debug:
                raise e.error
            else:
                e.echo()
                exit(1)
        except Exception as e:
            if debug:
                raise e
            else:
                StoryError.internal_error(e).echo()
                exit(1)

    @staticmethod
    @main.command(aliases=['l'])
    @click.argument('path', default=os.getcwd())
    @click.option('--ebnf', help=ebnf_help)
    @click.option('--debug', is_flag=True)
    def lex(path, ebnf, debug):
        """
        Shows lexer tokens for given stories
        """
        try:
            results = App.lex(path, ebnf=ebnf)
            for file, tokens in results.items():
                click.echo('File: {}'.format(file))
                for n, token in enumerate(tokens):
                    click.echo('{} {} {}'.format(n, token.type, token.value))
        except StoryError as e:
            if debug:
                raise e.error
            else:
                e.echo()
                exit(1)
        except Exception as e:
            if debug:
                raise e
            else:
                StoryError.internal_error(e).echo()
                exit(1)

    @staticmethod
    @main.command(aliases=['g'])
    def grammar():
        """
        Prints the grammar specification
        """
        click.echo(App.grammar())

    @staticmethod
    @main.command(aliases=['n'])
    @click.argument('name')
    def new(name):
        """
        Creates a new project
        """
        Project.new(name)

    @staticmethod
    @main.command(aliases=['h'])
    @click.pass_context
    def help(context):
        """
        Prints this help text
        """
        click.echo(context.parent.get_help())

    @staticmethod
    @main.command(aliases=['v'])
    def version():
        click.echo(app_version)
