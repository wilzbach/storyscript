# -*- coding: utf-8 -*-


class StoryscriptSyntaxError(SyntaxError):

    def __init__(self, error_type, token):
        self.error_type = error_type
        self.token = token

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
        message = '"{}" not allowed at line {}, column {}.\n\n{}'
        return message.format(self.token, self.token.line, self.token.column,
                              self.reason())
