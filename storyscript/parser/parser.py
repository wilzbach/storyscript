# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .ebnf import Ebnf
from .grammar import Grammar
from .indenter import CustomIndenter


class Parser:

    def __init__(self, algo='lalr'):
        self.algo = algo
        self.grammar = Grammar()

    def indenter(self):
        return CustomIndenter()

    def parse(self, source):
        lark = Lark(self.grammar.build(), parser=self.algo,
                    postlex=self.indenter())
        try:
            tree = lark.parse(source)
        except UnexpectedToken:
            return None
        return tree
