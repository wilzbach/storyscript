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


def test_grammar_nested_block(grammar, ebnf):
    grammar.nested_block()
    definition = '_INDENT block+ _DEDENT'
    ebnf.rule.assert_called_with('nested_block', definition, raw=True)


def test_grammar_typed_argument(grammar, ebnf):
    grammar.typed_argument()
    definition = ('name', 'colon', 'types')
    ebnf.rule.assert_called_with('typed_argument', definition)


def test_grammar_function_output(grammar, ebnf):
    grammar.function_output()
    ebnf.token.assert_called_with('returns', 'returns', inline=True)
    ebnf.rule.assert_called_with('function_output', ('returns', 'types'))


def test_grammar_function_statement(patch, call_count, grammar, ebnf):
    patch.many(Grammar, ['typed_argument', 'function_output'])
    grammar.function_statement()
    call_count(Grammar, ['typed_argument', 'function_output'])
    rule = 'FUNCTION_TYPE NAME typed_argument* function_output?'
    ebnf.rule.assert_called_with('function_statement', rule, raw=True)


def test_grammar_function_block(patch, grammar, ebnf):
    patch.object(Grammar, 'function_statement')
    grammar.function_block()
    definition = ('function_statement', 'nl', 'nested_block')
    ebnf.rule.assert_called_with('function_block', definition)


def test_grammar_service_block(patch, grammar, ebnf):
    patch.object(Grammar, 'service')
    grammar.service_block()
    rule = 'service _NL (nested_block)?'
    ebnf.rule.assert_called_with('service_block', rule, raw=True)


def test_grammar_when_block(patch, grammar, ebnf):
    grammar.when_block()
    ebnf.token.assert_called_with('when', 'when', inline=True)
    rule = '_WHEN (path output|service) _NL nested_block'
    ebnf.rule.assert_called_with('when_block', rule, raw=True)


def test_grammar_block(patch, call_count, grammar, ebnf):
    methods = ['if_block', 'foreach_block', 'function_block', 'service_block',
               'when_block']
    patch.many(Grammar, methods)
    grammar.block()
    call_count(Grammar, methods)
    definition = ('rules _NL|if_block|foreach_block|function_block'
                  '|arguments|service_block|when_block')
    ebnf.rule.assert_called_with('block', definition, raw=True)


def test_grammar_return_statement(patch, ebnf, grammar):
    grammar.return_statement()
    ebnf.token.assert_called_with('return', 'return', inline=True)
    rule = '_RETURN (path|values)'
    ebnf.rule.assert_called_with('return_statement', rule, raw=True)
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


def test_grammar_build(patch, call_count, grammar, ebnf):
    methods = ['macros', 'types', 'values', 'assignments', 'imports',
               'service', 'expressions', 'rules']
    patch.many(Grammar, methods)
    result = grammar.build()
    call_count(Grammar, methods)
    assert ebnf.start == 'nl? block'
    ebnf.ignore.assert_called_with('_WS')
    assert result == ebnf.build()
