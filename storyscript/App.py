# -*- coding: utf-8 -*-
import json

from .Bundle import Bundle
from .compiler.Preprocessor import Preprocessor
from .parser import Grammar


class App:
    """
    Exposes functionalities for internal use e.g the command line
    """

    @staticmethod
    def parse(path, ignored_path=None, ebnf=None, preprocess=False):
        """
        Parses stories found in path, returning their trees
        """
        bundle = Bundle.from_path(path, ignored_path=ignored_path)
        stories = bundle.bundle_trees(ebnf=ebnf)
        if preprocess:
            for story, tree in stories.items():
                stories[story] = Preprocessor.process(tree)
        return stories

    @staticmethod
    def compile(path, ignored_path=None, ebnf=None, concise=False):
        """
        Parses and compiles stories found in path, returning JSON
        """
        bundle = Bundle.from_path(path, ignored_path=ignored_path)
        result = bundle.bundle(ebnf=ebnf)
        if concise:
            result = _clean_dict(result)
        return json.dumps(result, indent=2)

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


def _clean_dict(d):
    """
    Removes all falsy elements from a nested dict
    """
    if not isinstance(d, dict):
        return d
    return {k: _clean_dict(v) for k, v in d.items() if v}
