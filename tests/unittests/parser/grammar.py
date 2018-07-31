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


def test_grammar_line(grammar, ebnf):
    grammar.line()
    defintions = (['values'], ['expression'], ['comment'], ['assignment'],
                  ['imports'], ['return_statement'], ['block'])
    ebnf.rules.assert_called_with('line', *defintions)


def test_grammar_whitespaces(grammar, ebnf):
    grammar.whitespaces()
    tokens = (('ws', '(" ")+'), ('nl', r'/(\r?\n[\t ]*)+/'))
    ebnf.tokens.assert_called_with(*tokens, inline=True, regexp=True)


def test_grammar_indentation(grammar, ebnf):
    grammar.indentation()
    tokens = (('indent', '<INDENT>'), ('dedent', '<DEDENT>'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)


def test_grammar_spaces(patch, grammar):
    patch.many(Grammar, ['whitespaces', 'indentation'])
    grammar.spaces()
    assert Grammar.whitespaces.call_count == 1
    assert Grammar.indentation.call_count == 1


def test_grammar_nested_block(grammar, ebnf):
    grammar.nested_block()
    definition = '_INDENT block+ _DEDENT'
    ebnf.rule.assert_called_with('nested_block', definition, raw=True)


def test_grammar_elseif_block(patch, grammar, ebnf):
    patch.many(Grammar, ['nested_block', 'elseif_statement'])
    grammar.elseif_block()
    assert grammar.nested_block.call_count == 1
    assert grammar.elseif_statement.call_count == 1
    definition = ('elseif_statement', 'nl', 'nested_block')
    ebnf.rule.assert_called_with('elseif_block', definition)


def test_grammar_else_block(patch, grammar, ebnf):
    patch.object(Grammar, 'else_statement')
    grammar.else_block()
    assert Grammar.else_statement.call_count == 1
    definition = ('else_statement', 'nl', 'nested_block')
    ebnf.rule.assert_called_with('else_block', definition)


def test_grammar_if_block(patch, grammar, ebnf):
    patch.many(Grammar, ['if_statement', 'elseif_block', 'else_block'])
    grammar.if_block()
    assert Grammar.if_statement.call_count == 1
    assert Grammar.elseif_block.call_count == 1
    assert Grammar.else_block.call_count == 1
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


def test_grammar_function_argument(patch, grammar, ebnf):
    patch.object(Grammar, 'typed_argument')
    grammar.function_argument()
    assert Grammar.typed_argument.call_count == 1
    ebnf.rule.assert_called_with('function_argument', ('ws', 'typed_argument'))


def test_grammar_function_output(grammar, ebnf):
    grammar.function_output()
    ebnf.token.assert_called_with('returns', 'returns', inline=True)
    rule = ('ws', 'returns', 'ws', 'types')
    ebnf.rule.assert_called_with('function_output', rule)


def test_grammar_function_statement(patch, grammar, ebnf):
    patch.many(Grammar, ['function_argument', 'function_output'])
    grammar.function_statement()
    assert Grammar.function_argument.call_count == 1
    assert Grammar.function_output.call_count == 1
    rule = 'FUNCTION_TYPE _WS NAME function_argument* function_output?'
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
    patch.object(Grammar, 'inline_expression')
    grammar.arguments()
    assert Grammar.inline_expression.call_count == 1
    rule = '_WS? NAME? _COLON (values|path|inline_expression)'
    ebnf.rule.assert_called_with('arguments', rule, raw=True)


def test_grammar_command(grammar, ebnf):
    grammar.command()
    ebnf.rule.assert_called_with('command', ('ws', 'name'))


def test_grammar_output(grammar, ebnf):
    grammar.output()
    rule = '(_WS _AS _WS NAME (_COMMA _WS? NAME)*)'
    ebnf.rule.assert_called_with('output', rule, raw=True)


def test_grammar_service_fragment(patch, grammar, ebnf):
    patch.many(Grammar, ['arguments', 'command', 'output'])
    grammar.service_fragment()
    assert Grammar.arguments.call_count == 1
    assert Grammar.command.call_count == 1
    assert Grammar.output.call_count == 1
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
    rule = '_WHEN _WS (path output|service) _NL nested_block'
    ebnf.rule.assert_called_with('when_block', rule, raw=True)


def test_grammar_block(patch, grammar, ebnf):
    patch.many(Grammar, ['if_block', 'foreach_block', 'function_block',
                         'service_block', 'when_block'])
    grammar.block()
    assert Grammar.if_block.call_count == 1
    assert Grammar.foreach_block.call_count == 1
    assert Grammar.function_block.call_count == 1
    assert Grammar.service_block.call_count == 1
    assert Grammar.when_block.call_count == 1
    definition = ('line _NL|if_block|foreach_block|function_block'
                  '|arguments|service_block|when_block')
    ebnf.rule.assert_called_with('block', definition, raw=True)


def test_grammar_number(grammar, ebnf):
    grammar.number()
    tokens = (('int', '"0".."9"+'), ('float', """INT "." INT? | "." INT"""))
    ebnf.tokens.assert_called_with(*tokens, regexp=True, priority=2)
    ebnf.rules.assert_called_with('number', ['int'], ['float'])


def test_grammar_string(grammar, ebnf):
    grammar.string()
    tokens = (('single_quoted', "/'([^']*)'/"),
              ('double_quoted', '/"([^"]*)"/'))
    ebnf.tokens.assert_called_with(*tokens, regexp=True)
    definitions = (['single_quoted'], ['double_quoted'])
    ebnf.rules.assert_called_with('string', *definitions)


def test_grammar_boolean(grammar, ebnf):
    grammar.boolean()
    ebnf.tokens.assert_called_with(('true', 'true'), ('false', 'false'))
    ebnf.rules.assert_called_with('boolean', ['true'], ['false'])


def test_grammar_values(patch, grammar, ebnf):
    patch.many(Grammar, ['number', 'string', 'list', 'objects', 'boolean'])
    grammar.values()
    assert Grammar.number.call_count == 1
    assert Grammar.string.call_count == 1
    assert Grammar.boolean.call_count == 1
    assert Grammar.list.call_count == 1
    assert Grammar.objects.call_count == 1
    rules = (['number'], ['string'], ['boolean'], ['list'], ['objects'])
    ebnf.rules.assert_called_with('values', *rules)


def test_grammar_operator(grammar, ebnf):
    grammar.operator()
    tokens = (('plus', '+'), ('dash', '-'), ('multiplier', '*'),
              ('bslash', '/'))
    ebnf.tokens.assert_called_with(*tokens)
    definitions = (['plus'], ['dash'], ['multiplier'], ['bslash'])
    ebnf.rules.assert_called_with('operator', *definitions)


def test_grammar_mutation(grammar, ebnf):
    grammar.mutation()
    rule = '_WS NAME arguments*'
    ebnf.rule.assert_called_with('mutation', rule, raw=True)


def test_grammar_expression(patch, grammar, ebnf):
    patch.many(Grammar, ['operator', 'mutation'])
    grammar.expression()
    assert Grammar.operator.call_count == 1
    assert Grammar.mutation.call_count == 1
    definitions = (('values', 'ws', 'operator', 'ws', 'values'),
                   ('values', 'operator', 'values'),
                   ('values', 'mutation'))
    ebnf.rules.assert_called_with('expression', *definitions)


def test_grammar_list(grammar, ebnf):
    grammar.list()
    tokens = (('comma', ','), ('osb', '['), ('csb', ']'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)
    definition = ('_OSB (_NL _INDENT)? (values (_COMMA (_WS|_NL)? '
                  'values)*)? (_NL _DEDENT)? _CSB')
    ebnf.rule.assert_called_with('list', definition, raw=True)


def test_grammar_key_value(grammar, ebnf):
    grammar.key_value()
    ebnf.token.assert_called_with('colon', ':', inline=True)
    ebnf.rule.assert_called_with('key_value', ('string', 'colon', 'values'))


def test_grammar_objects(patch, grammar, ebnf):
    patch.object(Grammar, 'key_value')
    grammar.objects()
    assert Grammar.key_value.call_count == 1
    ebnf.tokens.assert_called_with(('ocb', '{'), ('ccb', '}'), inline=True)
    rule = '_OCB (key_value (_COMMA key_value)*)? _CCB'
    ebnf.rule.assert_called_with('objects', rule, raw=True)


def test_grammar_path_fragment(grammar, ebnf):
    grammar.path_fragment()
    ebnf.token.assert_called_with('dot', '.', inline=True)
    definitions = (('dot', 'name'), ('osb', 'int', 'csb'),
                   ('osb', 'string', 'csb'))
    ebnf.rules.assert_called_with('path_fragment', *definitions)


def test_grammar_path(patch, grammar, ebnf):
    patch.object(Grammar, 'path_fragment')
    grammar.path()
    token = '/[a-zA-Z-\/_0-9]+/'
    ebnf.token.assert_called_with('name', token, regexp=True, priority=1)
    Grammar.path_fragment.call_count == 1
    ebnf.rule.assert_called_with('path', 'NAME (path_fragment)*', raw=True)


def test_grammar_assignment_fragment(patch, grammar, ebnf):
    grammar.assignment_fragment()
    ebnf.token.assert_called_with('equals', '=')
    rule = 'EQUALS _WS? (values|expression|path|service)'
    ebnf.rule.assert_called_with('assignment_fragment', rule, raw=True)


def test_grammar_assignment(patch, grammar, ebnf):
    patch.many(Grammar, ['path', 'assignment_fragment'])
    grammar.assignment()
    assert Grammar.path.call_count == 1
    assert Grammar.assignment_fragment.call_count == 1
    definition = ('path', 'ws?', 'assignment_fragment')
    ebnf.rule.assert_called_with('assignment', definition)


def test_grammar_imports(patch, grammar, ebnf):
    grammar.imports()
    ebnf.token.assert_called_with('import', 'import', inline=True)
    rule = ('import', 'ws', 'string', 'ws', 'as', 'ws', 'name')
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
    rule = '_IF _WS path_value (_WS comparisons _WS path_value)?'
    ebnf.rule.assert_called_with('if_statement', rule, raw=True)


def test_grammar_else_statement(grammar, ebnf):
    grammar.else_statement()
    ebnf.token.assert_called_with('else', 'else', inline=True)
    ebnf.rule.assert_called_with('else_statement', ['else'])


def test_grammar_elseif_statement(grammar, ebnf):
    grammar.elseif_statement()
    rule = '_ELSE _WS? _IF _WS path_value (_WS comparisons _WS path_value)?'
    ebnf.rule.assert_called_with('elseif_statement', rule, raw=True)


def test_grammar_foreach_statement(grammar, ebnf):
    grammar.foreach_statement()
    definition = ('foreach', 'ws', 'name', 'output')
    ebnf.rule.assert_called_with('foreach_statement', definition)
    tokens = (('foreach', 'foreach'), ('as', 'as'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)


def test_grammar_return_statement(patch, ebnf, grammar):
    grammar.return_statement()
    ebnf.token.assert_called_with('return', 'return', inline=True)
    rule = '_RETURN _WS (path|values)'
    ebnf.rule.assert_called_with('return_statement', rule, raw=True)


def test_grammar_int_type(grammar, ebnf):
    grammar.int_type()
    ebnf.token.assert_called_with('int_type', 'int')


def test_grammar_float_type(grammar, ebnf):
    grammar.float_type()
    ebnf.token.assert_called_with('float_type', 'float')


def test_grammar_number_type(grammar, ebnf):
    grammar.number_type()
    ebnf.token.assert_called_with('number_type', 'number')


def test_grammar_string_type(grammar, ebnf):
    grammar.string_type()
    ebnf.token.assert_called_with('string_type', 'string')


def test_grammar_list_type(grammar, ebnf):
    grammar.list_type()
    ebnf.token.assert_called_with('list_type', 'list')


def test_grammar_object_type(grammar, ebnf):
    grammar.object_type()
    ebnf.token.assert_called_with('object_type', 'object')


def test_grammar_regexp_type(grammar, ebnf):
    grammar.regexp_type()
    ebnf.token.assert_called_with('regexp_type', 'regexp')


def test_grammar_types(patch, grammar, ebnf):
    patch.many(Grammar, ['int_type', 'float_type', 'number_type',
                         'string_type', 'list_type', 'object_type',
                         'regexp_type', 'function_type'])
    grammar.types()
    assert grammar.int_type.call_count == 1
    assert grammar.float_type.call_count == 1
    assert grammar.number_type.call_count == 1
    assert grammar.string_type.call_count == 1
    assert grammar.list_type.call_count == 1
    assert grammar.object_type.call_count == 1
    assert grammar.regexp_type.call_count == 1
    assert grammar.function_type.call_count == 1
    definitions = (['int_type'], ['float_type'], ['string_type'],
                   ['list_type'], ['object_type'], ['regexp_type'],
                   ['function_type'])
    ebnf.rules.assert_called_with('types', *definitions)


def test_grammar_comment(grammar, ebnf):
    grammar.comment()
    token = token = '/(?<=###)\s(.*|\\n)+(?=\s###)|#(.*)/'
    ebnf.token.assert_called_with('comment', token, regexp=True)
    ebnf.rule.assert_called_with('comment', 'COMMENT+', raw=True)


def test_grammar_build(patch, grammar):
    patch.many(Grammar, ['line', 'spaces', 'values', 'expression', 'comment',
                         'block', 'comparisons', 'assignment', 'imports',
                         'types', 'return_statement'])
    result = grammar.build()
    grammar.ebnf.start.assert_called_with('_NL? block')
    assert Grammar.line.call_count == 1
    assert Grammar.spaces.call_count == 1
    assert Grammar.values.call_count == 1
    assert Grammar.expression.call_count == 1
    assert Grammar.assignment.call_count == 1
    assert Grammar.return_statement.call_count == 1
    assert Grammar.block.call_count == 1
    assert Grammar.imports.call_count == 1
    assert Grammar.comparisons.call_count == 1
    assert Grammar.types.call_count == 1
    assert Grammar.comment.call_count == 1
    assert result == grammar.ebnf.build()
