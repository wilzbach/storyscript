# -*- coding: utf-8 -*-
import json

from .Bundle import Bundle
from .parser import Grammar


class App:
    """
    Exposes functionalities for internal use e.g the command line
    """

    @staticmethod
    def parse(path, ignored_path=None, ebnf=None, debug=None):
        """
        Parses stories found in path, returning their trees
        """
        bundle = Bundle.from_path(path, ignored_path=ignored_path)
        return bundle.bundle_trees(ebnf=ebnf, debug=debug)

    @staticmethod
    def compile(path, ignored_path=None, ebnf=None, debug=False):
        """
        Parses and compiles stories found in path, returning JSON
        """
        bundle = Bundle.from_path(path, ignored_path=ignored_path)
        return json.dumps(bundle.bundle(ebnf=ebnf, debug=debug), indent=2)

    @staticmethod
    def lex(path, ebnf=None):
        """
        Lex stories, producing the list of used tokens
        """
        return Bundle.from_path(path).lex(ebnf=ebnf)

    @staticmethod
    def grammar():
        """
        Returns the current grammar
        """
        return Grammar().build()
