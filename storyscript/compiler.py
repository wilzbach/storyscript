# -*- coding: utf-8 -*-
from .version import version


class Compiler:

    """
    Compiles Storyscript abstract syntax tree to JSON.
    """

    @staticmethod
    def assignment(tree):
        return {
            'method': 'set',
            'ln': str(tree.node('path').children[0].line),
            'container': None,
            'args': [
                {'$OBJECT': 'path', 'paths': [
                 tree.node('path').child(0).value]},
                {'$OBJECT': 'string',
                 'string': tree.child(2).node('string').child(0).value[1:-1]}
            ],
            'output': None,
            'enter': None,
            'exit': None
        }

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
