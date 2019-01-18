# -*- coding: utf-8 -*-
from .ProcessingError import ProcessingError
from ..ErrorCodes import ErrorCodes


class ConstDict:
    """
    Like a dict, but as constant attributes
    """

    def __init__(self, data):
        self.data = data

    def __getattr__(self, attr):
        return self.data[attr]


class CompilerError(ProcessingError):
    """
    A compiler error that occurs despite the syntax being correct, for example
    a return outside of a function.
    """
    def __init__(self, error, token=None, tree=None, message='', **kwargs):
        super().__init__(error, token=token, tree=tree)
        self._message = message
        self.extra = ConstDict(kwargs)

    def __str__(self):
        if len(self._message) > 0:
            return self._message
        elif hasattr(self, 'error') and ErrorCodes.is_error(self.error):
            return ErrorCodes.get_error(self.error)[1]
        else:
            return 'Unknown compiler error'

    def message(self):
        return str(self)
