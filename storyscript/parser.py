# -*- coding: utf-8 -*-
from .grammar import Grammar


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def grammar(self):
        grammar = Grammar()
        grammar.start('line')
        return grammar.build()
