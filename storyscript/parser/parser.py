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
                       ['comment'], ['command'], ['block'])
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
        self.grammar.loads(['int', 'float'])
        self.grammar.rules('number', ['int'], ['float'])

    def string(self):
        tokens = (('single_quoted', "/'([^']*)'/"),
                  ('double_quoted', '/"([^"]*)"/'))
        self.grammar.tokens(*tokens, regexp=True)
        self.grammar.rules('string', ['single_quoted'], ['double_quoted'])

    def boolean(self):
        self.grammar.tokens(('true', 'true'), ('false', 'false'))
        self.grammar.rules('boolean', ['true'], ['false'])

    def filepath(self):
        self.grammar.token('filepath', '/`([^"]*)`/', regexp=True)

    def list(self):
        self.grammar.tokens(('comma', ','), ('osb', '['), ('csb', ']'),
                            inline=True)
        definition = '_OSB (values (_COMMA values)*)? _CSB'
        self.grammar.rule('list', definition, raw=True)

    def values(self):
        self.number()
        self.string()
        self.boolean()
        self.filepath()
        self.list()
        defintions = (['number'], ['string'], ['boolean'], ['filepath'],
                      ['list'])
        self.grammar.rules('values', *defintions)

    def assignments(self):
        self.grammar.load('word')
        self.grammar.token('equals', '=')
        self.grammar.rule('assignments', ('word', 'equals', 'values'))

    def comparisons(self):
        tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
                  ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
        self.grammar.tokens(*tokens)
        definitions = (['greater'], ['greater_equal'], ['lesser'],
                       ['lesser_equal'], ['not'], ['equal'])
        self.grammar.rules('comparisons', *definitions)

    def if_statement(self):
        self.grammar.token('if', 'if')
        self.grammar.rule('if_statement', ('if', 'ws', 'word'))

    def for_statement(self):
        self.grammar.tokens(('for', 'for'), ('in', 'in'))
        definition = ('for', 'ws', 'word', 'ws', 'in', 'ws', 'word')
        self.grammar.rule('for_statement', definition)

    def foreach_statement(self):
        self.grammar.tokens(('foreach', 'foreach'), ('as', 'as'))
        definition = ('foreach', 'ws', 'word', 'ws', 'as', 'ws', 'word')
        self.grammar.rule('foreach_statement', definition)

    def wait_statement(self):
        self.grammar.token('wait', 'wait')
        definitions = (('wait', 'ws', 'word'), ('wait', 'ws', 'string'))
        self.grammar.rules('wait_statement', *definitions)

    def next_statement(self):
        self.grammar.token('next', 'next')
        definitions = (('next', 'ws', 'word'), ('next', 'ws', 'filepath'))
        self.grammar.rules('next_statement', *definitions)

    def statements(self):
        statements = (['if_statement'], ['for_statement'],
                      ['foreach_statement'], ['wait_statement'],
                      ['next_statement'])
        self.if_statement()
        self.for_statement()
        self.foreach_statement()
        self.wait_statement()
        self.next_statement()
        self.grammar.rules('statements', *statements)

    def options(self):
        self.grammar.token('dash', '-')
        definitions = (('dash', 'dash', 'word', 'ws', 'word'),
                       ('dash', 'dash', 'word', 'ws', 'values'))
        self.grammar.rules('options', *definitions)

    def arguments(self):
        self.options()
        definitions = (['ws', 'values'], ['ws', 'word'], ['ws', 'options'])
        self.grammar.rules('arguments', *definitions)

    def command(self):
        self.arguments()
        self.grammar.token('run', 'run')
        rule = 'RUN _WS WORD arguments*|WORD arguments*'
        self.grammar.rule('command', rule, raw=True)

    def comment(self):
        self.grammar.token('comment', '/#(.*)/', regexp=True)
        self.grammar.rule('comment', ['comment'])

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
        self.comparisons()
        self.assignments()
        self.statements()
        self.comment()
        self.block()
        self.command()
        return self.grammar.build()

    def parse(self):
        lark = Lark(self.build_grammar(), parser=self.algo,
                    postlex=self.indenter())
        try:
            tree = lark.parse(self.source)
        except UnexpectedToken:
            return None
        return tree
