# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar
from .indenter import CustomIndenter
from .transformer import Transformer


class Parser:

    def __init__(self, algo='lalr'):
        self.algo = algo
        self.grammar = Grammar()

    def indenter(self):
        return CustomIndenter()

    def transformer(self):
        return Transformer()

    def parse(self, source):
        lark = Lark(self.grammar.build(), parser=self.algo,
                    postlex=self.indenter())
        try:
            tree = lark.parse(source)
        except UnexpectedToken:
            return None
        return self.transformer().transform(tree)
