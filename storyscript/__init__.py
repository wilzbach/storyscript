import argparse
import json
import os
import sys

from . import exceptions
from . import resolver
from .lexer import Lexer
from .parser import Parser
from .version import version


__version__ = VERSION = version


def parse(script, debug=False):
    _parser = Parser(
        lex_optimize=(not debug),
        yacc_optimize=(not debug)
    )
    return _parser.parse(script, debug=debug)
