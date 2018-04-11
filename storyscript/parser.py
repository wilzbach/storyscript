# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def line(self, grammar):
        grammar.rule('line', ['values', 'assignments'])

    def values(self, grammar):
        grammar.rule('values', ['INT', 'STRING_INNER WORD STRING_INNER',
                                'DQS WORD DQS'])
        grammar.terminal('DQS', '("\\\""|/[^"]/)')
        grammar.loads(['common.INT', 'common.WORD', 'common.STRING_INNER'])

    def assignments(self, grammar):
        grammar.rule('assignments', ['WORD EQUALS values'])
        grammar.terminal('equals', '"="')

    def grammar(self):
        grammar = Grammar()
        grammar.start('line')
        self.line(grammar)
        self.values(grammar)
        self.assignments(grammar)
        return grammar.build()

    def parse(self):
        lark = Lark(self.grammar(), parser=self.algo)
        try:
            tree = lark.parse(self.source)
        except UnexpectedToken:
            return None
        return tree
