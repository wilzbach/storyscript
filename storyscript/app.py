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

    @classmethod
    def compile(cls, path, ebnf=None, debug=False):
        """
        Parse and compile stories in path to JSON
        """
        bundle = Bundle(path).bundle(ebnf=ebnf, debug=debug)
        return json.dumps(bundle, indent=2)

    @classmethod
    def lex(cls, path, ebnf=None):
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
