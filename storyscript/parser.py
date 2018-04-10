# -*- coding: utf-8 -*-
from lark import Lark

from .grammar import Grammar


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def grammar(self):
        grammar = Grammar()
        grammar.start('line')
        return grammar.build()

    def parse(self):
        lark = Lark(self.grammar())
        return lark.parse()
