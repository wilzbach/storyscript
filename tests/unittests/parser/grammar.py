# -*- coding: utf-8 -*-
from pytest import fixture, raises

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
    rule = ('int_type, float_type, number_type, string_type, list_type, '
            'object_type, regexp_type, function_type')
    assert ebnf.types == rule


def test_grammar_values(grammar, ebnf):
    grammar.values()
    assert ebnf._NL == r'/(\r?\n[\t ]*)+/'
    assert ebnf._INDENT == '<INDENT>'
    assert ebnf._DEDENT == '<DEDENT>'
    assert ebnf.TRUE == 'true'
    assert ebnf.FALSE == 'false'
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
    assert ebnf.number == 'int, float'
    assert ebnf.string == 'single_quoted, double_quoted'
    assert ebnf.key_value == '(string, path) colon (values, path)'
    assert ebnf.objects == ebnf.collection()
    assert ebnf.inline_expression == 'op service cp'
    values = 'number, string, boolean, list, objects, inline_expression'
    assert ebnf.values == values


def test_grammar_assignments(grammar, ebnf):
    grammar.assignments()
    ebnf.set_token.assert_called_with('NAME.1', '/[a-zA-Z-\/_0-9]+/')
    assert ebnf.EQUALS == '='
    assert ebnf._DOT == '.'
    path_fragment = 'dot name, osb int csb, osb string csb, osb path csb'
    assert ebnf.path_fragment == path_fragment
    assert ebnf.path == 'name (path_fragment)*'
    assignment_fragment = 'equals (values, expression, path, service)'
    assert ebnf.assignment_fragment == assignment_fragment
    assert ebnf.assignment == 'path assignment_fragment'


def test_grammar_imports(grammar, ebnf):
    grammar.imports()
    assert ebnf._AS == 'as'
    assert ebnf._IMPORT == 'import'
    assert ebnf.imports == 'import string as name'


def test_grammar_service(grammar, ebnf):
    grammar.service()
    assert ebnf.command == 'name'
    assert ebnf.arguments == 'name? colon (values, path)'
    assert ebnf.output == '(as name (comma name)*)'
    assert ebnf.service_fragment == '(command arguments*|arguments+) output?'
    assert ebnf.service == 'path service_fragment'


def test_grammar_expressions(grammar, ebnf):
    grammar.expressions()
    assert ebnf.PLUS == '+'
    assert ebnf.DASH == '-'
    assert ebnf.MULTIPLIER == '*'
    assert ebnf.BSLASH == '/'
    assert ebnf.operator == 'plus, dash, multiplier, bslash'
    assert ebnf.mutation == 'name arguments*'
    assert ebnf.expression == 'values operator values, values mutation'
    assert ebnf.absolute_expression == 'expression'


def test_grammar_rules(grammar, ebnf):
    grammar.rules()
    assert ebnf._RETURN == 'return'
    assert ebnf.return_statement == 'return (path, values)'
    rules = ('values, absolute_expression, assignment, imports, '
             'return_statement, block')
    assert ebnf.rules == rules


def test_grammar_if_block(grammar, ebnf):
    grammar.if_block()
    assert ebnf.GREATER == '>'
    assert ebnf.GREATER_EQUAL == '>='
    assert ebnf.LESSER == '<'
    assert ebnf.LESSER_EQUAL == '<='
    assert ebnf.NOT == '!='
    assert ebnf.EQUAL == '=='
    assert ebnf._IF == 'if'
    assert ebnf._ELSE == 'else'
    assert ebnf.path_value == 'path, values'
    comparisons = 'greater, greater_equal, lesser, lesser_equal, not, equal'
    assert ebnf.comparisons == comparisons
    assert ebnf.if_statement == 'if path_value (comparisons path_value)?'
    elseif_statement = 'else if path_value (comparisons path_value)?'
    assert ebnf.elseif_statement == elseif_statement
    assert ebnf.elseif_block == ebnf.simple_block()
    ebnf.set_rule.assert_called_with('!else_statement', 'else')
    assert ebnf.else_block == ebnf.simple_block()
    if_block = 'if_statement nl nested_block elseif_block* else_block?'
    assert ebnf.if_block == if_block


def test_grammar_foreach_block(grammar, ebnf):
    grammar.foreach_block()
    assert ebnf._FOREACH == 'foreach'
    assert ebnf.foreach_statement == 'foreach name output'
    ebnf.simple_block.assert_called_with('foreach_statement')
    assert ebnf.foreach_block == ebnf.simple_block()


def test_grammar_function_block(grammar, ebnf):
    grammar.function_block()
    assert ebnf._RETURNS == 'returns'
    assert ebnf.typed_argument == 'name colon types'
    assert ebnf.function_output == 'returns types'
    function_statement = 'function_type name typed_argument* function_output?'
    assert ebnf.function_statement == function_statement
    ebnf.simple_block.assert_called_with('function_statement')
    assert ebnf.function_block == ebnf.simple_block()


def test_grammar_block(grammar, ebnf):
    grammar.block()
    assert ebnf._WHEN == 'when'
    assert ebnf.service_block == 'service nl (nested_block)?'
    ebnf.simple_block.assert_called_with('when (path output|service)')
    assert ebnf.when_block == ebnf.simple_block()
    block = ('rules nl, if_block, foreach_block, function_block, '
             'arguments, service_block, when_block')
    assert ebnf.block == block
    assert ebnf.nested_block == 'indent block+ dedent'


def test_grammar_build(patch, call_count, grammar, ebnf):
    methods = ['macros', 'types', 'values', 'assignments', 'imports',
               'service', 'expressions', 'rules']
    patch.many(Grammar, methods)
    result = grammar.build()
    call_count(Grammar, methods)
    assert ebnf.start == 'nl? block'
    ebnf.ignore.assert_called_with('_WS')
    assert result == ebnf.build()
