# -*- coding: utf-8 -*-
class ProcessingError(Exception):
    """
    A generic error that occurs while processing a story
    """

    def __init__(self, error, line=None, column=None):
        self.error = error
        self.line = line
        self.column = column
