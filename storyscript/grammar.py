# -*- coding: utf-8 -*-


class Grammar:

    def __init__(self):
        self.start_line = None
        self.terminals = []
        self.rules = []
        self.ignores = []
        self.imports = []

    def start(self, rule):
        """
        Produces the start rule
        """
        self.start_line = 'start: {}+'.format(rule)

    def terminal(self, name, value, priority=None, insensitive=False):
        """
        Adds a terminal token to the terminals list
        """
        string = '{}: {}'
        if priority:
            string = '{}.{}: {}'.format('{}', priority, '{}')
        if insensitive:
            string = '{}i'.format(string)
        self.terminals.append(string.format(name.upper(), value))

    def rule(self, name, definitions):
        string = '|'.join(definitions)
        self.rules.append('{}: {}'.format(name, string))

    def ignore(self, terminal):
        self.ignores.append('%ignore {}'.format(terminal))

    def load(self, terminal):
        self.imports.append('%import {}'.format(terminal))

    def loads(self, terminals):
        for terminal in terminals:
            self.load(terminal)

    def build(self):
        rules = '\n'.join(self.rules)
        terminals = '\n'.join(self.terminals)
        ignores = '\n'.join(self.ignores)
        imports = '\n'.join(self.imports)
        args = (self.start_line, rules, terminals, ignores, imports)
        return '{}\n{}\n{}\n{}\n{}'.format(*args)
