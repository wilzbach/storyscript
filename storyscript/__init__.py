import argparse
import json
import os
import sys

from . import resolver
from .lexer import Lexer
from .parser import Parser


__version__ = VERSION = version = '0.0.1'


def parse(script, debug=False):
    _parser = Parser(
        lex_optimize=(not debug),
        yacc_optimize=(not debug)
    )
    return _parser.parse(script, debug=debug)


def all_in_directory(_this, debug):
    _print_filename = '\n\033[92mFile: {}\033[0m\n'
    for _path, _dir, _files in os.walk(_this):
        for _f in _files:
            if _f.endswith('.story'):
                with open(os.path.join(_path, _f), 'r') as f:
                    sys.stdout.write(
                        _print_filename.format(os.path.join(_path, _f))
                    )
                    try:
                        result = parse(
                            f.read(),
                            debug=debug,
                            using_cli=True
                        )
                        sys.stdout.write(
                            json.dumps(
                                result.json(),
                                indent=2,
                                separators=(',', ': ')
                            )
                        )
                    except Exception as e:
                        sys.stdout.write(str(e)+'\n')


def main():
    parser = argparse.ArgumentParser(
        prog='storyscript',
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Learn more at http://storyscript.org'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='StoryScript {} - http://storyscript.org'.format(version)
    )
    parser.add_argument(
        '--debug', '-v',
        action='store_true',
        help='Verbose mode'
    )
    parser.add_argument(
        '--lexer', '-l',
        action='store_true',
        help='Show lexer tokens'
    )
    parser.add_argument(
        '--parse', '-p',
        action='store_true',
        help='Parse only, dont show json dump'
    )
    parser.add_argument(
        '--silent', '-s',
        action='store_true',
        help='Silent mode. Return syntax errors only.'
    )
    parser.add_argument(
        '--file', '-f',
        action='store',
        help='File(s) to parse'
    )
    parser.add_argument(
        'script',
        nargs='?',
        help='File to parse'
    )

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()

        if args.file:
            if os.path.isdir(args.file):
                all_in_directory(args.file, args.debug)
                return
            else:
                with open(args.file) as f:
                    story = f.read()
        else:
            story = args.script.replace('\\n', '\n')\
                               .replace('\\t', '\t')

        if args.lexer:
            lexer = Lexer()
            lexer.input(story)
            for x, tok in enumerate(lexer.lexer):
                sys.stdout.write('\033[90m#\033[0m%s\t%s\n' % (x, str(tok)))

        result = Parser().parse(story, debug=args.debug, using_cli=True)
        if args.parse:
            if not args.silent:
                sys.stdout.write('\033[92mScript syntax passed!\033[0m')
        else:
            if not args.silent:
                sys.stdout.write(
                    json.dumps(
                        result.json(),
                        indent=2,
                        separators=(',', ': ')
                    )
                )


if __name__ == '__main__':
    main()
