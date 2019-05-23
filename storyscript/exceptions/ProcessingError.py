# -*- coding: utf-8 -*-
from ..ErrorCodes import ErrorCodes


class ConstDict:
    """
    Like a dict, but with constant attributes
    """

    def __init__(self, data):
        self._data = data

    def __getattr__(self, attr):
        return self._data[attr]

    def __getitem__(self, item):
        return self._data[item]

    def keys(self):
        return self._data.keys()


class ProcessingError(Exception):
    """
    A generic error that occurs while processing a story
    """

    def __init__(self, error, token=None, tree=None, format_args=None):
        self.error = error
        self.token_position(token)
        self.tree_position(tree)
        if format_args is None:
            self.format_args = {}
        else:
            self.format_args = format_args
        self.format_args = ConstDict(self.format_args)

    def token_position(self, token):
        """
        Extracts the position from a token.
        """
        if token:
            self.line = token.line
            self.column = token.column
            self.end_column = token.end_column

    def tree_position(self, tree):
        """
        Extracts the position from a tree.
        """
        if tree:
            self.line = tree.line()
            self.column = tree.column()
            self.end_column = tree.end_column()

    def message(self):
        if ErrorCodes.is_error(self.error):
            return ErrorCodes.get_error(self.error)[1].format(
                **self.format_args)
        else:
            return 'Unknown compiler error'

    def __str__(self):
        return self.message()
