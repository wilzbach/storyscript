# -*- coding: utf-8 -*-
from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from .CompilerError import CompilerError
from .ErrorTextFormatter import ErrorTextFormatter
from .ProcessingError import ProcessingError
from ..ErrorCodes import ErrorCodes
from ..Intention import Intention


class StoryError(ErrorTextFormatter, SyntaxError):

    """
    Handles story-related errors (reading, parsing, compiling), transforming
    raw errors in nice and helpful messages.
    """

    def __init__(self, error, story):
        super().__init__(error, story)

    def header(self):
        text = 'Error: syntax error in {name} at line {line}'
        return self._format_header(text)

    def hint(self):
        """
        Provides an hint for the current error.
        """
        if self.error_tuple == ErrorCodes.unidentified_error:
            return StoryError._internal_error(self.error)

        # Not every error originates from a ProcessingError
        # (we also catch Lark's errors)
        if isinstance(self.error, ProcessingError):
            return self.error.message()

        # We might have added formatting attributes to a Lark error
        values = getattr(self, '_format', {})
        return self.error_tuple[1].format(**values)

    def unexpected_token_code(self):
        """
        Finds the error code when the error is UnexpectedToken
        """
        intention = Intention(self.get_line())
        token = self.error.token

        if self.error.expected == ['_CP']:
            if token.type == '_AS':
                return ErrorCodes.service_no_inline_output
            self._format = {'cp': ')'}
            return ErrorCodes.expected_closing_parenthesis

        if intention.unnecessary_colon():
            return ErrorCodes.unnecessary_colon
        elif self.error.expected == ['_INDENT']:
            return ErrorCodes.block_expected_after
        elif self.error.expected == ['_DEDENT']:
            return ErrorCodes.expected_closing_block
        elif self.error.expected == ['_COLON']:
            return ErrorCodes.arguments_expected
        elif self.error.token == 'as':
            return ErrorCodes.assignment_no_as
        elif intention.assignment():
            return ErrorCodes.assignment_incomplete

        self._format = {'allowed': str(self.error.expected)}
        if token.type == '_NL':
            return ErrorCodes.unexpected_end_of_line

        self._format['token'] = str(token)
        if len(self.error.expected) == 1 and \
                self.error.expected[0] == '_NL':
            return ErrorCodes.expected_end_of_line

        return ErrorCodes.unexpected_token

    @staticmethod
    def is_valid_name_start(char):
        """
        Checks whether a character token is a valid start of a name
        """
        return char.isalpha() or char == '_'

    def unexpected_characters_code(self):
        """
        Finds the error code when the error is UnexpectedCharacters
        """
        line = self.get_line()
        error_column = line[self.error.column - 1]
        intention = Intention(line)
        if intention.is_function():
            return ErrorCodes.function_misspell
        elif intention.unnecessary_colon():
            return ErrorCodes.unnecessary_colon
        elif error_column == "'":
            return ErrorCodes.single_quotes
        elif error_column == '\t':
            return ErrorCodes.tabs
        elif self.error.allowed is None and \
                self.is_valid_name_start(error_column):
            return ErrorCodes.block_expected_before

        self._format = {'character': error_column}
        return ErrorCodes.invalid_character

    def identify(self):
        """
        Identifies the error.
        """
        if hasattr(self.error, 'error'):
            if not isinstance(self.error.error, str):
                return ErrorCodes.unidentified_error
            if ErrorCodes.is_error(self.error.error):
                return ErrorCodes.get_error(self.error.error)

        if isinstance(self.error, UnexpectedToken):
            return self.unexpected_token_code()
        elif isinstance(self.error, UnexpectedCharacters):
            return self.unexpected_characters_code()
        return ErrorCodes.unidentified_error

    def process(self):
        """
        Process the error, assigning the error code and performing other
        operations when necessary.
        """
        self.error_tuple = self.identify()

    @staticmethod
    def create_error(error_code, **kwargs):
        """
        Builds a compiler error with 'error_code' and all other arguments
        as its format parameters.
        """
        return StoryError(CompilerError(error_code, format_args=kwargs), None)

    @staticmethod
    def internal_error(error):
        """
        Builds an internal error.
        """
        return StoryError(error, story=None)
