# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def line(self, grammar):
        grammar.rule('line', ['values'])

    def grammar(self):
        grammar = Grammar()
        grammar.start('line')
        return grammar.build()

    def parse(self):
        lark = Lark(self.grammar(), parser=self.algo)
        try:
            tree = lark.parse(self.source)
        except UnexpectedToken:
            return None
        return tree
