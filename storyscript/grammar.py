# -*- coding: utf-8 -*-


class Grammar:

    def __init__(self):
        self.terminals = []
        self.rules = []

    def start(self):
        """
        Produces the start rule
        """
        return 'start:'

    def terminal(self, name, value):
        """
        Adds a terminal token to the terminals list
        """
        self.terminals.append('{}: {}'.format(name, value))
    def build(self):
        return self.start()
