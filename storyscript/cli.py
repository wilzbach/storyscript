import click

from .app import App
from .version import version as app_version


class Cli:

    version_help = 'Prints Storyscript version'
    debug_help = 'Prints Storyscript version'
    silent_help = 'Silent mode. Return syntax errors only.'
    lexer_help = 'Show lexer tokens'
    parse_help = 'Parse only, dont show json dump'

    @staticmethod
    @click.command()
    @click.option('--version', is_flag=True, help=version_help)
    @click.option('--debug', '-v', is_flag=True, help=debug_help)
    @click.option('--silent', '-s', is_flag=True, help=silent_help)
    @click.option('--lexer', '-l', is_flag=True, help=lexer_help)
    @click.option('--parse', '-p', is_flag=True, help=parse_help)
    @click.argument('storypath', required=False)
    def main(version, debug, silent, lexer, parse, storypath):
        if version:
            message = 'StoryScript {} - http://storyscript.org'
            click.echo(message.format(app_version))
            exit()

        if lexer:
            result = App.lexer(storypath)
            message = '{} {}'
            for x, tok in enumerate(result):
                click.echo(message.format(x, tok))
            exit()

        result = App.parse(storypath, debug=debug)
        if not silent:
            if parse:
                click.echo('Script syntax passed!', fg='green')
                exit()
            click.echo(result)
