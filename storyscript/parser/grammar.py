# -*- coding: utf-8 -*-


class Grammar:
    """
    Advanced EBNF grammar generator that provides for a readable, nicer and
    testable way of creating a grammar.

    A grammar is made by rules and rules are made by combinations of tokens.
    Tokens can be literals or regular expressions.

    Tokens can also be imported from an available grammar, or ignored
    completely, meaning they will not appear in the parsed tree.
    """

    def __init__(self):
        self.start_line = None
        self.tokens_list = []
        self.rules = []
        self.ignores = []
        self.imports = []

    def start(self, rule):
        """
        Produces the start rule
        """
        self.start_line = 'start: {}+'.format(rule)

    def token(self, name, value, priority=None, insensitive=False,
              inline=False, regexp=False):
        """
        Adds a terminal token to the terminals list
        """
        string = '{}: "{}"'
        if regexp:
            string = '{}: {}'
        if priority:
            string = '{}.{}: "{}"'.format('{}', priority, '{}')
        if insensitive:
            string = '{}i'.format(string)
        if inline:
            string = '_{}'.format(string)
        self.tokens_list.append(string.format(name.upper(), value))

    def tokens(self, *args, **kwargs):
        for token_args in args:
            self.token(*token_args, **kwargs)

    def rule(self, name, definitions):
        string = '|'.join(definitions)
        self.rules.append('{}: {}'.format(name, string))

    def ignore(self, terminal):
        self.ignores.append('%ignore {}'.format(terminal))

    def load(self, token):
        self.imports.append('%import common.{}'.format(token))

    def loads(self, tokens):
        for token in tokens:
            self.load(token)

    def build(self):
        rules = '\n'.join(self.rules)
        tokens = '\n'.join(self.tokens_list)
        ignores = '\n'.join(self.ignores)
        imports = '\n'.join(self.imports)
        args = (self.start_line, rules, tokens, ignores, imports)
        return '{}\n{}\n\n{}\n\n{}\n\n{}'.format(*args)
