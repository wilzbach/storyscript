# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar
from .indenter import CustomIndenter


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def add_rules(self):
        """
        Adds all the rules. Used after the Grammar instance is available
        """
        self.line()
        self.spaces()
        self.values()
        self.assignments()
        self.statements()
        self.comment()
        self.block()
        self.comparisons()

    def line(self):
        rules = ['values', 'assignments', 'statements', 'comment', 'block']
        self.grammar.rule('line', rules)

    def whitespace(self):
        self.grammar.terminal('WS', '(" ")+', inline=True)

    def newline(self):
        self.grammar.terminal('NL', r'/(\r?\n[\t ]*)+/', inline=True)

    def indent(self):
        self.grammar.terminal('INDENT', '"<INDENT>"', inline=True)

    def dedent(self):
        self.grammar.terminal('DEDENT', '"<DEDENT>"', inline=True)

    def spaces(self):
        self.whitespace()
        self.newline()
        self.indent()
        self.dedent()

    def block(self):
        self.grammar.rule('block', ['line _NL [_INDENT block+ _DEDENT]'])

    def number(self):
        self.grammar.rule('number', ['FLOAT', 'INT'])
        self.grammar.loads(['INT', 'FLOAT'])

    def string(self):
        self.grammar.rules('string',
            ('single_quotes', 'word', 'single_quotes'),
            ('double_quotes', 'word', 'double_quotes')
        )
        self.grammar.tokens(('single_quotes', """("\\\'"|/[^']/)"""),
                            ('double_quotes', '("\\\""|/[^"]/)'),
                            inline=True, regexp=True)
        self.grammar.load('WORD')

    def list(self, grammar):
        grammar.rule('list', ['_OSB (values (_COMMA values)*)? _CSB'])
        grammar.terminal('COMMA', '","', inline=True)
        grammar.terminal('OSB', '"["', inline=True)
        grammar.terminal('CSB', '"]"', inline=True)

    def values(self):
        self.number()
        self.string()
        self.list()
        self.grammar.rules('values', ('number'), ('string'), ('list'))

    def assignments(self):
        self.grammar.rule('assignments', ('word', 'equals', 'values'))
        self.grammar.token('equals', '=')

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

    def get_grammar(self):
        return Grammar()

    def indenter(self):
        return CustomIndenter()

    def build_grammar(self):
        self.grammar = self.get_grammar()
        self.grammar.start('_NL? block')
        rules = ['line', 'spaces', 'values', 'assignments', 'statements',
                 'comment', 'block', 'comparisons']
        self.add_rules(self.grammar, rules)
        return self.grammar.build()

    def parse(self):
        lark = Lark(self.build_grammar(), parser=self.algo,
                    postlex=self.indenter())
        try:
            tree = lark.parse(self.source)
        except UnexpectedToken:
            return None
        return tree
