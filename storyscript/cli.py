# -*- coding: utf-8 -*-
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
    @click.argument('storypath')
    @click.argument('output_file_path', required=False)
    @click.option('--json', '-j', is_flag=True)
    @click.option('--silent', '-s', is_flag=True, help=silent_help)
    @click.option('--ebnf-file', help=ebnf_file_help)
    def parse(storypath, output_file_path, json, silent, ebnf_file):
        """
        Parses stories and prints the resulting json
        """
        results = App.compile(storypath, ebnf_file=ebnf_file)
        if not silent:
            if json:
                click.echo(results)
            else:
                click.echo(click.style('Script syntax passed!', fg='green'))
        if output_file_path:
            with open(output_file_path, "w") as output_file:
                output_file.write(results)

    @staticmethod
    @main.command()
    @click.argument('storypath')
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
