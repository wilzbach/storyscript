# -*- coding: utf-8 -*-
from .Ebnf import Ebnf


class Grammar:

    """
    Defines Storyscript's grammar using the Ebnf module, producing the complete
    EBNF grammar for it.
    """

    def __init__(self):
        self.ebnf = Ebnf()

    def macros(self):
        """
        Define the macros
        """
        collection = '{} (nl indent)? ({} (comma nl? {})*)? (nl dedent)? {}'
        self.ebnf.macro('collection', collection)
        self.ebnf.macro('simple_block', '{} nl nested_block')

    def types(self):
        """
        Defines available types
        """
        self.ebnf.INT_TYPE = 'int'
        self.ebnf.BOOLEAN_TYPE = 'boolean'
        self.ebnf.FLOAT_TYPE = 'float'
        self.ebnf.STRING_TYPE = 'string'
        self.ebnf.OBJECT_TYPE = 'object'
        self.ebnf.REGEXP_TYPE = 'regex'
        self.ebnf.FUNCTION_TYPE = 'function'
        self.ebnf.TIME_TYPE = 'time'
        self.ebnf.ANY_TYPE = 'any'
        self.ebnf.base_type = ('int_type, float_type, string_type, '
                               'object_type, regexp_type, function_type, '
                               'any_type, boolean_type, time_type')
        self.ebnf.OSB = '['
        self.ebnf.CSB = ']'
        self.ebnf._COMMA = ','
        self.ebnf._LIST_KEYWORD = 'List'
        self.ebnf._MAP_KEYWORD = 'Map'
        self.ebnf.list_type = 'list_keyword osb types csb'
        self.ebnf.map_type = 'map_keyword osb base_type comma types csb'
        self.ebnf.types = 'list_type , map_type, base_type'

    def values(self):
        self.ebnf._NL = r'/(\r?\n *)+/'
        self.ebnf._INDENT = '<INDENT>'
        self.ebnf._DEDENT = '<DEDENT>'
        self.ebnf.TRUE = 'true'
        self.ebnf.FALSE = 'false'
        self.ebnf.NULL_CONSTANT = 'null'
        self.ebnf.set_token('RAW_INT.2', r'/[0-9]+/')
        self.ebnf.set_token('INT.2', '("+"|"-")? RAW_INT')
        self.ebnf.set_token('FLOAT.2', '("+"|"-")? INT "." RAW_INT? | '
                            '"." RAW_INT')
        self.ebnf.SINGLE_QUOTED = r"/'([^'\\]*(?:\\(.|\n)[^'\\]*)*)'/"
        self.ebnf.DOUBLE_QUOTED = r'/"([^"\\]*(?:\\(.|\n)[^"\\]*)*)"/'
        self.ebnf.set_token('DOUBLE_QUOTED_HEREDOC.2', r'/"""(.|\n)*?"""/')
        self.ebnf.set_token('REGEXP.10', r'/\/([^\/\n]*)\/g?i?m?s?u?y?/')
        self.ebnf.set_token('NAME.1', r'/[a-zA-Z_][a-zA-Z-\/_0-9]*/')
        self.ebnf.set_token('RAW_TIME.3', r'/([0-9]+(ms|[smhdw]))+/')
        self.ebnf.OCB = '{'
        self.ebnf.CCB = '}'
        self.ebnf._COLON = ':'
        self.ebnf._OP = '('
        self.ebnf._CP = ')'
        self.ebnf.boolean = 'true, false'
        self.ebnf.null = 'null_constant'
        self.ebnf.number = 'int, float'
        self.ebnf.time = 'raw_time'

        self.ebnf.string = ('single_quoted, double_quoted, '
                            'double_quoted_heredoc')

        list = self.ebnf.collection('osb', 'base_expression',
                                    'base_expression', 'csb')
        self.ebnf.set_rule('!list', list)
        self.ebnf.key_value = ('(string, path, number, boolean) '
                               'colon base_expression')
        map_ = ('ocb', 'key_value', 'key_value', 'ccb')
        self.ebnf.map = self.ebnf.collection(*map_)
        self.ebnf.regular_expression = 'regexp'
        self.ebnf.inline_expression = ('op inline_service cp, '
                                       'call_expression')
        self.ebnf.value_fragment = 'osb expression csb'
        values = ('number, string, boolean, null, (list|map) value_fragment*, '
                  'regular_expression, time')
        self.ebnf.values = values

    def assignments(self):
        self.ebnf.EQUALS = '='
        self.ebnf._DOT = '.'
        self.ebnf.set_token('ADD_EQUALS.5', '+=')
        self.ebnf.set_token('SUB_EQUALS.5', '-=')
        self.ebnf.set_token('DIV_EQUALS.5', '/=')
        self.ebnf.set_token('MUL_EQUALS.5', '*=')
        self.ebnf.set_token('MOD_EQUALS.5', '%=')
        self.ebnf.range_start = '(number | path) colon'
        self.ebnf.range_start_end = '(number | path) colon (number | path)'
        self.ebnf.range_end = 'colon (number | path)'
        self.ebnf.range = 'range_start_end | range_start | range_end'
        path_fragment = ('dot name, osb '
                         '(expression | range) csb')
        self.ebnf.path_fragment = path_fragment
        self.ebnf.path = ('name (path_fragment)* | '
                          'inline_expression (path_fragment)*')
        self.ebnf.operator_assignment = ('ADD_EQUALS, SUB_EQUALS, DIV_EQUALS, '
                                         'MUL_EQUALS, MOD_EQUALS')
        assignment_fragment = '(operator_assignment | equals) base_expression'
        self.ebnf.assignment_fragment = assignment_fragment
        objects = self.ebnf.collection('ocb', 'path', 'path', 'ccb')
        self.ebnf.assignment_destructoring = objects
        self.ebnf.assignment = ('(path | assignment_destructoring) '
                                'assignment_fragment')

    def expressions(self):

        self.ebnf.POWER = '^'
        self.ebnf.NOT = 'not'

        self.ebnf.OR = 'or'
        self.ebnf.AND = 'and'

        self.ebnf._AS = 'as'

        self.ebnf.GREATER = '>'
        self.ebnf.GREATER_EQUAL = '>='
        self.ebnf.LESSER = '<'
        self.ebnf.LESSER_EQUAL = '<='
        self.ebnf.NOT_EQUAL = '!='
        self.ebnf.EQUAL = '=='

        self.ebnf.set_token('BSLASH.5', '/')
        self.ebnf.MULTIPLIER = '*'
        self.ebnf.set_token('MODULUS.5', '%')

        self.ebnf.set_token('PLUS.5', '+')
        self.ebnf.set_token('DASH.5', '-')

        # create a special token for integer mutations (e.g. 1.mutation)
        # s.t. the lexer prefers this over a FLOAT (1.)
        self.ebnf.set_token('FLOAT_MUT.5', 'FLOAT NAME "("')

        self.ebnf.cmp_operator = ('GREATER, GREATER_EQUAL, LESSER, '
                                  'LESSER_EQUAL, NOT_EQUAL, EQUAL')
        self.ebnf.arith_operator = 'PLUS, DASH'
        self.ebnf.unary_operator = 'NOT'
        self.ebnf.mul_operator = 'MULTIPLIER, BSLASH, MODULUS'

        self.ebnf.primary_expression = 'entity , op or_expression cp'
        self.ebnf.output_names = 'name (comma name)*'
        self.ebnf.as_operator = 'as (types | output_names)'
        self.ebnf.pow_operator = 'POWER'

        args = 'name op arguments* cp'
        self.ebnf.dot_arguments = f'dot {args}'
        self.ebnf.dot_expression = f'primary_expression dot_arguments*, ' \
                                   f'float_mut arguments* cp dot_arguments*'
        self.ebnf.pow_expression = 'dot_expression (pow_operator ' \
                                   'unary_expression)?, dot_expression'
        self.ebnf.unary_expression = ('unary_operator unary_expression , '
                                      'pow_expression')
        self.ebnf.as_expression = 'unary_expression (as_operator)?'
        self.ebnf.mul_expression = '(mul_expression mul_operator)? ' \
                                   'as_expression'
        self.ebnf.arith_expression = '(arith_expression arith_operator)? ' \
                                     'mul_expression'
        self.ebnf.cmp_expression = '(cmp_expression cmp_operator)? ' \
                                   'arith_expression'
        self.ebnf.and_operator = 'AND'
        self.ebnf.and_expression = '(and_expression and_operator)? ' \
                                   'cmp_expression'
        self.ebnf.or_operator = 'OR'
        self.ebnf.or_expression = '(or_expression or_operator)? ' \
                                  'and_expression'

        self.ebnf.expression = 'or_expression'
        self.ebnf.absolute_expression = 'expression'
        # service calls don't need parentheses when they are at
        # the base,e.g. `if my_service commmand`
        self.ebnf.base_expression = '(expression, inline_service)'

    def throw_statement(self):
        self.ebnf.THROW = 'throw'
        self.ebnf.throw_statement = ('throw entity?')

    def rules(self):
        self.ebnf.RETURN = 'return'
        self.ebnf.BREAK = 'break'
        self.ebnf.CONTINUE = 'continue'
        self.ebnf.return_statement = 'return base_expression?'
        self.ebnf.break_statement = 'break'
        self.ebnf.continue_statement = 'continue'
        self.ebnf.entity = 'values, path'
        rules = ('absolute_expression, assignment, return_statement, '
                 'throw_statement, break_statement, continue_statement, '
                 'block')
        self.ebnf.rules = rules

    def service_block(self):
        self.ebnf.command = 'name'
        self.ebnf.arguments = 'name? colon expression'
        self.ebnf.output = '(as name (comma name)*)'
        self.ebnf.service_fragment = 'command arguments* output?'
        self.ebnf.when_service_fragment = '(command arguments*|arguments+) ' \
                                          'output?'
        self.ebnf.inline_service_fragment = 'command arguments*'
        self.ebnf.service = 'path service_fragment'
        self.ebnf.service_block = 'service nl (nested_block)?'
        self.ebnf.inline_service = ('path inline_service_fragment')

    def call_expression(self):
        self.ebnf.call_expression = ('path op arguments* '
                                     '(nl indent (arguments nl?)* dedent)? cp')

    def if_block(self):
        self.ebnf._IF = 'if'
        self.ebnf._ELSE = 'else'
        self.ebnf.if_statement = 'if base_expression'
        elseif_statement = 'else if base_expression'
        self.ebnf.elseif_statement = elseif_statement
        self.ebnf.elseif_block = self.ebnf.simple_block('elseif_statement')
        self.ebnf.set_rule('!else_statement', 'else')
        self.ebnf.else_block = self.ebnf.simple_block('else_statement')
        if_block = 'if_statement nl nested_block elseif_block* else_block?'
        self.ebnf.if_block = if_block

    def while_block(self):
        self.ebnf._WHILE = 'while'
        self.ebnf.while_statement = 'while base_expression'
        self.ebnf.while_block = self.ebnf.simple_block('while_statement')

    def foreach_block(self):
        self.ebnf._FOREACH = 'foreach'
        self.ebnf.foreach_statement = 'foreach base_expression output?'
        self.ebnf.foreach_block = self.ebnf.simple_block('foreach_statement')

    def function_block(self):
        self.ebnf._RETURNS = 'returns'
        self.ebnf.typed_argument = 'name colon types'
        self.ebnf.function_output = 'returns types'
        function_statement = ('function_type name typed_argument* '
                              'function_output?')
        self.ebnf.function_statement = function_statement
        self.ebnf._DOUBLE_DEDENT = '<DOUBLE_DEDENT>'
        self.ebnf.indented_typed_arguments = \
            'indent (typed_argument+ nl)+ dedent _DOUBLE_DEDENT'
        self.ebnf.function_block = (
            'function_statement nl '
            '(indented_typed_arguments? block+ _DEDENT | '
            'nested_block)'
        )

    def try_block(self):
        self.ebnf.TRY = 'try'
        self.ebnf.CATCH = 'catch'
        self.ebnf.FINALLY = 'finally'
        self.ebnf.catch_statement = 'catch (as name)?'
        self.ebnf.catch_block = self.ebnf.simple_block('catch_statement')
        self.ebnf.finally_statement = 'finally'
        self.ebnf.finally_block = self.ebnf.simple_block('finally_statement')
        self.ebnf.try_statement = 'try'
        try_block = ('try_statement nl nested_block catch_block? '
                     'finally_block?')
        self.ebnf.try_block = try_block

    def block(self):
        self.ebnf._WHEN = 'when'
        self.ebnf.when_service = 'name path (when_service_fragment | output?)'
        when = 'when (when_service | name output?)'
        self.ebnf.when_block = self.ebnf.simple_block(when)
        self.ebnf.indented_arguments = 'indent (arguments nl)+ dedent'
        block = ('rules nl, if_block, foreach_block, function_block, '
                 'arguments, service_block, when_block, try_block, '
                 'indented_arguments, while_block')
        self.ebnf.block = block
        self.ebnf.nested_block = 'indent block+ dedent'

    def build(self):
        self.ebnf._WS = '(" ")+'
        self.macros()
        self.types()
        self.values()
        self.assignments()
        self.expressions()
        self.rules()
        self.service_block()
        self.call_expression()
        self.if_block()
        self.foreach_block()
        self.while_block()
        self.function_block()
        self.try_block()
        self.throw_statement()
        self.block()
        self.ebnf.start = 'nl? block*'
        self.ebnf.ignore('_WS')
        self.ebnf.SINGLE_LINE_COMMENT = r'/(\r?\n)?\s*#[^\n\r]*/'
        self.ebnf.ignore('SINGLE_LINE_COMMENT')
        self.ebnf.MULTI_LINE_COMMENT = \
            r'/(\r?\n)?\s*#+##[^#](.|\n)*?###[^\n\r]*/'
        self.ebnf.ignore('MULTI_LINE_COMMENT')

        return self.ebnf.build()
