# -*- coding: utf-8 -*-
import io
import os
import re

from .compiler import Compiler
from .parser import Parser


class Story:

    def __init__(self, story):
        self.story = story

    @staticmethod
    def clean_source(source):
        """
        Cleans a story by removing comments.
        """
        expression = '(?<=###)\s(.*|\\n)+(?=\s###)|#(.*)'
        return re.sub(expression, '', source)

    @classmethod
    def read(cls, path):
        """
        Reads a story
        """
        try:
            with io.open(path, 'r') as file:
                return cls.clean_source(file.read())
        except FileNotFoundError:
            abspath = os.path.abspath(path)
            print('File "{}" not found at {}'.format(path, abspath))
            exit()

    @classmethod
    def from_file(cls, path):
        """
        Creates a story from a file source
        """
        return Story(cls.read(path))

    @staticmethod
    def from_stream(stream):
        """
        Creates a story from a stream source
        """
        return Story(stream.read())

    def parse(self, ebnf=None, debug=False):
        self.tree = Parser(ebnf=ebnf).parse(self.story, debug=debug)

    def modules(self):
        """
        Gets the modules of a story from its tree.
        """
        modules = []
        for module in self.tree.find_data('imports'):
            path = module.string.child(0).value[1:-1]
            if path.endswith('.story') is False:
                path = '{}.story'.format(path)
            modules.append(path)
        return modules

    def compile(self, debug=False):
        self.compiled = Compiler.compile(self.tree, debug=debug)

    def lex(self, ebnf=None):
        return Parser(ebnf=ebnf).lex(self.story)

    def process(self, ebnf=None, debug=False):
        self.parse(ebnf=ebnf, debug=debug)
        self.compile(debug=debug)
        return self.compiled
