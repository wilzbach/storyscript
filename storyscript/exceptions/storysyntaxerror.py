# -*- coding: utf-8 -*-
from .processingerror import ProcessingError


class StorySyntaxError(ProcessingError):
    """
    A syntax error, like an incomplete structure or a typo.
    """

    def set_position(self, line, column):
        self.line = line
        self.column = column
