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

    def token_template(self, value, line, column):
        template = ('Failed reading story because of unexpected "{}" at '
                    'line {}, column {}')
        return template.format(value, line, column)

    def tree_template(self, value, line):
        template = ('Failed reading story because of unexpected "{}" at '
                    'line {}')
        return template.format(value, line)

    def compile_template(self):
        if hasattr(self.item, 'data'):
            return self.tree_template(self.item, self.item.line())
        elif hasattr(self.item, 'token'):
            return self.token_template(self.item.token.value, self.item.line,
                                       self.item.column)
        return self.token_template(self.item, self.item.line, self.item.column)

    def message(self):
        """
        Produces a message for the error, including a reason when provided
        """
        if hasattr(self.item, 'data'):
            message = self.tree_template(self.item, self.item.line())
        else:
            message = self.token_template(self.item, self.item.line,
                                          self.item.column)
        if self.error_type != 'unknown':
            return '{}. Reason: {}'.format(message, self.reason())
        return message

    def __str__(self):
        return self.message()
