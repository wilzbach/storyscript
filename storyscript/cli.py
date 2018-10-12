# -*- coding: utf-8 -*-
import io
import os

import click

from .app import App
from .version import version as app_version


class Cli:

    version_help = 'Prints Storyscript version'
    silent_help = 'Silent mode. Return syntax errors only.'
    ebnf_help = 'Load the grammar from a file. Useful for development'

    @click.group(invoke_without_command=True)
    @click.option('--version', is_flag=True, help=version_help)
    @click.pass_context
    def main(context, version): # noqa N805
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
    @main.command()
    @click.argument('path', default=os.getcwd())
    @click.option('--debug', is_flag=True)
    @click.option('--ebnf', help=ebnf_help)
    def parse(path, debug, ebnf):
        """
        Parses stories, producing the abstract syntax tree.
        """
        App.parse(path, ebnf=ebnf, debug=debug)

    @staticmethod
    @main.command()
    @click.argument('path', default=os.getcwd())
    @click.argument('output', required=False)
    @click.option('--json', '-j', is_flag=True)
    @click.option('--silent', '-s', is_flag=True, help=silent_help)
    @click.option('--debug', is_flag=True)
    @click.option('--ebnf', help=ebnf_help)
    def compile(path, output, json, silent, debug, ebnf):
        """
        Compiles stories and prints the resulting json
        """
        results = App.compile(path, ebnf=ebnf, debug=debug)
        if not silent:
            if json:
                if output:
                    with io.open(output, 'w') as f:
                        f.write(results)
                    exit()
                click.echo(results)
            else:
                click.echo(click.style('Script syntax passed!', fg='green'))

    @staticmethod
    @main.command()
    @click.argument('path', default=os.getcwd())
    @click.option('--ebnf', help=ebnf_help)
    def lex(path, ebnf):
        """
        Shows lexer tokens for given stories
        """
        results = App.lex(path, ebnf=ebnf)
        for file, tokens in results.items():
            click.echo('File: {}'.format(file))
            for n, token in enumerate(tokens):
                click.echo('{} {} {}'.format(n, token.type, token.value))

    @staticmethod
    @main.command()
    def grammar():
        """
        Prints the grammar specification
        """
        click.echo(App.grammar())

    @staticmethod
    @main.command()
    @click.pass_context
    def help(context):
        """
        Prints this help text
        """
        click.echo(context.parent.get_help())

    @staticmethod
    @main.command()
    def version():
        click.echo(app_version)
