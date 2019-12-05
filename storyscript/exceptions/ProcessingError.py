# -*- coding: utf-8 -*-
from .Diagnostics import Diagnostics
from ..ErrorCodes import ErrorCodes


class ProcessingError(Diagnostics):
    """
    A generic error that occurs while processing a story
    """

    def __init__(self, error, token=None, tree=None, format_args=None):
        super().__init__(token=token, tree=tree, format_args=format_args)
        self.error = error

    def message(self):
        if ErrorCodes.is_error(self.error):
            return ErrorCodes.get_error(self.error)[1].format(
                **self.format_args
            )
        else:
            return "Unknown compiler error"

    def __str__(self):
        return self.message()
