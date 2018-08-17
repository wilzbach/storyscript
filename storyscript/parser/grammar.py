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
        definitions = (['values'], ['absolute_expression'], ['comment'],
                       ['assignment'], ['imports'], ['return_statement'],
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
        rule = ('_ELSE _WS? _IF _WS path_value '
                '(_WS comparisons _WS path_value)?')
        self.ebnf.rule('elseif_statement', rule, raw=True)

    def elseif_block(self):
        self.nested_block()
        self.elseif_statement()
        definition = ('elseif_statement', 'nl', 'nested_block')
        self.ebnf.rule('elseif_block', definition)

    def else_statement(self):
        self.ebnf.token('else', 'else', inline=True)
        self.ebnf.rule('else_statement', ['else'])

    def else_block(self):
        self.else_statement()
        self.ebnf.rule('else_block', ('else_statement', 'nl', 'nested_block'))

    def path_value(self):
        self.ebnf.rules('path_value', *(['path'], ['values']))

    def if_statement(self):
        self.path_value()
        self.ebnf.token('if', 'if', inline=True)
        rule = '_IF _WS path_value (_WS comparisons _WS path_value)?'
        self.ebnf.rule('if_statement', rule, raw=True)

    def if_block(self):
        self.if_statement()
        self.elseif_block()
        self.else_block()
        definition = 'if_statement _NL nested_block elseif_block* else_block?'
        self.ebnf.rule('if_block', definition, raw=True)

    def foreach_block(self):
        self.foreach_statement()
        definition = 'foreach_statement _NL nested_block'
        self.ebnf.rule('foreach_block', definition, raw=True)

    def typed_argument(self):
        self.ebnf.rule('typed_argument', ('name', 'colon', 'types'))

    def function_argument(self):
        self.typed_argument()
        self.ebnf.rule('function_argument', ('ws', 'typed_argument'))

    def function_output(self):
        self.ebnf.token('returns', 'returns', inline=True)
        self.ebnf.rule('function_output', ('ws', 'returns', 'ws', 'types'))

    def function_statement(self):
        self.function_argument()
        self.function_output()
        rule = 'FUNCTION_TYPE _WS NAME function_argument* function_output?'
        self.ebnf.rule('function_statement', rule, raw=True)

    def function_block(self):
        self.function_statement()
        rule = ('function_statement', 'nl', 'nested_block')
        self.ebnf.rule('function_block', rule)

    def inline_expression(self):
        self.ebnf.tokens(('op', '('), ('cp', ')'), inline=True)
        self.ebnf.rule('inline_expression', ('op', 'service', 'cp'))

    def arguments(self):
        self.inline_expression()
        rule = '_WS? NAME? _COLON (values|path|inline_expression)'
        self.ebnf.rule('arguments', rule, raw=True)

    def command(self):
        self.ebnf.rule('command', ('ws', 'name'))

    def output(self):
        rule = '(_WS _AS _WS NAME (_COMMA _WS? NAME)*)'
        self.ebnf.rule('output', rule, raw=True)

    def service_fragment(self):
        self.arguments()
        self.command()
        self.output()
        rule = '(command arguments*|arguments+) output?'
        self.ebnf.rule('service_fragment', rule, raw=True)

    def service(self):
        self.service_fragment()
        self.ebnf.rule('service', ('path', 'service_fragment'))

    def service_block(self):
        self.service()
        rule = 'service _NL (nested_block)?'
        self.ebnf.rule('service_block', rule, raw=True)

    def when_block(self):
        self.ebnf.token('when', 'when', inline=True)
        rule = '_WHEN _WS (path output|service) _NL nested_block'
        self.ebnf.rule('when_block', rule, raw=True)

    def block(self):
        self.if_block()
        self.foreach_block()
        self.function_block()
        self.service_block()
        self.when_block()
        definition = ('line _NL|if_block|foreach_block|function_block'
                      '|arguments|service_block|when_block')
        self.ebnf.rule('block', definition, raw=True)

    def number(self):
        tokens = (('int', '"0".."9"+'),
                  ('float', """INT "." INT? | "." INT"""))
        self.ebnf.tokens(*tokens, regexp=True, priority=2)
        self.ebnf.rules('number', ['int'], ['float'])

    def string(self):
        tokens = (('single_quoted', "/'([^']*)'/"),
                  ('double_quoted', '/"([^"]*)"/'))
        self.ebnf.tokens(*tokens, regexp=True)
        self.ebnf.rules('string', ['single_quoted'], ['double_quoted'])

    def boolean(self):
        self.ebnf.tokens(('true', 'true'), ('false', 'false'))
        self.ebnf.rules('boolean', ['true'], ['false'])

    def list(self):
        self.ebnf.tokens(('comma', ','), ('osb', '['), ('csb', ']'),
                         inline=True)
        definition = ('_OSB (_NL _INDENT)? (values (_COMMA (_WS|_NL)? '
                      'values)*)? (_NL _DEDENT)? _CSB')
        self.ebnf.rule('list', definition, raw=True)

    def key_value(self):
        self.ebnf.token('colon', ':', inline=True)
        rule = 'string _COLON _WS? (values|path)'
        self.ebnf.rule('key_value', rule, raw=True)

    def objects(self):
        self.key_value()
        self.ebnf.tokens(('ocb', '{'), ('ccb', '}'), inline=True)
        rule = '_OCB (key_value (_COMMA _WS? key_value)*)? _CCB'
        self.ebnf.rule('objects', rule, raw=True)

    def values(self):
        self.number()
        self.string()
        self.boolean()
        self.list()
        self.objects()
        rules = (['number'], ['string'], ['boolean'], ['list'], ['objects'])
        self.ebnf.rules('values', *rules)

    def operator(self):
        self.ebnf.tokens(('plus', '+'), ('dash', '-'), ('multiplier', '*'),
                         ('bslash', '/'))
        definitions = (['plus'], ['dash'], ['multiplier'], ['bslash'])
        self.ebnf.rules('operator', *definitions)

    def mutation(self):
        mutation = '_WS NAME arguments*'
        self.ebnf.rule('mutation', mutation, raw=True)

    def expression(self):
        self.operator()
        self.mutation()
        definitions = (('values', 'ws', 'operator', 'ws', 'values'),
                       ('values', 'operator', 'values'),
                       ('values', 'mutation'))
        self.ebnf.rules('expression', *definitions)

    def absolute_expression(self):
        """
        An expression on its own line. This is necessary for the compiler to
        understand how to compile an expression.
        """
        self.expression()
        self.ebnf.rule('absolute_expression', ['expression'])

    def path_fragment(self):
        self.ebnf.token('dot', '.', inline=True)
        definitions = (('dot', 'name'), ('osb', 'int', 'csb'),
                       ('osb', 'string', 'csb'))
        self.ebnf.rules('path_fragment', *definitions)

    def path(self):
        self.ebnf.token('name', '/[a-zA-Z-\/_0-9]+/', regexp=True, priority=1)
        self.path_fragment()
        self.ebnf.rule('path', 'NAME (path_fragment)*', raw=True)

    def assignment_fragment(self):
        self.ebnf.token('equals', '=')
        rule = 'EQUALS _WS? (values|expression|path|service)'
        self.ebnf.rule('assignment_fragment', rule, raw=True)

    def assignment(self):
        self.path()
        self.assignment_fragment()
        self.ebnf.rule('assignment', ('path', 'ws?', 'assignment_fragment'))

    def imports(self):
        self.ebnf.token('import', 'import', inline=True)
        rule = ('import', 'ws', 'string', 'ws', 'as', 'ws', 'name')
        self.ebnf.rule('imports', rule)

    def comparisons(self):
        tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
                  ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
        self.ebnf.tokens(*tokens)
        definitions = (['greater'], ['greater_equal'], ['lesser'],
                       ['lesser_equal'], ['not'], ['equal'])
        self.ebnf.rules('comparisons', *definitions)

    def foreach_statement(self):
        self.ebnf.tokens(('foreach', 'foreach'), ('as', 'as'), inline=True)
        definition = ('foreach', 'ws', 'name', 'output')
        self.ebnf.rule('foreach_statement', definition)

    def return_statement(self):
        self.ebnf.token('return', 'return', inline=True)
        rule = '_RETURN _WS (path|values)'
        self.ebnf.rule('return_statement', rule, raw=True)

    def int_type(self):
        self.ebnf.token('int_type', 'int')

    def float_type(self):
        self.ebnf.token('float_type', 'float')

    def number_type(self):
        self.ebnf.token('number_type', 'number')

    def string_type(self):
        self.ebnf.token('string_type', 'string')

    def list_type(self):
        self.ebnf.token('list_type', 'list')

    def object_type(self):
        self.ebnf.token('object_type', 'object')

    def regexp_type(self):
        self.ebnf.token('regexp_type', 'regexp')

    def function_type(self):
        self.ebnf.token('function_type', 'function')

    def types(self):
        self.int_type()
        self.float_type()
        self.number_type()
        self.string_type()
        self.list_type()
        self.object_type()
        self.regexp_type()
        self.function_type()
        definitions = (['int_type'], ['float_type'], ['string_type'],
                       ['list_type'], ['object_type'], ['regexp_type'],
                       ['function_type'])
        self.ebnf.rules('types', *definitions)

    def comment(self):
        token = '/(?<=###)\s(.*|\\n)+(?=\s###)|#(.*)/'
        self.ebnf.token('comment', token, regexp=True)
        self.ebnf.rule('comment', 'COMMENT+', raw=True)

    def build(self):
        self.ebnf.start('_NL? block')
        self.line()
        self.spaces()
        self.values()
        self.comparisons()
        self.assignment()
        self.return_statement()
        self.absolute_expression()
        self.block()
        self.imports()
        self.types()
        self.comment()
        return self.ebnf.build()
