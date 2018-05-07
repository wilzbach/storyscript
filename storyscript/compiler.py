# -*- coding: utf-8 -*-
from .version import version


class Compiler:

    """
    Compiles Storyscript abstract syntax tree to JSON.
    """

    @staticmethod
    def compile(tree):
        dictionary = {'script': {}, 'version': version}
        return dictionary
