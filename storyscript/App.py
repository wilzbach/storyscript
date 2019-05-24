# -*- coding: utf-8 -*-
import json

from .Bundle import Bundle
from .exceptions import StoryError
from .parser import Grammar


class App:
    """
    Exposes functionalities for internal use e.g the command line
    """

    @staticmethod
    def parse(path, ignored_path=None, ebnf=None, lower=False, features=None):
        """
        Parses stories found in path, returning their trees
        """
        bundle = Bundle.from_path(path, ignored_path=ignored_path,
                                  features=features)
        return bundle.bundle_trees(ebnf=ebnf, lower=lower)

    @staticmethod
    def compile(path, ignored_path=None, ebnf=None, concise=False,
                first=False, features=None):
        """
        Parses and compiles stories found in path, returning JSON
        """
        bundle = Bundle.from_path(path, ignored_path=ignored_path,
                                  features=features)
        result = bundle.bundle(ebnf=ebnf)
        if concise:
            result = _clean_dict(result)
        if first:
            if len(result['stories']) != 1:
                raise StoryError.create_error('first_option_more_stories')
            result = next(iter(result['stories'].values()))
        return json.dumps(result, indent=2)

    @staticmethod
    def lex(path, features, ebnf=None):
        """
        Lex stories, producing the list of used tokens
        """
        return Bundle.from_path(path, features=features).lex(ebnf=ebnf)

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
