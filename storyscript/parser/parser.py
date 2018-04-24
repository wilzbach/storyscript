# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar
from .indenter import CustomIndenter


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def add_rules(self, grammar, rules):
        for rule in rules:
            getattr(self, rule)(grammar)

    def line(self, grammar):
        grammar.rule('line', ['values', 'assignments', 'statements',
                              'comment', 'block'])

    def spaces(self, grammar):
        grammar.terminal('WS', '(" ")+', inline=True)
        grammar.terminal('NL', r'/(\r?\n[\t ]*)+/', inline=True)
        grammar.terminal('INDENT', '"<INDENT>"', inline=True)
        grammar.terminal('DEDENT', '"<DEDENT>"', inline=True)

    def block(self, grammar):
        grammar.rule('block', ['line _NL [_INDENT block+ _DEDENT]'])

    def number(self, grammar):
        grammar.rule('number', ['FLOAT', 'INT'])
        grammar.loads(['INT', 'FLOAT'])

    def string(self, grammar):
        grammar.rule('string', ['_STRING_INNER WORD _STRING_INNER',
                                '_DOUBLE_QUOTES WORD _DOUBLE_QUOTES'])
        grammar.terminal('DOUBLE_QUOTES', '("\\\""|/[^"]/)', inline=True)
        grammar.terminal('STRING_INNER', """("\\\'"|/[^']/)""", inline=True)
        grammar.loads(['WORD'])

    def list(self, grammar):
        grammar.rule('list', ['_OSB (values (_COMMA values)*)? _CSB'])
        grammar.terminal('COMMA', '","', inline=True)
        grammar.terminal('OSB', '"["', inline=True)
        grammar.terminal('CSB', '"]"', inline=True)

    def values(self, grammar):
        self.add_rules(grammar, ['number', 'string', 'list'])
        grammar.rule('values', ['number', 'string', 'list'])

    def assignments(self, grammar):
        grammar.rule('assignments', ['WORD EQUALS values'])
        grammar.terminal('equals', '"="')

    def comparisons(self, grammar):
        grammar.terminal('GREATER', '">"')
        grammar.terminal('GREATER_EQUAL', '">="')
        grammar.terminal('LESSER', '"<"')
        grammar.terminal('LESSER_EQUAL', '"<="')
        grammar.terminal('NOT', '"!="')
        grammar.terminal('EQUAL', '"=="')

    def if_statement(self, grammar):
        grammar.rule('if_statement', ['IF _WS WORD'])
        grammar.terminal('IF', '"if"')

    def for_statement(self, grammar):
        grammar.rule('for_statement', ['FOR _WS WORD _WS IN _WS WORD'])
        grammar.terminal('FOR', '"for"')
        grammar.terminal('IN', '"in"')

    def foreach_statement(self, grammar):
        grammar.rule('foreach_statement', ['FOREACH _WS WORD _WS AS _WS WORD'])
        grammar.terminal('FOREACH', '"foreach"')
        grammar.terminal('AS', '"as"')

    def wait_statement(self, grammar):
        grammar.rule('wait_statement', ['WAIT _WS WORD', 'WAIT _WS string'])
        grammar.terminal('WAIT', '"wait"')

    def statements(self, grammar):
        statements = ['if_statement', 'for_statement', 'foreach_statement',
                      'wait_statement']
        self.add_rules(grammar, statements)
        grammar.rule('statements', statements)

    def comment(self, grammar):
        grammar.rule('comment', ['COMMENT'])
        grammar.terminal('COMMENT', '/#(.*)/')

    def grammar(self):
        return Grammar()

    def indenter(self):
        return CustomIndenter()

    def build_grammar(self):
        grammar = self.grammar()
        grammar.start('_NL? block')
        rules = ['line', 'spaces', 'values', 'assignments', 'statements',
                 'comment', 'block', 'comparisons']
        self.add_rules(grammar, rules)
        return grammar.build()

    def parse(self):
        lark = Lark(self.build_grammar(), parser=self.algo,
                    postlex=self.indenter())
        try:
            tree = lark.parse(self.source)
        except UnexpectedToken:
            return None
        return tree
