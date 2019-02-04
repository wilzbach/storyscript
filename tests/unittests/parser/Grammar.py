# -*- coding: utf-8 -*-
from unittest.mock import call

from pytest import fixture

from storyscript.parser import Ebnf, Grammar


@fixture
def grammar(magic):
    grammar = Grammar()
    grammar.ebnf = magic()
    return grammar


@fixture
def ebnf(magic, grammar):
    ebnf = magic()
    grammar.ebnf = ebnf
    return ebnf


def test_grammar_init():
    grammar = Grammar()
    assert isinstance(grammar.ebnf, Ebnf)


def test_grammar_macros(grammar, ebnf):
    grammar.macros()
    ebnf.macro.call_count == 2


def test_grammar_types(grammar, ebnf):
    grammar.types()
    assert ebnf.INT_TYPE == 'int'
    assert ebnf.FLOAT_TYPE == 'float'
    assert ebnf.NUMBER_TYPE == 'number'
    assert ebnf.STRING_TYPE == 'string'
    assert ebnf.LIST_TYPE == 'list'
    assert ebnf.OBJECT_TYPE == 'object'
    assert ebnf.REGEXP_TYPE == 'regex'
    assert ebnf.FUNCTION_TYPE == 'function'
    assert ebnf.ANY_TYPE == 'any'
    rule = ('int_type, float_type, number_type, string_type, list_type, '
            'object_type, regexp_type, function_type, any_type')
    assert ebnf.types == rule


def test_grammar_values(grammar, ebnf):
    grammar.values()
    assert ebnf._NL == r'/(\r?\n[\t ]*)+/'
    assert ebnf._INDENT == '<INDENT>'
    assert ebnf._DEDENT == '<DEDENT>'
    assert ebnf.TRUE == 'true'
    assert ebnf.FALSE == 'false'
    assert ebnf.NULL == 'null'
    assert ebnf.SINGLE_QUOTED == "/'([^']*)'/"
    assert ebnf.DOUBLE_QUOTED == '/"([^"]*)"/'
    assert ebnf._OSB == '['
    assert ebnf._CSB == ']'
    assert ebnf._OCB == '{'
    assert ebnf._CCB == '}'
    assert ebnf._COLON == ':'
    assert ebnf._COMMA == ','
    assert ebnf._OP == '('
    assert ebnf._CP == ')'
    assert ebnf.boolean == 'true, false'
    assert ebnf.void == 'null'
    assert ebnf.number == 'int, float'
    assert ebnf.string == 'single_quoted, double_quoted'
    assert ebnf.key_value == '(string, path) colon expression'
    assert ebnf.objects == ebnf.collection()
    assert ebnf.regular_expression == 'regexp name?'
    assert ebnf.inline_expression == 'op service cp'
    values = ('number, string, boolean, void, list, objects, '
              'regular_expression')
    assert ebnf.values == values


def test_grammar_assignments(grammar, ebnf):
    grammar.assignments()
    assert ebnf.EQUALS == '='
    assert ebnf._DOT == '.'
    path_fragment = 'dot name, osb int csb, osb string csb, osb path csb'
    assert ebnf.path_fragment == path_fragment
    assert ebnf.path == ('name (path_fragment)* | '
                         'inline_expression (path_fragment)*')
    assignment_fragment = 'equals (expression, service, mutation)'
    assert ebnf.assignment_fragment == assignment_fragment
    assert ebnf.assignment == 'path assignment_fragment'


def test_grammar_imports(grammar, ebnf):
    grammar.imports()
    assert ebnf._AS == 'as'
    assert ebnf._IMPORT == 'import'
    assert ebnf.imports == 'import string as name'


def test_grammar_expressions(grammar, ebnf, magic):
    ebnf.set_token = magic()
    grammar.expressions()
    assert ebnf.set_token.call_args_list == [
        call('DASH.4', '-'),
    ]

    assert ebnf.POWER == '^'
    assert ebnf.NOT == 'not'

    assert ebnf.OR == 'or'
    assert ebnf.AND == 'and'

    assert ebnf.GREATER == '>'
    assert ebnf.GREATER_EQUAL == '>='
    assert ebnf.LESSER == '<'
    assert ebnf.LESSER_EQUAL == '<='
    assert ebnf.NOT_EQUAL == '!='
    assert ebnf.EQUAL == '=='

    assert ebnf.BSLASH == '/'
    assert ebnf.MULTIPLIER == '*'
    assert ebnf.MODULUS == '%'

    assert ebnf.PLUS == '+'

    assert ebnf.cmp_operator == ('GREATER, GREATER_EQUAL, LESSER, '
                                 'LESSER_EQUAL, NOT_EQUAL, EQUAL')
    assert ebnf.arith_operator == 'PLUS, DASH'
    assert ebnf.unary_operator == 'NOT'
    assert ebnf.mul_operator == 'MULTIPLIER, BSLASH, MODULUS'

    assert ebnf.primary_expression == 'entity , op or_expression cp'
    assert ebnf.pow_expression == ('primary_expression (POWER '
                                   'unary_expression)?')
    assert ebnf.unary_expression == ('unary_operator unary_expression , '
                                     'pow_expression')
    assert ebnf.mul_expression == '(mul_expression mul_operator)? ' \
                                  'unary_expression'
    assert ebnf.arith_expression == '(arith_expression arith_operator)? ' \
                                    'mul_expression'
    assert ebnf.cmp_expression == '(cmp_expression cmp_operator)? ' \
                                  'arith_expression'
    assert ebnf.and_expression == '(and_expression AND)? cmp_expression'
    assert ebnf.or_expression == '(or_expression OR)? and_expression'

    assert ebnf.expression == 'or_expression'
    assert ebnf.absolute_expression == 'expression'


