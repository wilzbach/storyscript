# -*- coding: utf-8 -*-


class StoryError(SyntaxError):

    """
    Handles errors related to the story, such as unrecognized tokens, syntax
    errors and so on.  Supports both trees and tokens as error items.
    """

    reasons = {
        'unknown': 'unknown',
        'service-path': ('Service names can only contain alphanumeric ,'
                         'characters dashes and backslashes.'),
        'variables-backslash': "Variable names can't contain backslashes",
        'variables-dash': "Variable names can't contain dashes",
        'return-outside': "Return can't be used outside functions",
        'arguments-noservice': 'Missing service before service arguments'
    }

    def __init__(self, error_type, item):
        self.error_type = error_type
        self.item = item

    def reason(self):
        """
        Provides a reason for error.
        """
        return self.reasons[self.error_type]

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
        if self.error_type != 'unknown':
            return '{}. Reason: {}'.format(message, self.reason())
        return message

    def __str__(self):
        return self.pretty()
