# -*- coding: utf-8 -*-
from .processingerror import ProcessingError


class CompilerError(ProcessingError):
    """
    A compiler error that occurs despite the syntax being correct, for example
    a return outside of a function.
    """
    pass
