# -*- coding: utf-8 -*-


class StoryError(SyntaxError):

    """
    Handles errors related to the story, such as unrecognized tokens, syntax
    errors and so on.  Supports trees, tokens and lark errors as items.
    """

    reasons = {
        'service-path': ('Service names can only contain alphanumeric ,'
                         'characters dashes and backslashes.'),
        'variables-backslash': "Variable names can't contain backslashes",
        'variables-dash': "Variable names can't contain dashes",
        'return-outside': "Return can't be used outside functions",
        'arguments-noservice': 'Missing service before service arguments'
    }

    def __init__(self, error_type, item, path=None):
        self.error_type = error_type
        self.item = item
        self.path = path

    @staticmethod
    def escape_string(string):
        return string.encode('unicode_escape').decode('utf-8')

    def reason(self):
        """
        Provides a reason for error.
        """
        if self.error_type in self.reasons:
            return self.reasons[self.error_type]
        return 'unknown'

    def name(self):
        """
        Formats the name of the story, or just 'story'
        """
        if self.path:
            return 'story "{}"'.format(self.path)
        return 'story'

    def token_template(self, value, line, column):
        template = ('Failed reading story because of unexpected "{}" at '
                    'line {}, column {}')
        return template.format(value, line, column)

    def tree_template(self, value, line):
        template = ('Failed reading story because of unexpected "{}" at '
                    'line {}')
        return template.format(value, line)

    def compile_template(self):
        """
        Compiles the correct template for the item, depending on whether it's
        UnexpectedToken, UnexpectedInput, a tree, a dict or a token.
        """
        if hasattr(self.item, 'data'):
            return self.tree_template(self.item, self.item.line())
        elif hasattr(self.item, 'token'):
            return self.token_template(self.item.token.value, self.item.line,
                                       self.item.column)
        elif hasattr(self.item, 'context'):
            return self.token_template(self.item.context, self.item.line,
                                       self.item.column)
        elif isinstance(self.item, dict):
            return self.tree_template(self.item['value'], self.item['line'])
        return self.token_template(self.item, self.item.line, self.item.column)

    def message(self):
        """
        Produces a message for the error, including a reason when provided
        """
        message = self.escape_string(self.compile_template())
        if self.error_type != 'unknown':
            return '{}. Reason: {}'.format(message, self.reason())
        return message

    def __str__(self):
        return self.message()
