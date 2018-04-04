# -*- coding: utf-8 -*-


class Grammar:

    def __init__(self):
        self.terminals = []

    def start(self):
        """
        Produces the start rule
        """
        return 'start:'

    def build(self):
        return self.start()
