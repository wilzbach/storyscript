import click

from .app import App
from .version import version as app_version


class Cli:

    version_help = 'Prints Storyscript version'
    debug_help = 'Debug mode'
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
    def lexer(storypath):
        """
        Shows lexer tokens for given stories
        """
        results = App.lexer(storypath)
        message = '{} {}'
        for file, tokens in results.items():
            click.echo('File: {}'.format(file))
            for x, tok in enumerate(tokens):
                click.echo(message.format(x, tok))

    @staticmethod
    @main.command()
    @click.argument('storypath')
    @click.option('--json', '-j', is_flag=True)
    @click.option('--silent', '-s', is_flag=True, help=silent_help)
    @click.option('--debug', '-d', is_flag=True, help=debug_help)
    def parse(storypath, json, silent, debug):
        """
        Parses stories and prints the resulting json
        """
        results = App.parse(storypath, debug=debug, as_json=json)
        if not silent:
            if not json:
                click.echo('Script syntax passed!', fg='green')
                exit()

            for file, story_json in results.items():
                click.echo('File: {}'.format(file))
                click.echo(story_json)
