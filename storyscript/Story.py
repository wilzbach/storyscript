# -*- coding: utf-8 -*-
import io
import os
import re

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
        self.story = self.clean_source(story)
        self.path = path

    @staticmethod
    def remove_comments(source):
        """
        Removes inline comments from source.
        """
        return re.sub(r'#[^#\n]+', '', source)

    @staticmethod
    def delete_line(match):
        """
        Clears the contents of a line.
        """
        return re.sub(r'.*', '', match.group())

    @classmethod
    def clean_source(cls, source):
        """
        Cleans a story by removing all comments.
        """
        return re.sub(
            r'###[^#]+###', cls.delete_line, cls.remove_comments(source)
        )

    @classmethod
    def read(cls, path):
        """
        Reads a story
        """
        msg = None
        try:
            with io.open(path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            abspath = os.path.abspath(path)
            msg = 'File "{}" not found at {}'.format(path, abspath)

        if msg is not None:
            raise StoryError.unnamed_error(msg)

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
