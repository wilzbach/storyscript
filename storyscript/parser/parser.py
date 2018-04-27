# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .grammar import Grammar
from .indenter import CustomIndenter


class Parser:

    def __init__(self, source, algo='lalr'):
        self.source = source
        self.algo = algo

    def line(self):
        definitions = (['values'], ['assignments'],[ 'statements'],
                       ['comment'], ['block'])
        self.grammar.rules('line', *definitions)

    def whitespaces(self):
        tokens = (('ws', '(" ")+'), ('nl', r'/(\r?\n[\t ]*)+/'))
        self.grammar.tokens(*tokens, inline=True, regexp=True)

    def indentation(self):
        tokens = (('indent', '<INDENT>'), ('dedent', '<DEDENT>'))
        self.grammar.tokens(*tokens, inline=True)

    def spaces(self):
        self.whitespaces()
        self.indentation()

    def block(self):
        definition = 'line _NL [_INDENT block+ _DEDENT]'
        self.grammar.rule('block', definition, raw=True)

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

    def list(self):
        definition = ('osb', '(values', '(comma', 'values)*)?', 'csb')
        self.grammar.rule('list', definition)
        self.grammar.tokens(('comma', ','), ('osb', '['), ('csb', ']'),
                            inline=True)

    def values(self):
        self.number()
        self.string()
        self.list()
        self.grammar.rules('values', ['number'], ['string'], ['list'])

    def assignments(self):
        self.grammar.rule('assignments', ('word', 'equals', 'values'))
        self.grammar.token('equals', '=')

    def comparisons(self):
        tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
                  ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
        self.grammar.tokens(*tokens)

    def if_statement(self):
        self.grammar.rule('if_statement', ('if', 'ws', 'word'))
        self.grammar.token('if', 'if')

    def for_statement(self):
        definition = ('for', 'ws', 'word', 'in', 'ws', 'word')
        self.grammar.rule('for_statement', definition)
        self.grammar.tokens(('for', 'for'), ('in', 'in'))

    def foreach_statement(self):
        definition = ('foreach', 'ws', 'word', 'ws', 'as', 'ws', 'word')
        self.grammar.rule('foreach_statement', definition)
        self.grammar.tokens(('foreach', 'foreach'), ('as', 'as'))

    def wait_statement(self):
        definitions = (('wait', 'ws', 'word'), ('wait', 'ws', 'string'))
        self.grammar.rules('wait_statement', *definitions)
        self.grammar.token('wait', 'wait')

    def statements(self):
        statements = (['if_statement'], ['for_statement'],
                      ['foreach_statement'], ['wait_statement'])
        self.if_statement()
        self.for_statement()
        self.foreach_statement()
        self.wait_statement()
        self.grammar.rules('statements', *statements)

    def comment(self):
        self.grammar.rule('comment', ('comment'))
        self.grammar.token('comment', '/#(.*)/', regexp=True)

    def get_grammar(self):
        return Grammar()

    def indenter(self):
        return CustomIndenter()

    def build_grammar(self):
        self.grammar = self.get_grammar()
        self.grammar.start('_NL? block')
        self.line()
        self.spaces()
        self.values()
        self.assignments()
        self.statements()
        self.comment()
        self.block()
        self.comparisons()
        return self.grammar.build()

    def parse(self):
        lark = Lark(self.build_grammar(), parser=self.algo,
                    postlex=self.indenter())
        try:
            tree = lark.parse(self.source)
        except UnexpectedToken:
            return None
        return tree
