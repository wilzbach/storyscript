# -*- coding: utf-8 -*-
import json
import os

from .bundle import Bundle
from .parser import Grammar
from .story import Story


class App:
    """
    Exposes functionalities for internal use e.g the command line
    """

    @staticmethod
    def parse(path, ebnf=None, debug=None):
        """
        Parses stories found in path, returning their trees
        """
        return Bundle(path).parse(ebnf=ebnf, debug=debug)

    @staticmethod
    def compile(path, ebnf=None, debug=False):
        """
        Parses and compiles stories found in path, returning JSON
        """
        bundle = Bundle(path).bundle(ebnf=ebnf, debug=debug)
        return json.dumps(bundle, indent=2)

    @staticmethod
    def lex(path, ebnf=None):
        """
        Lex stories, producing the list of used tokens
        """
        return Bundle(path).lex(ebnf=ebnf)

    @staticmethod
    def grammar():
        """
        Returns the current grammar
        """
        return Grammar().build()
