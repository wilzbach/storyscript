# -*- coding: utf-8 -*-
from .ProcessingError import ProcessingError
from ..ErrorCodes import ErrorCodes


class CompilerError(ProcessingError):
    """
    A compiler error that occurs despite the syntax being correct, for example
    a return outside of a function.
    """
    def __init__(self, error, token=None, tree=None, message=''):
        super().__init__(error, token=token, tree=tree)
        self._message = message

    def __str__(self):
        if len(self._message) > 0:
            return self._message
        elif hasattr(self, 'error') and ErrorCodes.is_error(self.error):
            return ErrorCodes.get_error(self.error)[1]
        else:
            return 'Unknown compiler error'

    def message(self):
        return str(self)
