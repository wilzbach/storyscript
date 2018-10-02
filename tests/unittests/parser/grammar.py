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


def test_grammar_rules(grammar, ebnf):
    grammar.rules()
    defintions = (['values'], ['absolute_expression'], ['assignment'],
                  ['imports'], ['return_statement'], ['block'])
    ebnf.rules.assert_called_with('rules', *defintions)


def test_grammar_whitespaces(grammar, ebnf):
    grammar.whitespaces()
    tokens = (('ws', '(" ")+'), ('nl', r'/(\r?\n[\t ]*)+/'))
    ebnf.tokens.assert_called_with(*tokens, inline=True, regexp=True)


def test_grammar_indentation(grammar, ebnf):
    grammar.indentation()
    tokens = (('indent', '<INDENT>'), ('dedent', '<DEDENT>'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)


def test_grammar_spaces(patch, call_count, grammar):
    patch.many(Grammar, ['whitespaces', 'indentation'])
    grammar.spaces()
    call_count(Grammar, ['whitespaces', 'indentation'])


def test_grammar_nested_block(grammar, ebnf):
    grammar.nested_block()
    definition = '_INDENT block+ _DEDENT'
    ebnf.rule.assert_called_with('nested_block', definition, raw=True)


def test_grammar_elseif_block(patch, call_count, grammar, ebnf):
    patch.many(Grammar, ['nested_block', 'elseif_statement'])
    grammar.elseif_block()
    call_count(Grammar, ['nested_block', 'elseif_statement'])
    definition = ('elseif_statement', 'nl', 'nested_block')
    ebnf.rule.assert_called_with('elseif_block', definition)


def test_grammar_else_block(patch, grammar, ebnf):
    patch.object(Grammar, 'else_statement')
    grammar.else_block()
    assert Grammar.else_statement.call_count == 1
    definition = ('else_statement', 'nl', 'nested_block')
    ebnf.rule.assert_called_with('else_block', definition)


def test_grammar_if_block(patch, call_count, grammar, ebnf):
    patch.many(Grammar, ['if_statement', 'elseif_block', 'else_block'])
    grammar.if_block()
    call_count(Grammar, ['if_statement', 'elseif_block', 'else_block'])
    definition = 'if_statement _NL nested_block elseif_block* else_block?'
    ebnf.rule.assert_called_with('if_block', definition, raw=True)


def test_grammar_foreach_block(patch, grammar, ebnf):
    patch.object(Grammar, 'foreach_statement')
    grammar.foreach_block()
    assert Grammar.foreach_statement.call_count == 1
    definition = 'foreach_statement _NL nested_block'
    ebnf.rule.assert_called_with('foreach_block', definition, raw=True)


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


def test_grammar_inline_expression(patch, grammar, ebnf):
    grammar.inline_expression()
    ebnf.tokens.assert_called_with(('op', '('), ('cp', ')'), inline=True)
    ebnf.rule.assert_called_with('inline_expression', ('op', 'service', 'cp'))


def test_grammar_arguments(patch, grammar, ebnf):
    grammar.arguments()
    rule = 'NAME? _COLON (values|path)'
    ebnf.rule.assert_called_with('arguments', rule, raw=True)


def test_grammar_command(grammar, ebnf):
    grammar.command()
    ebnf.rule.assert_called_with('command', ['name'])


def test_grammar_output(grammar, ebnf):
    grammar.output()
    rule = '(_AS NAME (_COMMA NAME)*)'
    ebnf.rule.assert_called_with('output', rule, raw=True)


def test_grammar_service_fragment(patch, call_count, grammar, ebnf):
    patch.many(Grammar, ['arguments', 'command', 'output'])
    grammar.service_fragment()
    call_count(Grammar, ['arguments', 'command', 'output'])
    rule = '(command arguments*|arguments+) output?'
    ebnf.rule.assert_called_with('service_fragment', rule, raw=True)


def test_grammar_service(patch, grammar, ebnf):
    patch.object(Grammar, 'service_fragment')
    grammar.service()
    assert Grammar.service_fragment.call_count == 1
    ebnf.rule.assert_called_with('service', ('path', 'service_fragment'))


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


def test_grammar_operator(grammar, ebnf):
    grammar.operator()
    tokens = (('plus', '+'), ('dash', '-'), ('multiplier', '*'),
              ('bslash', '/'))
    ebnf.tokens.assert_called_with(*tokens)
    definitions = (['plus'], ['dash'], ['multiplier'], ['bslash'])
    ebnf.rules.assert_called_with('operator', *definitions)


def test_grammar_mutation(grammar, ebnf):
    grammar.mutation()
    rule = 'NAME arguments*'
    ebnf.rule.assert_called_with('mutation', rule, raw=True)


def test_grammar_expression(patch, grammar, ebnf):
    patch.many(Grammar, ['operator', 'mutation'])
    grammar.expression()
    assert Grammar.operator.call_count == 1
    assert Grammar.mutation.call_count == 1
    definitions = (('values', 'operator', 'values'),
                   ('values', 'operator', 'values'),
                   ('values', 'mutation'))
    ebnf.rules.assert_called_with('expression', *definitions)


def test_grammar_absolute_expression(patch, grammar, ebnf):
    patch.object(Grammar, 'expression')
    grammar.absolute_expression()
    assert Grammar.expression.call_count == 1
    ebnf.rule.assert_called_with('absolute_expression', ['expression'])


def test_grammar_imports(patch, grammar, ebnf):
    grammar.imports()
    ebnf.token.assert_called_with('import', 'import', inline=True)
    rule = ('import', 'string', 'as', 'name')
    ebnf.rule.assert_called_with('imports', rule)


def test_grammar_comparisons(grammar, ebnf):
    grammar.comparisons()
    tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
              ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
    ebnf.tokens.assert_called_with(*tokens)
    definitions = (['greater'], ['greater_equal'], ['lesser'],
                   ['lesser_equal'], ['not'], ['equal'])
    ebnf.rules.assert_called_with('comparisons', *definitions)


def test_grammar_path_value(grammar, ebnf):
    grammar.path_value()
    ebnf.rules.assert_called_with('path_value', *(['path'], ['values']))


def test_grammar_if_statement(patch, grammar, ebnf):
    patch.object(Grammar, 'path_value')
    grammar.if_statement()
    assert Grammar.path_value.call_count == 1
    ebnf.token.assert_called_with('if', 'if', inline=True)
    rule = '_IF path_value (comparisons path_value)?'
    ebnf.rule.assert_called_with('if_statement', rule, raw=True)


def test_grammar_else_statement(grammar, ebnf):
    grammar.else_statement()
    ebnf.token.assert_called_with('else', 'else', inline=True)
    ebnf.rule.assert_called_with('!else_statement', ['else'])


def test_grammar_elseif_statement(grammar, ebnf):
    grammar.elseif_statement()
    rule = '_ELSE _IF path_value (comparisons path_value)?'
    ebnf.rule.assert_called_with('elseif_statement', rule, raw=True)


def test_grammar_foreach_statement(grammar, ebnf):
    grammar.foreach_statement()
    definition = ('foreach', 'name', 'output')
    ebnf.rule.assert_called_with('foreach_statement', definition)
    tokens = (('foreach', 'foreach'), ('as', 'as'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)


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
    assert ebnf.TRUE == 'true'
    assert ebnf.FALSE == 'false'
    assert ebnf.SINGLE_QUOTED == "/'([^']*)'/"
    assert ebnf.DOUBLE_QUOTED == '/"([^"]*)"/'
    assert ebnf._OSB == '['
    assert ebnf._CSB == ']'
    assert ebnf._OCB == '{'
    assert ebnf._CCB == '}'
    assert ebnf._COLON == ':'
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
    path_fragment = 'dot name, osb int csb, osb string csb, osb path csb'
    assert ebnf.path_fragment == path_fragment
    assert ebnf.path == 'name (path_fragment)*'
    assignment_fragment = 'equals (values, expression, path, service)'
    assert ebnf.assignment_fragment == assignment_fragment
    assert ebnf.assignment == 'path assignment_fragment'


def test_grammar_build(patch, call_count, grammar, ebnf):
    methods = ['macros', 'types', 'values', 'assignments', 'rules']
    patch.many(Grammar, methods)
    result = grammar.build()
    call_count(Grammar, methods)
    assert ebnf.start == 'nl? block'
    ebnf.ignore.assert_called_with('_WS')
    assert result == ebnf.build()
