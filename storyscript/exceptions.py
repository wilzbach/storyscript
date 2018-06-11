# -*- coding: utf-8 -*-


class StoryscriptSyntaxError(SyntaxError):

    """
    Handles syntax errors and provides useful output about them.
    """

    def __init__(self, error_type, item):
        self.error_type = error_type
        self.item = item

    def reason(self):
        reasons = [
            'unknown',
            ('Service names can only contain alphanumeric characters, '
             'dashes and backslashes.'),
            "Variable names can't contain backslashes",
            "Variable names can't contain dashes",
            "Return can't be used outside functions"
        ]
        return reasons[self.error_type]

    def __str__(self):
        if hasattr(self.item, 'data'):
            return '{} at line {}'.format(self.reason(), self.item.line())
        message = '"{}" not allowed at line {}, column {}.\n\n> {}'
        return message.format(self.item, self.item.line, self.item.column,
                              self.reason())
