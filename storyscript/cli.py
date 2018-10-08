# -*- coding: utf-8 -*-
import os

import click

from .app import App
from .version import version as app_version


class Cli:

    version_help = 'Prints Storyscript version'
    silent_help = 'Silent mode. Return syntax errors only.'
    ebnf_file_help = 'Load the grammar from a file. Useful for development'

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
    @click.argument('storypath', default=os.getcwd())
    @click.argument('output_file_path', required=False)
    @click.option('--json', '-j', is_flag=True)
    @click.option('--silent', '-s', is_flag=True, help=silent_help)
    @click.option('--debug', is_flag=True)
    @click.option('--ebnf-file', help=ebnf_file_help)
    def compile(storypath, output_file_path, json, silent, debug, ebnf_file):
        """
        Compiles stories and prints the resulting json
        """
        results = App.compile(storypath, ebnf_file=ebnf_file, debug=debug)
        if not silent:
            if json:
                if output_file_path:
                    with open(output_file_path, 'w') as f:
                        f.write(results)
                    exit()
                click.echo(results)
            else:
                click.echo(click.style('Script syntax passed!', fg='green'))

    @staticmethod
    @main.command()
    @click.argument('storypath', default=os.getcwd())
    def lex(storypath):
        """
        Shows lexer tokens for given stories
        """
        results = App.lex(storypath)
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
    def version():
        click.echo(app_version)
