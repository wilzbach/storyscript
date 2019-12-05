# -*- coding: utf-8 -*-
from .DeprecationCodes import DeprecationCodes
from .Diagnostics import Diagnostics


class Deprecation(Diagnostics):
    """
    A deprecation message that is emitted to indicate to developers that
    particular language feature is going to go away in future.
    """
    def __init__(self, deprecation, token=None, tree=None, format_args=None):
        super().__init__(token=token, tree=tree, format_args=format_args)
        self.deprecation = deprecation

    def message(self):
        if DeprecationCodes.is_deprecation(self.deprecation):
            return DeprecationCodes.get_deprecation(self.deprecation)[1].\
                format(**self.format_args)
        else:
            return 'Unknown deprecation message'

    def __str__(self):
        return self.message()


def deprecate(name, tree=None, token=None, **kwargs):
    """
    Return a Deprecation object.

    Params:
        tree: A tree object for positioning
        name: deprecation name for DeprecationCodes
        token: token to use a location for the deprecation message
        kwargs: additional format arguments
    """
    return Deprecation(deprecation=name, token=token,
                       tree=tree, format_args=kwargs)
