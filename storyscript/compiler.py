# -*- coding: utf-8 -*-
from .version import version


class Compiler:

    """
    Compiles Storyscript abstract syntax tree to JSON.
    """

    @staticmethod
    def command(tree):
        dictionary = {
            'method': 'run',
            'ln': tree.children[0].line,
            'container': tree.children[0].value,
            'args': None,
            'output': None,
            'enter': None,
            'exit': None
        }
        return dictionary

    @classmethod
    def parse_tree(cls, tree):
        return {}

    @staticmethod
    def compile(tree):
        dictionary = {'script': Compiler.parse_tree(tree), 'version': version}
        return dictionary
