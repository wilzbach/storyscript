# -*- coding: utf-8 -*-


class Grammar:

    def __init__(self):
        self.terminals = []
        self.rules = []
        self.ignores = []
        self.imports = []

    def start(self, rule):
        """
        Produces the start rule
        """
        return 'start: {}+'.format(rule)

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

    def build(self):
        return self.start()
