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
        self.ebnf.FLOAT_TYPE = 'float'
        self.ebnf.NUMBER_TYPE = 'number'
        self.ebnf.STRING_TYPE = 'string'
        self.ebnf.LIST_TYPE = 'list'
        self.ebnf.OBJECT_TYPE = 'object'
        self.ebnf.REGEXP_TYPE = 'regex'
        self.ebnf.FUNCTION_TYPE = 'function'
        self.ebnf.ANY_TYPE = 'any'
        rule = ('int_type, float_type, number_type, string_type, list_type, '
                'object_type, regexp_type, function_type, any_type')
        self.ebnf.types = rule

    def values(self):
        self.ebnf._NL = r'/(\r?\n[\t ]*)+/'
        self.ebnf._INDENT = '<INDENT>'
        self.ebnf._DEDENT = '<DEDENT>'
        self.ebnf.TRUE = 'true'
        self.ebnf.FALSE = 'false'
        self.ebnf.NULL = 'null'
        self.ebnf.set_token('INT.2', r'/[0-9]+/')
        self.ebnf.set_token('FLOAT.2', 'INT "." INT? | "." INT')
        self.ebnf.SINGLE_QUOTED = "/'([^']*)'/"
        self.ebnf.DOUBLE_QUOTED = '/"([^"]*)"/'
        self.ebnf.set_token('REGEXP.2', r'/\/([^\/]*)\//')
        self.ebnf.set_token('NAME.1', r'/[a-zA-Z-\/_0-9]+/')
        self.ebnf._OSB = '['
        self.ebnf._CSB = ']'
        self.ebnf._OCB = '{'
        self.ebnf._CCB = '}'
        self.ebnf._COLON = ':'
        self.ebnf._COMMA = ','
        self.ebnf._OP = '('
        self.ebnf._CP = ')'
        self.ebnf.boolean = 'true, false'
        self.ebnf.void = 'null'
        self.ebnf.number = 'int, float'
        self.ebnf.string = 'single_quoted, double_quoted'
        list = self.ebnf.collection('osb', 'entity', 'entity', 'csb')
        self.ebnf.set_rule('!list', list)
        self.ebnf.key_value = '(string, path) colon entity'
        objects = ('ocb', 'key_value', 'key_value', 'ccb')
        self.ebnf.objects = self.ebnf.collection(*objects)
        self.ebnf.regular_expression = 'regexp name?'
        self.ebnf.inline_expression = 'op service cp'
        values = ('number, string, boolean, void, list, objects, '
                  'regular_expression')
        self.ebnf.values = values

    def assignments(self):
        self.ebnf.EQUALS = '='
        self.ebnf._DOT = '.'
        path_fragment = 'dot name, osb int csb, osb string csb, osb path csb'
        self.ebnf.path_fragment = path_fragment
        self.ebnf.path = ('name (path_fragment)* | '
                          'inline_expression (path_fragment)*')
        assignment_fragment = 'equals (expression, service)'
        self.ebnf.assignment_fragment = assignment_fragment
        self.ebnf.assignment = 'path assignment_fragment'

    def imports(self):
        self.ebnf._AS = 'as'
        self.ebnf._IMPORT = 'import'
        self.ebnf.imports = 'import string as name'

    def service(self):
        self.ebnf.command = 'name'
        self.ebnf.arguments = 'name? colon entity'
        self.ebnf.output = '(as name (comma name)*)'
        self.ebnf.service_fragment = '(command arguments*|arguments+) output?'
        self.ebnf.service = 'path service_fragment'

    def expressions(self):
        self.ebnf.PLUS = '+'
        self.ebnf.set_token('DASH.4', '-')
        self.ebnf.MULTIPLIER = '*'
        self.ebnf.set_token('BSLASH.3', '/')
        self.ebnf.MODULUS = '%'
        self.ebnf.POWER = '^'
        self.ebnf.NOT = 'not'
        self.ebnf.AND = 'and'
        self.ebnf.OR = 'or'
        self.ebnf.mutation = 'name arguments*'
        self.ebnf.factor = '(dash, plus)? entity, op expression cp'
        self.ebnf.exponential = 'factor (power exponential)?'
        self.ebnf.multiplication = ('exponential (( multiplier, bslash, '
                                    'modulus ) exponential)*')
        self.ebnf.expression = ('multiplication ( ( plus, dash ) '
                                'multiplication)*, number multiplication+, '
                                'entity mutation')
        self.ebnf.absolute_expression = 'expression'

    def rules(self):
        self.ebnf._RETURN = 'return'
        self.ebnf.return_statement = 'return entity'
        self.ebnf.entity = 'values, path'
        rules = ('absolute_expression, assignment, imports, return_statement, '
                 'block')
        self.ebnf.rules = rules

    def if_block(self):
        self.ebnf.GREATER = '>'
        self.ebnf.GREATER_EQUAL = '>='
        self.ebnf.LESSER = '<'
        self.ebnf.LESSER_EQUAL = '<='
        self.ebnf.NOT = '!='
        self.ebnf.EQUAL = '=='
        self.ebnf._IF = 'if'
        self.ebnf._ELSE = 'else'
        comparisons = ('greater, greater_equal, lesser, lesser_equal, not, '
                       'equal')
        self.ebnf.comparisons = comparisons
        self.ebnf.if_statement = 'if entity (comparisons entity)?'
        elseif_statement = 'else if entity (comparisons entity)?'
        self.ebnf.elseif_statement = elseif_statement
        self.ebnf.elseif_block = self.ebnf.simple_block('elseif_statement')
        self.ebnf.set_rule('!else_statement', 'else')
        self.ebnf.else_block = self.ebnf.simple_block('else_statement')
        if_block = 'if_statement nl nested_block elseif_block* else_block?'
        self.ebnf.if_block = if_block

    def while_block(self):
        self.ebnf._WHILE = 'while'
        self.ebnf.while_statement = 'while entity'
        self.ebnf.while_block = self.ebnf.simple_block('while_statement')

    def foreach_block(self):
        self.ebnf._FOREACH = 'foreach'
        self.ebnf.foreach_statement = 'foreach entity output'
        self.ebnf.foreach_block = self.ebnf.simple_block('foreach_statement')

    def function_block(self):
        self.ebnf._RETURNS = 'returns'
        self.ebnf.typed_argument = 'name colon types'
        self.ebnf.function_output = 'returns types'
        function_statement = ('function_type name typed_argument* '
                              'function_output?')
        self.ebnf.function_statement = function_statement
        self.ebnf.function_block = self.ebnf.simple_block('function_statement')

    def raise_statement(self):
        self.ebnf.RAISE = 'raise'
        self.ebnf.raise_statement = ('raise entity?')

    def try_block(self):
        self.ebnf.TRY = 'try'
        self.ebnf._CATCH = 'catch'
        self.ebnf.FINALLY = 'finally'
        self.ebnf.catch_statement = 'catch as name'
        self.ebnf.catch_block = self.ebnf.simple_block('catch_statement')
        self.ebnf.finally_statement = 'finally'
        self.ebnf.finally_block = self.ebnf.simple_block('finally_statement')
        self.ebnf.try_statement = 'try'
        try_block = ('try_statement nl nested_block catch_block? '
                     'finally_block?')
        self.ebnf.try_block = try_block

    def block(self):
        self.ebnf._WHEN = 'when'
        self.ebnf.service_block = 'service nl (nested_block)?'
        when = 'when (path output|service)'
        self.ebnf.when_block = self.ebnf.simple_block(when)
        self.ebnf.indented_arguments = 'indent (arguments nl)+ dedent'
        block = ('rules nl, if_block, foreach_block, function_block, '
                 'arguments, service_block, when_block, try_block, '
                 'indented_arguments, while_block, raise_statement')
        self.ebnf.block = block
        self.ebnf.nested_block = 'indent block+ dedent'

    def build(self):
        self.ebnf._WS = '(" ")+'
        self.macros()
        self.types()
        self.values()
        self.assignments()
        self.imports()
        self.service()
        self.expressions()
        self.rules()
        self.if_block()
        self.foreach_block()
        self.while_block()
        self.function_block()
        self.try_block()
        self.raise_statement()
        self.block()
        self.ebnf.start = 'nl? block+'
        self.ebnf.ignore('_WS')
        return self.ebnf.build()
