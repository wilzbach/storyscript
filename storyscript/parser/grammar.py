# -*- coding: utf-8 -*-
from .ebnf import Ebnf


class Grammar:

    """
    Defines Storyscript's grammar using the Ebnf module, producing the complete
    EBNF grammar for it.
    """

    def __init__(self):
        self.ebnf = Ebnf()

    def line(self):
        definitions = (['values'], ['operation'], ['comment'], ['statement'],
                       ['block'])
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

    def nested_block(self):
        self.ebnf.rule('nested_block', '_INDENT block+ _DEDENT', raw=True)

    def elseif_statement(self):
        rule = 'ELSE _WS? IF _WS NAME [_WS comparisons _WS NAME]?'
        self.ebnf.rule('elseif_statement', rule, raw=True)

    def elseif_block(self):
        self.nested_block()
        self.elseif_statement()
        definition = ('elseif_statement', 'nl', 'nested_block')
        self.ebnf.rule('elseif_block', definition)

    def else_statement(self):
        self.ebnf.token('else', 'else')
        self.ebnf.rule('else_statement', ['else'])

    def else_block(self):
        self.else_statement()
        self.ebnf.rule('else_block', ('else_statement', 'nl', 'nested_block'))

    def if_statement(self):
        self.ebnf.token('if', 'if')
        definitions = (('if', 'ws', 'name'),
                       ('if', 'ws', 'name', 'ws', 'comparisons', 'ws', 'name'))
        self.ebnf.rules('if_statement', *definitions)

    def if_block(self):
        self.if_statement()
        self.elseif_block()
        self.else_block()
        definition = 'if_statement _NL nested_block elseif_block* else_block?'
        self.ebnf.rule('if_block', definition, raw=True)

    def for_block(self):
        self.for_statement()
        self.foreach_statement()
        definition = '(for_statement|foreach_statement) _NL nested_block'
        self.ebnf.rule('for_block', definition, raw=True)

    def block(self):
        self.if_block()
        self.for_block()
        definition = 'line _NL nested_block?|if_block|for_block'
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
        definition = '_OSB (values (_COMMA _WS? values)*)? _CSB'
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
        self.ebnf.tokens(('plus', '+'), ('dash', '-'), ('multiplier', '*'),
                         ('bslash', '/'))
        definitions = (['plus'], ['dash'], ['multiplier'], ['bslash'])
        self.ebnf.rules('operator', *definitions)

    def operation(self):
        self.operator()
        definitions = (('values', 'ws', 'operator', 'ws', 'values'),
                       ('values', 'operator', 'values'))
        self.ebnf.rules('operation', *definitions)

    def path_fragment(self):
        self.ebnf.token('dot', '.', inline=True)
        definitions = (('dot', 'name'), ('osb', 'int', 'csb'),
                       ('osb', 'string', 'csb'))
        self.ebnf.rules('path_fragment', *definitions)

    def path(self):
        self.ebnf.token('name', '/[a-zA-Z-\/]+/', regexp=True)
        self.path_fragment()
        self.ebnf.rule('path', 'NAME (path_fragment)*', raw=True)

    def assignment_fragment(self):
        self.ebnf.token('equals', '=')
        self.ebnf.rule('assignment_fragment', 'EQUALS _WS? values', raw=True)

    def statement(self):
        self.path()
        self.assignment_fragment()
        self.service_fragment()
        rule = 'path _WS? (service_fragment|assignment_fragment)'
        self.ebnf.rule('statement', rule, raw=True)

    def comparisons(self):
        tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
                  ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
        self.ebnf.tokens(*tokens)
        definitions = (['greater'], ['greater_equal'], ['lesser'],
                       ['lesser_equal'], ['not'], ['equal'])
        self.ebnf.rules('comparisons', *definitions)

    def for_statement(self):
        self.ebnf.tokens(('for', 'for'), ('in', 'in'), inline=True)
        definition = ('for', 'ws', 'name', 'ws', 'in', 'ws', 'name')
        self.ebnf.rule('for_statement', definition)

    def foreach_statement(self):
        self.ebnf.tokens(('foreach', 'foreach'), ('as', 'as'), inline=True)
        definition = ('foreach', 'ws', 'name', 'ws', 'as', 'ws', 'name')
        self.ebnf.rule('foreach_statement', definition)

    def arguments(self):
        self.ebnf.rule('arguments', ('ws', 'name', 'colon', 'values'))

    def command(self):
        self.ebnf.rule('command', ('ws', 'name'))

    def service_fragment(self):
        self.arguments()
        self.command()
        self.ebnf.rule('service_fragment', 'command? arguments*', raw=True)

    def comment(self):
        self.ebnf.token('comment', '/#(.*)/', regexp=True)
        self.ebnf.rule('comment', ['comment'])

    def build(self):
        self.ebnf.start('_NL? block')
        self.line()
        self.spaces()
        self.values()
        self.comparisons()
        self.statement()
        self.operation()
        self.comment()
        self.block()
        return self.ebnf.build()
