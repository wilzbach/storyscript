# -*- coding: utf-8 -*-


class StoryscriptSyntaxError(SyntaxError):

    """
    Handles syntax errors and provides useful output about them. It supports
    both trees and tokens as error items.
    """

    def __init__(self, error_type, item):
        self.error_type = error_type
        self.item = item

    def reason(self):
        """
        Provides a reason for error.
        """
        reasons = [
            'unknown',
            ('Service names can only contain alphanumeric characters, '
             'dashes and backslashes.'),
            "Variable names can't contain backslashes",
            "Variable names can't contain dashes",
            "Return can't be used outside functions",
            "Missing service before service arguments"
        ]
        return reasons[self.error_type]

    def __str__(self):
        """
        Print a message for the item, checking whether it's a tree or a token,
        using the reason that matches the error type.
        """
        if hasattr(self.item, 'data'):
            return '{} at line {}'.format(self.reason(), self.item.line())
        message = '"{}" not allowed at line {}, column {}.\n\n> {}'
        return message.format(self.item, self.item.line, self.item.column,
                              self.reason())
