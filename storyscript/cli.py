import click

from .app import App
from .version import version as app_version


class Cli:

    version_help = 'Prints Storyscript version'
    silent_help = 'Silent mode. Return syntax errors only.'

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
    @click.option('--json', '-j', is_flag=True)
    @click.option('--silent', '-s', is_flag=True, help=silent_help)
    def parse(storypath, json, silent):
        """
        Parses stories and prints the resulting json
        """
        results = App.compile(storypath)
        if not silent:
            if not json:
                click.echo(click.style('Script syntax passed!', fg='green'))
                exit()

            for file, story_json in results.items():
                click.echo('File: {}'.format(file))
                click.echo(story_json)

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
