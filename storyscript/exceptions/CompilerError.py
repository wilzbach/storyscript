# -*- coding: utf-8 -*-
from .ProcessingError import ProcessingError


class CompilerError(ProcessingError):
    """
    A compiler error that occurs despite the syntax being correct, for example
    a return outside of a function.
    """
    def __init__(self, error, token=None, tree=None, format_args=None):
        super().__init__(error, token=token, tree=tree,
                         format_args=format_args)
