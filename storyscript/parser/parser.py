# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from .ebnf import Ebnf
from .indenter import CustomIndenter


class Parser:

    def __init__(self, algo='lalr'):
        self.algo = algo

    def line(self):
        definitions = (['values'], ['assignments'], ['operation'],
                       ['statements'], ['comment'], ['command'], ['block'])
        self.ebnf.rules('line', *definitions)

    def whitespaces(self):
        tokens = (('ws', '(" ")+'), ('nl', r'/(\r?\n[\t ]*)+/'))
        self.ebnf.tokens(*tokens, inline=True, regexp=True)

    def indentation(self):
        tokens = (('indent', '<INDENT>'), ('dedent', '<DEDENT>'))
        self.ebnf.tokens(*tokens, inline=True)

    def spaces(self):
        self.whitespaces()
        self.indentation()

    def block(self):
        definition = 'line _NL [_INDENT block+ _DEDENT]'
        self.ebnf.rule('block', definition, raw=True)

    def number(self):
        self.ebnf.loads(['int', 'float'])
        self.ebnf.rules('number', ['int'], ['float'])

    def string(self):
        tokens = (('single_quoted', "/'([^']*)'/"),
                  ('double_quoted', '/"([^"]*)"/'))
        self.ebnf.tokens(*tokens, regexp=True)
        self.ebnf.rules('string', ['single_quoted'], ['double_quoted'])

    def boolean(self):
        self.ebnf.tokens(('true', 'true'), ('false', 'false'))
        self.ebnf.rules('boolean', ['true'], ['false'])

    def filepath(self):
        self.ebnf.token('filepath', '/`([^"]*)`/', regexp=True)

    def list(self):
        self.ebnf.tokens(('comma', ','), ('osb', '['), ('csb', ']'),
                            inline=True)
        definition = '_OSB (values (_COMMA values)*)? _CSB'
        self.ebnf.rule('list', definition, raw=True)

    def key_value(self):
        self.ebnf.token('colon', ':', inline=True)
        self.ebnf.rule('key_value', ('string', 'colon', 'values'))

    def objects(self):
        self.key_value()
        self.ebnf.tokens(('ocb', '{'), ('ccb', '}'), inline=True)
        rule = '_OCB (key_value (_COMMA key_value)*)? _CCB'
        self.ebnf.rule('objects', rule, raw=True)

    def values(self):
        self.number()
        self.string()
        self.boolean()
        self.filepath()
        self.list()
        self.objects()
        defintions = (['number'], ['string'], ['boolean'], ['filepath'],
                      ['list'], ['objects'])
        self.ebnf.rules('values', *defintions)

    def operator(self):
        self.ebnf.tokens(('plus', '+'), ('minus', '-'), ('multiplier', '*'),
                         ('division', '/'))
        definitions = (['plus'], ['minus'], ['multiplier'], ['division'])
        self.ebnf.rules('operator', *definitions)

    def operation(self):
        self.operator()
        definitions = (('values', 'ws', 'operator', 'ws', 'values'),
                       ('values', 'operator', 'values'))
        self.ebnf.rules('operation', *definitions)

    def path_fragment(self):
        self.ebnf.load('word')
        self.ebnf.token('dot', '.',inline=True)
        definitions = (('dot', 'word'), ('osb', 'int', 'csb'),
                       ('osb', 'string', 'csb'))
        self.ebnf.rules('path_fragment', *definitions)

    def path(self):
        self.path_fragment()
        self.ebnf.rule('path', 'WORD (path_fragment)*', raw=True)

    def assignments(self):
        self.path()
        self.ebnf.token('equals', '=')
        self.ebnf.rule('assignments', ('path', 'equals', 'values'))

    def comparisons(self):
        tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
                  ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
        self.ebnf.tokens(*tokens)
        definitions = (['greater'], ['greater_equal'], ['lesser'],
                       ['lesser_equal'], ['not'], ['equal'])
        self.ebnf.rules('comparisons', *definitions)

    def if_statement(self):
        self.ebnf.token('if', 'if')
        definitions = (('if', 'ws', 'word'),
                       ('if', 'ws', 'word', 'ws', 'comparisons', 'ws', 'word'))
        self.ebnf.rules('if_statement', *definitions)

    def else_statement(self):
        self.ebnf.token('else', 'else')
        self.ebnf.rule('else_statement', ['else'])

    def elseif_statement(self):
        rule = 'ELSE _WS? IF _WS WORD [_WS comparisons _WS WORD]?'
        self.ebnf.rule('elseif_statement', rule, raw=True)

    def for_statement(self):
        self.ebnf.tokens(('for', 'for'), ('in', 'in'))
        definition = ('for', 'ws', 'word', 'ws', 'in', 'ws', 'word')
        self.ebnf.rule('for_statement', definition)

    def foreach_statement(self):
        self.ebnf.tokens(('foreach', 'foreach'), ('as', 'as'))
        definition = ('foreach', 'ws', 'word', 'ws', 'as', 'ws', 'word')
        self.ebnf.rule('foreach_statement', definition)

    def wait_statement(self):
        self.ebnf.token('wait', 'wait')
        definitions = (('wait', 'ws', 'word'), ('wait', 'ws', 'string'))
        self.ebnf.rules('wait_statement', *definitions)

    def next_statement(self):
        self.ebnf.token('next', 'next')
        definitions = (('next', 'ws', 'word'), ('next', 'ws', 'filepath'))
        self.ebnf.rules('next_statement', *definitions)

    def statements(self):
        """
        Defines all possible statements. Statements must be followed by an
        indented block.
        """
        statements = (['if_statement'], ['for_statement'],
                      ['foreach_statement'], ['wait_statement'],
                      ['next_statement'], ['else_statement'],
                      ['elseif_statement'])
        self.if_statement()
        self.else_statement()
        self.elseif_statement()
        self.for_statement()
        self.foreach_statement()
        self.wait_statement()
        self.next_statement()
        self.ebnf.rules('statements', *statements)

    def options(self):
        self.ebnf.token('dash', '-')
        definitions = (('dash', 'dash', 'word', 'ws', 'word'),
                       ('dash', 'dash', 'word', 'ws', 'values'))
        self.ebnf.rules('options', *definitions)

    def arguments(self):
        self.options()
        definitions = (['ws', 'values'], ['ws', 'word'], ['ws', 'options'])
        self.ebnf.rules('arguments', *definitions)

    def command(self):
        self.arguments()
        self.ebnf.token('run', 'run')
        rule = 'RUN _WS WORD arguments*|WORD arguments*'
        self.ebnf.rule('command', rule, raw=True)

    def comment(self):
        self.ebnf.token('comment', '/#(.*)/', regexp=True)
        self.ebnf.rule('comment', ['comment'])

    def get_ebnf(self):
        return Ebnf()

    def indenter(self):
        return CustomIndenter()

    def build_grammar(self):
        self.ebnf = self.get_ebnf()
        self.ebnf.start('_NL? block')
        self.line()
        self.spaces()
        self.values()
        self.comparisons()
        self.assignments()
        self.operation()
        self.statements()
        self.comment()
        self.block()
        self.command()
        return self.ebnf.build()

    def parse(self, source):
        lark = Lark(self.build_grammar(), parser=self.algo,
                    postlex=self.indenter())
        try:
            tree = lark.parse(source)
        except UnexpectedToken:
            return None
        return tree
