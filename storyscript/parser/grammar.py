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
        definitions = (['values'], ['assignments'], ['operation'],
                       ['comment'], ['command'], ['block'])
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
        self.ebnf.token('name', '/[a-zA-Z]+/', regexp=True)
        self.path_fragment()
        self.ebnf.rule('path', 'NAME (path_fragment)*', raw=True)

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
        definitions = (('if', 'ws', 'name'),
                       ('if', 'ws', 'name', 'ws', 'comparisons', 'ws', 'name'))
        self.ebnf.rules('if_statement', *definitions)

    def else_statement(self):
        self.ebnf.token('else', 'else')
        self.ebnf.rule('else_statement', ['else'])

    def elseif_statement(self):
        rule = 'ELSE _WS? IF _WS NAME [_WS comparisons _WS NAME]?'
        self.ebnf.rule('elseif_statement', rule, raw=True)

    def for_statement(self):
        self.ebnf.tokens(('for', 'for'), ('in', 'in'))
        definition = ('for', 'ws', 'name', 'ws', 'in', 'ws', 'name')
        self.ebnf.rule('for_statement', definition)

    def foreach_statement(self):
        self.ebnf.tokens(('foreach', 'foreach'), ('as', 'as'))
        definition = ('foreach', 'ws', 'name', 'ws', 'as', 'ws', 'name')
        self.ebnf.rule('foreach_statement', definition)

    def wait_statement(self):
        self.ebnf.token('wait', 'wait')
        definitions = (('wait', 'ws', 'name'), ('wait', 'ws', 'string'))
        self.ebnf.rules('wait_statement', *definitions)

    def next_statement(self):
        self.ebnf.token('next', 'next')
        definitions = (('next', 'ws', 'name'), ('next', 'ws', 'filepath'))
        self.ebnf.rules('next_statement', *definitions)

    def options(self):
        definitions = (('dash', 'dash', 'name', 'ws', 'name'),
                       ('dash', 'dash', 'name', 'ws', 'values'))
        self.ebnf.rules('options', *definitions)

    def arguments(self):
        self.options()
        definitions = (['ws', 'values'], ['ws', 'name'], ['ws', 'options'])
        self.ebnf.rules('arguments', *definitions)

    def container(self):
        self.ebnf.rules('container', *(['name'], ['dash'], ['bslash']))

    def command(self):
        self.arguments()
        self.container()
        self.ebnf.rule('command', 'container+ arguments*', raw=True)

    def comment(self):
        self.ebnf.token('comment', '/#(.*)/', regexp=True)
        self.ebnf.rule('comment', ['comment'])

    def build(self):
        self.ebnf.start('_NL? block')
        self.line()
        self.spaces()
        self.values()
        self.comparisons()
        self.assignments()
        self.operation()
        self.comment()
        self.block()
        self.command()
        return self.ebnf.build()
