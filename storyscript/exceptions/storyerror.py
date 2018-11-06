# -*- coding: utf-8 -*-
import os


class StoryError(SyntaxError):

    """
    Handles story-related errors (reading, parsing, compiling), transforming
    raw errors in nice and helpful messages.
    """

    def __init__(self, error, story, path=None):
        self.error = error
        self.story = story
        self.path = path

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
        template = 'Error: **syntax error** in {} at line {}, column {}'
        return template.format(self.name(), self.error.line, self.error.column)

    def symbols(self):
        """
        Creates the repeated symbols that mark the error.
        """
        end_column = int(self.error.column) + 1
        if hasattr(self.error, 'end_column'):
            end_column = int(self.error.end_column)
        return '^' * (end_column - int(self.error.column))

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
        if hasattr(self.error, 'error'):
            if self.error.error == 'service-name':
                return "A service name can't contain `.`"
            elif self.error.error == 'arguments-noservice':
                return 'You have defined an argument, but not a service'
            elif self.error.error == 'return-outside':
                return '`return` is allowed only inside functions'
            elif self.error.error == 'variables-backslash':
                return "A variable name can't contain `/`"
            elif self.error.error == 'variables-dash':
                return "A variable name can't contain `-`"
        return ''

    def message(self):
        """
        Creates a friendly error message.
        """
        args = (self.header(), self.highlight(), self.hint())
        return '{}\n\n{}\n\n{}'.format(*args)

    def echo(self):
        """
        Prints the message
        """
        print(self.message())
