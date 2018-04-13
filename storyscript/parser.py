# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def line(self, grammar):
        grammar.rule('line', ['values', 'assignments', 'statements'])

    def string(self, grammar):
        grammar.rule('string', ['STRING_INNER WORD STRING_INNER',
                                'DOUBLE_QUOTES WORD DOUBLE_QUOTES'])
        grammar.terminal('DOUBLE_QUOTES', '("\\\""|/[^"]/)')
        grammar.loads(['common.WORD', 'common.STRING_INNER'])

    def list(self, grammar):
        grammar.rule('list', ['OSB (values (COMMA values)*)? CSB'])
        grammar.terminal('COMMA', '","')
        grammar.terminal('OSB', '"["')
        grammar.terminal('CSB', '"]"')

    def values(self, grammar):
        grammar.rule('values', ['INT', 'string', 'list'])
        grammar.loads(['common.INT'])

    def assignments(self, grammar):
        grammar.rule('assignments', ['WORD EQUALS values'])
        grammar.terminal('equals', '"="')

    def if_statement(self, grammar):
        grammar.rule('if_statement', ['IF WS WORD'])
        grammar.terminal('IF', '"if"')
        grammar.load('common.WS')

    def for_statement(self, grammar):
        grammar.rule('for_statement', ['FOR WS WORD WS IN WS WORD'])
        grammar.terminal('FOR', '"for"')
        grammar.terminal('IN', '"in"')

    def foreach_statement(self, grammar):
        grammar.rule('foreach_statement', ['FOREACH WS WORD WS AS WS WORD'])
        grammar.terminal('FOREACH', '"foreach"')
        grammar.terminal('AS', '"as"')

    def wait_statement(self, grammar):
        grammar.rule('wait_statement', ['WAIT WS WORD', 'WAIT WS string'])
        grammar.terminal('WAIT', '"wait"')

    def statements(self, grammar):
        grammar.rule('statements', ['if_statement', 'for_statement',
                                    'foreach_statement', 'wait_statement'])

    def grammar(self):
        grammar = Grammar()
        grammar.start('line')
        for rule in ['line', 'string', 'values', 'list', 'assignments',
                     'if_statement', 'for_statement', 'foreach_statement',
                     'wait_statement', 'statements']:
            getattr(self, rule)(grammar)
        return grammar.build()

    def parse(self):
        lark = Lark(self.grammar(), parser=self.algo)
        try:
            tree = lark.parse(self.source)
        except UnexpectedToken:
            return None
        return tree
