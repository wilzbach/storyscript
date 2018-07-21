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
    def compile(cls, path, ebnf_file=None, debug=False):
        """
        Parse and compile stories in path to JSON
        """
        bundle = Bundle(path).bundle(ebnf_file=ebnf_file, debug=debug)
        return json.dumps(bundle, indent=2)

    @classmethod
    def lex(cls, path):
        """
        Lex stories, producing the list of used tokens
        """
        stories = Bundle(path).find_stories()
        results = {}
        for story in stories:
            results[story] = Story.from_file(story).lex()
        return results

    @staticmethod
    def grammar():
        """
        Returns the current grammar
        """
        return Grammar().build()
