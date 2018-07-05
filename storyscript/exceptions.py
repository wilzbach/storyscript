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
            'Missing service before service arguments'
        ]
        return reasons[self.error_type]

    def token_message(self, value, line, column):
        template = ('Failed reading story because of unexpected "{}" at '
                    'line {}, column {}')
        return template.format(value, line, column)

    def tree_message(self, value, line):
        template = ('Failed reading story because of unexpected "{}" at '
                    'line {}')
        return template.format(value, line)

    def pretty(self):
        """
        Returns a message for the item, using the reason that matches the
        error type.
        """
        if hasattr(self.item, 'data'):
            message = self.tree_message(self.item, self.item.line())
        else:
            message = self.token_message(self.item, self.item.line,
                                         self.item.column)
        return message

    def __str__(self):
        return self.pretty()
