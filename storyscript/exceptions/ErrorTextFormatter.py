# -*- coding: utf-8 -*-
import click


class ErrorTextFormatter:
    """
    Handles formatting for errors, deprecations.
    """

    def __init__(self, error, story):
        self.error = error
        self.story = story
        self.error_tuple = None
        self.with_color = True
        self.tabwidth = 2

    def int_line(self):
        """
        Gets the error line as an integer
        """
        line = self.error.line
        if not isinstance(line, int):
            line = int(line.split('.')[0])
        return line

    def get_line(self):
        """
        Gets the error line
        """
        line = self.int_line()
        return self.story.line(line)

    def _format_header(self, text):
        """
        Creates the header of the message

        Params:
            text: A formatted python string to be used to create
                the header. It is to accept `name` and `line` as
                keyword arguments.
        """
        name = self.story.name
        if self.with_color:
            name = click.style(self.story.name, bold=True)
        text = text.format(name=name, line=self.int_line())
        if self.error.column != 'None':
            text += f', column {self.error.column}'
        return text

    def symbols(self, line):
        """
        Creates the repeated symbols that mark the error.
        """
        if self.error.column != 'None':
            end_column = int(self.error.column) + 1
            if hasattr(self.error, 'end_column') and \
                    self.error.end_column != 'None':
                end_column = int(self.error.end_column)
            start_column = int(self.error.column)
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
        Creates the error highlight of the message
        """
        line = self.int_line()
        # replace tabs for consistent error messages
        raw_line = self.get_line()
        untabbed_line = raw_line.replace('\t', ' ' * self.tabwidth)
        highlight = self.symbols(raw_line)
        return '{}|    {}\n{}'.format(line, untabbed_line, highlight)

    def error_code(self):
        """
        Provides the error code for the current error.
        """
        return self.error_tuple[0]

    def hint(self):
        """
        Provides an hint for the current error.
        """
        raise NotImplementedError()

    def process(self):
        """
        Process the error, assigning the error code and performing other
        operations when necessary.
        """
        raise NotImplementedError()

    def message(self):
        """
        Creates a friendly error message.
        """
        self.process()
        # Check whether the error comes with source information
        if hasattr(self.error, 'line'):
            args = (self.header(), self.highlight(),
                    self.error_code(), self.hint())
            return '{}\n\n{}\n\n{}: {}'.format(*args)
        else:
            return f'{self.error_code()}: {self.hint()}'

    def short_message(self):
        """
        A short version of the error message
        """
        self.process()
        return f'{self.error_code()}: {self.hint()}'

    def echo(self):
        """
        Prints the message
        """
        click.echo(self.message())

    @staticmethod
    def _internal_error(error):
        """
        Creates the error message for an internal error.
        """
        url = 'https://github.com/storyscript/storyscript/issues'
        return ('Internal error occured: {error}\n'
                'Please report at {url}').format(error=str(error), url=url)
