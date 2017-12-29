import argparse
import json
import os
import sys

from . import exceptions
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
