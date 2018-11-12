# -*- coding: utf-8 -*-
from .ProcessingError import ProcessingError


class StorySyntaxError(ProcessingError):
    """
    A syntax error, like an incomplete structure or a typo.
    """
