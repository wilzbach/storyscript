# -*- coding: utf-8 -*-
from .DeprecationCodes import DeprecationCodes
from .ErrorTextFormatter import ErrorTextFormatter


class DeprecationMessage(ErrorTextFormatter):
    """
    A deprecation message that is emitted to indicate to developers that
    particular language feature is going to go away in future.
    """
    def __init__(self, deprecation, story):
        super().__init__(deprecation, story)

    def header(self):
        text = 'Deprecation: deprecated syntax in {name} at line {line}'
        return self._format_header(text)

    def process(self):
        if DeprecationCodes.is_deprecation(self.error.deprecation):
            self.error_tuple = \
                DeprecationCodes.get_deprecation(self.error.deprecation)
        else:
            self.error_tuple = DeprecationCodes.unidentified_deprecation

    def hint(self):
        if self.error_tuple == DeprecationCodes.unidentified_deprecation:
            return self._internal_error(self)
        return self.error_tuple[1].format(**self.error.format_args)
