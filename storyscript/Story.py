# -*- coding: utf-8 -*-
import io
import os

from lark.exceptions import UnexpectedInput, UnexpectedToken

from .compiler import Compiler
from .exceptions import CompilerError, StoryError, StorySyntaxError
from .parser import Parser


class Story:
    """
    Represents a single story and exposes methods for reading, parsing and
    compiling it.
    """

    def __init__(self, story, path=None):
        self.story = story
        self.path = path

    @classmethod
    def read(cls, path):
        """
        Reads a story
        """
        has_error = False
        try:
            with io.open(path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            has_error = True

        if has_error:
            abspath = os.path.abspath(path)
            raise StoryError.create_error('file_not_found', path=path,
                                          abspath=abspath)

    @classmethod
    def from_file(cls, path):
        """
        Creates a story from a file source
        """
        return Story(cls.read(path), path=path)

    @classmethod
    def from_stream(cls, stream):
        """
        Creates a story from a stream source
        """
        return Story(stream.read())

    def error(self, error):
        """
        Handles errors by wrapping the real error in a smart StoryError
        """
        return StoryError(error, self.story, path=self.path)

    def parse(self, ebnf=None):
        """
        Parses the story, storing the tree
        """
        parser = Parser(ebnf=ebnf)
        e = None
        try:
            self.tree = parser.parse(self.story)
        except StorySyntaxError as error:
            e = self.error(error)
        except UnexpectedToken as error:
            e = self.error(error)
        except UnexpectedInput as error:
            e = self.error(error)
        if e is not None:
            raise e

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

    def compile(self):
        """
        Compiles the story and stores the result.
        """
        e = None
        try:
            self.compiled = Compiler.compile(self.tree)
        except (CompilerError, StorySyntaxError) as error:
            e = self.error(error)
        if e is not None:
            raise e

    def lex(self, ebnf=None):
        """
        Lexes a story
        """
        return Parser(ebnf=ebnf).lex(self.story)

    def process(self, ebnf=None):
        """
        Parse and compile a story, returning the compiled JSON
        """
        self.parse(ebnf=ebnf)
        self.compile()
        return self.compiled
