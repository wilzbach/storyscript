# -*- coding: utf-8 -*-


class ConstDict:
    """
    Like a dict, but with constant attributes.
    """

    def __init__(self, data):
        self._data = data

    def __getattr__(self, attr):
        return self._data[attr]

    def __getitem__(self, item):
        return self._data[item]

    def keys(self):
        return self._data.keys()


class Diagnostics(Exception):
    """
    This is for holding basic information around an error/deprecation
    that would help construct useful formatted messages for the user.
    """

    def __init__(self, token=None, tree=None, format_args=None):
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
            pos = tree.position()
            self.line = pos.line
            self.column = pos.column
            self.end_column = pos.end_column