def test_grammar_raise_statement(grammar, ebnf):
    grammar.raise_statement()
    assert ebnf.RAISE == 'raise'
    assert ebnf.raise_statement == 'raise entity?'


def test_grammar_rules(grammar, ebnf):
    grammar.rules()
    assert ebnf.RETURN == 'return'
    assert ebnf.BREAK == 'break'
    assert ebnf.entity == 'values, path'
    assert ebnf.return_statement == 'return entity?'
    rules = ('absolute_expression, assignment, imports, return_statement, '
             'raise_statement, break_statement, block')
    assert ebnf.rules == rules


def test_mutation_block(grammar, ebnf):
    grammar.mutation_block()
    assert ebnf._THEN == 'then'
    assert ebnf.mutation_fragment == 'name arguments*'
    assert ebnf.chained_mutation == 'then mutation_fragment'
    assert ebnf.mutation == 'entity (mutation_fragment (chained_mutation)*)'
    assert ebnf.mutation_block == 'mutation nl (nested_block)?'
    assert ebnf.indented_chain == 'indent (chained_mutation nl)+ dedent'


def test_grammar_service_block(grammar, ebnf):
    grammar.service_block()
    assert ebnf.command == 'name'
    assert ebnf.arguments == 'name? colon expression'
    assert ebnf.output == '(as name (comma name)*)'
    assert ebnf.service_fragment == '(command arguments*|arguments+) output?'
    assert ebnf.service == 'path service_fragment chained_mutation*'
    assert ebnf.service_block == 'service nl (nested_block)?'


def test_grammar_if_block(grammar, ebnf):
    grammar.if_block()
    assert ebnf.if_statement == 'if expression'
    elseif_statement = 'else if expression'
    assert ebnf.elseif_statement == elseif_statement
    assert ebnf.elseif_block == ebnf.simple_block()
    ebnf.set_rule.assert_called_with('!else_statement', 'else')
    assert ebnf.else_block == ebnf.simple_block()
    if_block = 'if_statement nl nested_block elseif_block* else_block?'
    assert ebnf.if_block == if_block


def test_grammar_foreach_block(grammar, ebnf):
    grammar.foreach_block()
    assert ebnf._FOREACH == 'foreach'
    assert ebnf.foreach_statement == 'foreach entity output'
    ebnf.simple_block.assert_called_with('foreach_statement')
    assert ebnf.foreach_block == ebnf.simple_block()


def test_grammar_while_block(grammar, ebnf):
    grammar.while_block()
    assert ebnf._WHILE == 'while'
    assert ebnf.while_statement == 'while expression'
    ebnf.simple_block.assert_called_with('while_statement')
    assert ebnf.while_block == ebnf.simple_block()


def test_grammar_function_block(grammar, ebnf):
    grammar.function_block()
    assert ebnf._RETURNS == 'returns'
    assert ebnf.typed_argument == 'name colon types'
    assert ebnf.function_output == 'returns types'
    function_statement = 'function_type name typed_argument* function_output?'
    assert ebnf.function_statement == function_statement
    ebnf.simple_block.assert_called_with('function_statement')
    assert ebnf.function_block == ebnf.simple_block()


def test_grammar_try_block(grammar, ebnf):
    grammar.try_block()
    assert ebnf.TRY == 'try'
    assert ebnf._CATCH == 'catch'
    assert ebnf.FINALLY == 'finally'
    assert ebnf.catch_statement == 'catch as name'
    assert ebnf.catch_block == ebnf.simple_block()
    assert ebnf.finally_statement == 'finally'
    assert ebnf.finally_block == ebnf.simple_block()
    assert ebnf.try_statement == 'try'
    try_block = 'try_statement nl nested_block catch_block? finally_block?'
    assert ebnf.try_block == try_block


def test_grammar_block(grammar, ebnf):
    grammar.block()
    assert ebnf._WHEN == 'when'
    ebnf.simple_block.assert_called_with('when (path output|service)')
    assert ebnf.when_block == ebnf.simple_block()
    assert ebnf.indented_arguments == 'indent (arguments nl)+ dedent'
    block = ('rules nl, if_block, foreach_block, function_block, arguments, '
             'indented_chain, chained_mutation, mutation_block, '
             'service_block, when_block, try_block, indented_arguments, '
             'while_block')
    assert ebnf.block == block
    assert ebnf.nested_block == 'indent block+ dedent'


def test_grammar_build(patch, call_count, grammar, ebnf):
    methods = ['macros', 'types', 'values', 'assignments', 'imports',
               'expressions', 'rules', 'mutation_block', 'service_block',
               'if_block', 'foreach_block', 'function_block', 'try_block',
               'block', 'while_block', 'raise_statement']
    patch.many(Grammar, methods)
    result = grammar.build()
    assert ebnf._WS == '(" ")+'
    call_count(Grammar, methods)
    assert ebnf.start == 'nl? block*'
    ebnf.ignore.assert_called_with('_WS')
    assert result == ebnf.build()
