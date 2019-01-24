# -*- coding: utf-8 -*-


class InternalCompilerError(BaseException):
    """
    An internal compiler error is unrecoverable and fatal.
    It should never happen for any user input.
    """

    def __init__(self, message=''):
        self.message = message
        pass

    def __str__(self):
        return self.message


def internal_assert(a, b=None):
    """
    Make assertions about the compiler logic.
    Their failure will result in a hard InternalCompilerError.
    """
    if b is None:
        if not a:
            message = 'Internal Error'
            raise InternalCompilerError(message)
    elif a != b:
        message = f'{str(a)} != {str(b)}'
        raise InternalCompilerError(message)
