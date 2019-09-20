# -*- coding: utf-8 -*-
import click

from .DeprecationCodes import DeprecationCodes
from .Diagnostics import Diagnostics
from .StoryError import StoryError


class WarningDeprecation(Diagnostics):
    """
    A deprecation warning that is emitted to indicate to developers that
    particular language feature is going to go away in future.
    """
    def __init__(self, story, deprecation,
                 token=None, tree=None, format_args=None):
        super().__init__(token=token, tree=tree, format_args=format_args)
        self.deprecation = deprecation
        self.deprecation_tuple = None
        self.story = story
        self.with_color = True
        self.tabwidth = 2

    def int_line(self):
        """
        Gets the deprecation line as an integer
        """
        line = self.line
        if not isinstance(line, int):
            line = int(line.split('.')[0])
        return line

    def get_line(self):
        """
        Gets the deprecation line
        """
        line = self.int_line()
        return self.story.line(line)

    def header(self):
        """
        Creates the header of the message
        """
        name = self.story.name()
        if self.with_color:
            name = click.style(self.story.name(), bold=True)
        text = f'Warning: deprecation warning in ' \
            f'{name} at line {self.int_line()}'
        if self.column != 'None':
            text += f', column {self.column}'
        return text

    def symbols(self, line):
        """
        Creates the repeated symbols that mark the deprecation.
        """
        if self.column != 'None':
            end_column = int(self.column) + 1
            if hasattr(self.deprecation, 'end_column') and \
                    self.end_column != 'None':
                end_column = int(self.end_column)
            start_column = int(self.column)
        else:
            # if the column is not known, start at the first non-whitespace
            # token
            # columns are 1-indexed
            start_column = len(line) - len(line.lstrip()) + 1
            end_column = len(line) + 1

        # add tab offset
        start_column += line.count('\t', 0, start_column) * (self.tabwidth - 1)
        end_column += line.count('\t', 0, end_column) * (self.tabwidth - 1)
        symbols = '^' * (end_column - start_column)

        spaces = ' ' * (start_column + 5)
        highlight = f'{spaces}{symbols}'
        if self.with_color:
            return click.style(highlight, fg='red')
        else:
            return highlight

    def highlight(self):
        """
        Creates the deprecation highlight of the message
        """
        line = self.int_line()
        # replace tabs for consistent deprecation messages
        raw_line = self.get_line()
        untabbed_line = raw_line.replace('\t', ' ' * self.tabwidth)
        highlight = self.symbols(raw_line)
        return '{}|    {}\n{}'.format(line, untabbed_line, highlight)

    def process(self):
        if DeprecationCodes.is_deprecation(self.deprecation):
            self.deprecation_tuple = \
                DeprecationCodes.get_deprecation(self.deprecation)
        else:
            self.deprecation_tuple = DeprecationCodes.unidentified_deprecation

    def deprecation_code(self):
        return self.deprecation_tuple[0]

    def message(self):
        self.process()
        # Check whether the deprecation comes with source information
        if hasattr(self, 'line'):
            args = (self.header(), self.highlight(),
                    self.deprecation_code(), self.hint())
            return '{}\n\n{}\n\n{}: {}'.format(*args)
        else:
            return f'{self.deprecation_code()}: {self.hint()}'

    def hint(self):
        if self.deprecation_tuple == DeprecationCodes.unidentified_deprecation:
            return StoryError._internal_error(self)
        return self.deprecation_tuple[1].format(**self.format_args)

    @classmethod
    def deprecate(cls, story, tree, name, token=None, **kwargs):
        """
        Return a WarningDeprecation object.

        Params:
            tree: A tree object for positioning
            name: deprecation name for DeprecationCodes
            token: token to use a location for the deprecation message
            kwargs: additional format arguments
        """
        return cls(story=story, deprecation=name, token=token,
                   tree=tree, format_args=kwargs)
