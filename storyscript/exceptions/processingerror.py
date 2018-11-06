# -*- coding: utf-8 -*-
class ProcessingError(Exception):
    """
    A generic error that occurs while processing a story
    """

    def __init__(self, error, token=None, tree=None):
        self.error = error
        self.token_position(token)
        self.tree_position(tree)

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
