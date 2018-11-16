# -*- coding: utf-8 -*-
import os

import click

from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from ..ErrorCodes import ErrorCodes
from ..Intention import Intention


class StoryError(SyntaxError):

    """
    Handles story-related errors (reading, parsing, compiling), transforming
    raw errors in nice and helpful messages.
    """

    def __init__(self, error, story, path=None):
        self.error = error
        self.story = story
        self.path = path
        self.error_code = None

    def name(self):
        """
        Extracts the name of the story from the path.
        """
        if self.path:
            working_directory = os.getcwd()
            if self.path.startswith(working_directory):
                return self.path[len(working_directory) + 1:]
            return self.path
        return 'story'

    def get_line(self):
        """
        Gets the error line
        """
        return self.story.splitlines(keepends=False)[int(self.error.line) - 1]

    def header(self):
        """
        Creates the header of the message
        """
        template = 'Error: syntax error in {} at line {}, column {}'
        name = click.style(self.name(), bold=True)
        return template.format(name, self.error.line, self.error.column)

    def symbols(self):
        """
        Creates the repeated symbols that mark the error.
        """
        end_column = int(self.error.column) + 1
        if hasattr(self.error, 'end_column'):
            end_column = int(self.error.end_column)
        symbols = '^' * (end_column - int(self.error.column))
        return click.style(symbols, fg='red')

    def highlight(self):
        """
        Creates the error highlight of the message
        """
        spaces = ' ' * (int(self.error.column) + 5)
        highlight = '{}{}'.format(spaces, self.symbols())
        line = self.error.line
        return '{}|    {}\n{}'.format(line, self.get_line(), highlight)

    def hint(self):
        """
        Provides an hint for the current error.
        """
        return self.error_code[1]

    def identify(self):
        """
        Identifies the error.
        """
        if hasattr(self.error, 'error'):
            if hasattr(ErrorCodes, self.error.error):
                return getattr(ErrorCodes, self.error.error)

        intention = Intention(self.get_line())
        if isinstance(self.error, UnexpectedToken):
            if intention.assignment():
                return ErrorCodes.incomplete_assignment
        elif isinstance(self.error, UnexpectedCharacters):
            if intention.is_function():
                return ErrorCodes.misspelt_function
        return ErrorCodes.unidentified_error

    def process(self):
        """
        Process the error, assigning the error code and performing other
        operations when necessary.
        """
        self.error_code = self.identify()

    def message(self):
        """
        Creates a friendly error message.
        """
        self.process()
        args = (self.header(), self.highlight(), self.hint())
        return '{}\n\n{}\n\n{}'.format(*args)

    def echo(self):
        """
        Prints the message
        """
        click.echo(self.message())
