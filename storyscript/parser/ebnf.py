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
        self._imports = {}
        self._ignores = []

    def macro(self, name, template):
        """
        Creates a macro with the given name, by creating a method on the
        instance
        """
        def compile_macro(rule):
            return template.format(rule)
        setattr(self, name, compile_macro)

    def set_token(self, name, value):
        """
        Registers a token under a simplified name, and keep the original name,
        the value and the real token
        """
        token = name.split('.')[0]
        token_name = token.lower()
        if token_name.startswith('_'):
            token_name = token_name[1:]

        token_value = '"{}"'.format(value)
        if len(value) > 2:
            if value.startswith('/'):
                if value.endswith('/'):
                    token_value = value
        dictionary = {'name': name, 'value': token_value, 'token': token}
        self._tokens[token_name] = dictionary

    def resolve(self, name):
        """
        Resolves a name to its real value if it's a token, or leave it as it
        is.
        """
        clean_name = name.strip('*[]()?')
        if clean_name in self._tokens:
            real_name = self._tokens[clean_name]['token']
        else:
            real_name = clean_name
        return name.replace(clean_name, real_name)

    def set_rule(self, name, value):
        """
        Registers a rule, transforming tokens to their identifiers.
        """
        rule = ''
        for shard in value.split():
            rule = '{} {}'.format(rule, self.resolve(shard))
        self._rules[name] = rule.strip()

    def ignore(self, terminal):
        self._ignores.append('%ignore {}'.format(terminal))

    def load(self, token):
        self._imports[token] = '%import common.{}'.format(token.upper())

    def build_tokens(self):
        """
        Build the tokens that have been defined into a string
        """
        string = ''
        for name, value in self._tokens.items():
            string = '{}{}: {}\n'.format(string, value['name'], value['value'])
        return string

    def build_rules(self):
        """
        Build the rules that have been defined into a string
        """
        string = ''
        for name, value in self._rules.items():
            string = '{}{}: {}\n'.format(string, name, value)
        return string

    def build(self):
        """
        Build the grammar
        """
        tokens = self.build_tokens()
        rules = self.build_rules()
        ignores = '\n'.join(self._ignores)
        imports = '\n'.join(self._imports.values())
        return '{}\n{}\n{}\n\n{}'.format(rules, tokens, ignores, imports)

    def __setattr__(self, name, value):
        if isinstance(value, str):
            if name.isupper():
                return self.set_token(name, value)
            return self.set_rule(name, value)
        object.__setattr__(self, name, value)
