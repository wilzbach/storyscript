# -*- coding: utf-8 -*-


class Ebnf:
    """
    Advanced EBNF grammar generator that provides for a readable, nicer and
    testable way of creating a grammar.

    A grammar is made by rules and rules are made by combinations of tokens.
    Tokens can be literals or regular expressions.

    Tokens can also be imported from an available grammar, or ignored
    completely, meaning they will not appear in the parsed tree.
    """

    def __init__(self):
        self._tokens = {}
        self._rules = {}
        self.imports = {}
        self.ignores = []

    def macro(self, name, template):
        """
        Creates a macro with the given name, by creating a method on the
        instance
        """
        def compile_macro(rule):
            return template.format(rule)
        setattr(self, name, compile_macro)

    def set_token(self, name, value):
        self._tokens[name] = value

    def resolve(self, item_name):
        """
        Resolves an item's reference to its real name.
        """
        suffix = None
        if item_name.endswith('?'):
            item_name = item_name[:-1]
            suffix = '?'
        if item_name in self._tokens:
            token = self._tokens[item_name][0].split('.')[0]
            if suffix:
                return '{}{}'.format(token, suffix)
            return token
        if item_name in self.imports:
            return item_name.upper()
        return item_name

    def token(self, name, value, priority=None, insensitive=False,
              inline=False, regexp=False):
        """
        Adds a terminal token to the terminals list
        """
        name_string = name.upper()
        value_string = '"{}"'.format(value)
        if priority:
            name_string = '{}.{}'.format(name_string, priority)
        if inline:
            name_string = '_{}'.format(name_string)
        if regexp:
            value_string = '{}'.format(value)
        if insensitive:
            value_string = '{}i'.format(value_string)
        self._tokens[name] = (name_string, value_string)

    def rule(self, name, definition, raw=False):
        """
        Adds a rule with the given name and definition, which must be an
        iterable of tokens or literals.
        """
        if name not in self._rules:
            self._rules[name] = []
        if raw:
            self._rules[name].append(definition)
            return
        string = ''
        for token in definition:
            string = '{}{} '.format(string, self.resolve(token))
        self._rules[name].append(string[:-1])

    def ignore(self, terminal):
        self.ignores.append('%ignore {}'.format(terminal))

    def load(self, token):
        self.imports[token] = '%import common.{}'.format(token.upper())

    def build_tokens(self):
        string = ''
        for name, token in self._tokens.items():
            string += '{}: {}\n'.format(token[0], token[1])
        return string

    def build_rules(self):
        string = ''
        for name, definitions in self._rules.items():
            string += '{}: {}\n'.format(name, '\n\t| '.join(definitions))
        return string

    def build(self):
        tokens = self.build_tokens()
        rules = self.build_rules()
        ignores = '\n'.join(self.ignores)
        imports = '\n'.join(self.imports.values())
        args = (self.start_line, rules, tokens, ignores, imports)
        return '{}\n{}\n{}\n{}\n\n{}'.format(*args)
