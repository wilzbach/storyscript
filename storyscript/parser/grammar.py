# -*- coding: utf-8 -*-
from .ebnf import Ebnf


class Grammar:

    """
    Defines Storyscript's grammar using the Ebnf module, producing the complete
    EBNF grammar for it.
    """

    def __init__(self):
        self.ebnf = Ebnf()

    def rules(self):
        definitions = (['values'], ['absolute_expression'], ['assignment'],
                       ['imports'], ['return_statement'], ['block'])
        self.ebnf.rules('rules', *definitions)

    def whitespaces(self):
        tokens = (('ws', '(" ")+'), ('nl', r'/(\r?\n[\t ]*)+/'))
        self.ebnf.tokens(*tokens, inline=True, regexp=True)
        self.ebnf.ignore('_WS')

    def indentation(self):
        tokens = (('indent', '<INDENT>'), ('dedent', '<DEDENT>'))
        self.ebnf.tokens(*tokens, inline=True)

    def spaces(self):
        self.whitespaces()
        self.indentation()

    def nested_block(self):
        self.ebnf.rule('nested_block', '_INDENT block+ _DEDENT', raw=True)

    def elseif_statement(self):
        rule = ('_ELSE _IF path_value '
                '(comparisons path_value)?')
        self.ebnf.rule('elseif_statement', rule, raw=True)

    def elseif_block(self):
        self.nested_block()
        self.elseif_statement()
        definition = ('elseif_statement', 'nl', 'nested_block')
        self.ebnf.rule('elseif_block', definition)

    def else_statement(self):
        self.ebnf.token('else', 'else', inline=True)
        self.ebnf.rule('!else_statement', ['else'])

    def else_block(self):
        self.else_statement()
        self.ebnf.rule('else_block', ('else_statement', 'nl', 'nested_block'))

    def path_value(self):
        self.ebnf.rules('path_value', *(['path'], ['values']))

    def if_statement(self):
        self.path_value()
        self.ebnf.token('if', 'if', inline=True)
        rule = '_IF path_value (comparisons path_value)?'
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

    def function_output(self):
        self.ebnf.token('returns', 'returns', inline=True)
        self.ebnf.rule('function_output', ('returns', 'types'))

    def function_statement(self):
        self.typed_argument()
        self.function_output()
        rule = 'FUNCTION_TYPE NAME typed_argument* function_output?'
        self.ebnf.rule('function_statement', rule, raw=True)

    def function_block(self):
        self.function_statement()
        rule = ('function_statement', 'nl', 'nested_block')
        self.ebnf.rule('function_block', rule)

    def inline_expression(self):
        self.ebnf.tokens(('op', '('), ('cp', ')'), inline=True)
        self.ebnf.rule('inline_expression', ('op', 'service', 'cp'))

    def service_block(self):
        self.service()
        rule = 'service _NL (nested_block)?'
        self.ebnf.rule('service_block', rule, raw=True)

    def when_block(self):
        self.ebnf.token('when', 'when', inline=True)
        rule = '_WHEN (path output|service) _NL nested_block'
        self.ebnf.rule('when_block', rule, raw=True)

    def block(self):
        self.if_block()
        self.foreach_block()
        self.function_block()
        self.service_block()
        self.when_block()
        definition = ('rules _NL|if_block|foreach_block|function_block'
                      '|arguments|service_block|when_block')
        self.ebnf.rule('block', definition, raw=True)

    def operator(self):
        self.ebnf.tokens(('plus', '+'), ('dash', '-'), ('multiplier', '*'),
                         ('bslash', '/'))
        definitions = (['plus'], ['dash'], ['multiplier'], ['bslash'])
        self.ebnf.rules('operator', *definitions)

    def mutation(self):
        mutation = 'NAME arguments*'
        self.ebnf.rule('mutation', mutation, raw=True)
    def macros(self):
        """
        Define the macros
        """
        collection = '{} (nl indent)? ({} (comma nl? {})*)? (nl dedent)? {}'
        self.ebnf.macro('collection', collection)
        self.ebnf.macro('simple_block', '{} nl nested_block')

    def expression(self):
        self.operator()
        self.mutation()
        definitions = (('values', 'operator', 'values'),
                       ('values', 'operator', 'values'),
                       ('values', 'mutation'))
        self.ebnf.rules('expression', *definitions)

    def absolute_expression(self):
    def types(self):
        """
        An expression on its own line. This is necessary for the compiler to
        understand how to compile an expression.
        Defines available types
        """
        self.expression()
        self.ebnf.rule('absolute_expression', ['expression'])
    def comparisons(self):
        tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
                  ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
        self.ebnf.tokens(*tokens)
        definitions = (['greater'], ['greater_equal'], ['lesser'],
                       ['lesser_equal'], ['not'], ['equal'])
        self.ebnf.rules('comparisons', *definitions)

    def foreach_statement(self):
        self.ebnf.tokens(('foreach', 'foreach'), ('as', 'as'), inline=True)
        definition = ('foreach', 'name', 'output')
        self.ebnf.rule('foreach_statement', definition)

    def return_statement(self):
        self.ebnf.token('return', 'return', inline=True)
        rule = '_RETURN (path|values)'
        self.ebnf.rule('return_statement', rule, raw=True)

        self.ebnf.INT_TYPE = 'int'
        self.ebnf.FLOAT_TYPE = 'float'
        self.ebnf.NUMBER_TYPE = 'number'
        self.ebnf.STRING_TYPE = 'string'
        self.ebnf.LIST_TYPE = 'list'
        self.ebnf.OBJECT_TYPE = 'object'
        self.ebnf.REGEXP_TYPE = 'regex'
        self.ebnf.FUNCTION_TYPE = 'function'
        rule = ('int_type, float_type, number_type, string_type, list_type, '
                'object_type, regexp_type, function_type')
        self.ebnf.types = rule

    def values(self):
        self.ebnf.TRUE = 'true'
        self.ebnf.FALSE = 'false'
        self.ebnf.set_token('INT.2', '"0".."9"+')
        self.ebnf.set_token('FLOAT.2', 'INT "." INT? | "." INT')
        self.ebnf.SINGLE_QUOTED = "/'([^']*)'/"
        self.ebnf.DOUBLE_QUOTED = '/"([^"]*)"/'
        self.ebnf._OSB = '['
        self.ebnf._CSB = ']'
        self.ebnf._OCB = '{'
        self.ebnf._CCB = '}'
        self.ebnf._COLON = ':'
        self.ebnf._COMMA = ','
        self.ebnf._OP = '('
        self.ebnf._CP = ')'
        self.ebnf.boolean = 'true, false'
        self.ebnf.number = 'int, float'
        self.ebnf.string = 'single_quoted, double_quoted'
        list = self.ebnf.collection('osb', 'values', 'values', 'csb')
        self.ebnf.set_rule('!list', list)
        self.ebnf.key_value = '(string, path) colon (values, path)'
        objects = 'ocb', 'key_value', 'key_value', 'ccb'
        self.ebnf.objects = self.ebnf.collection(objects)
        self.ebnf.inline_expression = 'op service cp'
        values = 'number, string, boolean, list, objects, inline_expression'
        self.ebnf.values = values

    def assignments(self):
        self.ebnf.EQUALS = '='
        self.ebnf.set_token('NAME.1', '/[a-zA-Z-\/_0-9]+/')
        path_fragment = 'dot name, osb int csb, osb string csb, osb path csb'
        self.ebnf.path_fragment = path_fragment
        self.ebnf.path = 'name (path_fragment)*'
        assignment_fragment = 'equals (values, expression, path, service)'
        self.ebnf.assignment_fragment = assignment_fragment
        self.ebnf.assignment = 'path assignment_fragment'

    def imports(self):
        self.ebnf._AS = 'as'
        self.ebnf._IMPORT = 'import'
        self.ebnf.imports = 'import string as name'

    def service(self):
        self.ebnf.command = 'name'
        self.ebnf.arguments = 'name? colon (values, path)'
        self.ebnf.output = '(as name (comma name)*)'
        self.ebnf.service_fragment = '(command arguments*|arguments+) output?'
        self.ebnf.service = 'path service_fragment'

    def build(self):
        self.macros()
        self.types()
        self.values()
        self.assignments()
        self.imports()
        self.service()
        self.rules()
        self.ebnf.start = 'nl? block'
        self.ebnf.ignore('_WS')
        return self.ebnf.build()
