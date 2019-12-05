# -*- coding: utf-8 -*-
import os
from collections import namedtuple
from functools import lru_cache

from bom_open import bom_open

from lark.exceptions import UnexpectedInput, UnexpectedToken
from lark.lexer import Token

from .compiler import Compiler
from .compiler.lowering import Lowering
from .compiler.pretty.PrettyPrinter import PrettyPrinter
from .exceptions import CompilerError, StoryError, StorySyntaxError
from .exceptions.Deprecation import deprecate
from .exceptions.DeprecationMessage import DeprecationMessage
from .parser import Parser
from .parser.Tree import Tree


Compiled = namedtuple("Compiled", ["results", "deprecations"])


@lru_cache(maxsize=1)
def _parser():
    """
    Cached instance of the parser
    """
    return Parser()


class StoryContext:
    """
    Represents context of a given story.
    """

    def __init__(self, features):
        self.features = features
        self._deprecations = []

    def deprecate(self, tree_or_token, name, **kwargs):
        if isinstance(tree_or_token, Tree):
            deprecation = deprecate(name=name, tree=tree_or_token, **kwargs)
        else:
            assert isinstance(tree_or_token, Token)
            deprecation = deprecate(name=name, token=tree_or_token, **kwargs)
        self._deprecations.append(deprecation)

    def deprecations(self):
        return self._deprecations


class Story:
    """
    Represents a single story and exposes methods for reading, parsing and
    compiling it.
    """

    def __init__(self, story, features, path=None, backend="json", scope=None):
        self.story = story
        self.path = path
        self.lines = story.splitlines(keepends=False)
        self.context = StoryContext(features=features)
        self.backend = backend
        self.scope = scope
        self.name = self.extract_name()

    def extract_name(self):
        """
        Extracts the name of the story from the path.
        """
        if self.path:
            working_directory = os.getcwd()
            if self.path.startswith(working_directory):
                return self.path[len(working_directory) + 1 :]
            return self.path
        return "story"

    @classmethod
    def read(cls, path):
        """
        Reads a story
        """
        has_error = False
        try:
            with bom_open(path, "r") as file:
                r = file.read()
                return r
        except FileNotFoundError:
            has_error = True

        if has_error:
            abspath = os.path.abspath(path)
            raise StoryError.create_error(
                "file_not_found", path=path, abspath=abspath
            )

    @classmethod
    def from_file(cls, path, features):
        """
        Creates a story from a file source
        """
        return Story(cls.read(path), features, path=path)

    @classmethod
    def from_stream(cls, stream, features):
        """
        Creates a story from a stream source
        """
        return Story(stream.read(), features)

    def error(self, error):
        """
        Handles errors by wrapping the real error in a smart StoryError
        """
        return StoryError(error, self)

    def parse(self, parser, lower=False, allow_single_quotes=False):
        """
        Parses the story, storing the tree
        """
        if parser is None:
            parser = self._parser()
        try:
            self.tree = parser.parse(
                self.story, allow_single_quotes=allow_single_quotes
            )
            if lower:
                proc = Lowering(parser, features=self.context.features)
                self.tree = proc.process(self.tree)
        except (CompilerError, StorySyntaxError) as error:
            raise self.error(error) from error
        except UnexpectedToken as error:
            raise self.error(error) from error
        except UnexpectedInput as error:
            raise self.error(error) from error
        return self

    def format(self):
        """
        Pretty prints the story.
        """
        try:
            return PrettyPrinter().compile(self.tree)
        except (CompilerError, StorySyntaxError) as error:
            raise self.error(error) from error

    def compile(self):
        """
        Compiles the story and stores the result.
        """
        try:
            self.compiled = Compiler.compile(
                self.tree, story=self, backend=self.backend, scope=self.scope
            )
        except (CompilerError, StorySyntaxError) as error:
            raise self.error(error) from error

    def lex(self, parser):
        """
        Lexes a story
        """
        if parser is None:
            parser = self._parser()
        return parser.lex(self.story)

    def process(self, parser=None):
        """
        Parse and compile a story, returning the compiled JSON
        """
        if parser is None:
            parser = self._parser()
        self.parse(parser=parser)
        self.compile()
        return self.compiled

    def _parser(self):
        """
        Returns the default Parser instance (cached)
        """
        return _parser()

    def line(self, i):
        """
        Returns a line from the story source.
        Line numbers start with 1.
        """
        if isinstance(i, str):
            if not i.isdigit():
                return None
            i = int(i)
        assert i <= len(self.lines)
        return self.lines[i - 1]

    def deprecations(self):
        """
        Returns a list of deprecations after wrapping it in
        DeprecationMessage which will provide nicely formatted messages.
        """
        return [
            DeprecationMessage(d, self) for d in self.context.deprecations()
        ]
