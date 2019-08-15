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


def expect(cond, error, token, **kwargs):
    """
    Throws a compiler error with message if the condition is falsy.

    Args:
        cond: condition on whether to raise an error
        error: error message to raise
        token: token to use a location for the error message
        kwargs: additional format arguments
    """
    if not cond:
        raise CompilerError(error, token=token, format_args=kwargs)
