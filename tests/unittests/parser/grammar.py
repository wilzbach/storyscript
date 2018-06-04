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
    defintions = (['values'], ['operation'], ['comment'], ['statement'],
                  ['block'])
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


def test_grammar_block(patch, grammar, ebnf):
    patch.many(Grammar, ['if_block', 'foreach_block'])
    grammar.block()
    assert Grammar.if_block.call_count == 1
    assert Grammar.foreach_block.call_count == 1
    definition = 'line _NL nested_block?|if_block|foreach_block'
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


def test_grammar_filepath(grammar, ebnf):
    grammar.filepath()
    ebnf.token.assert_called_with('filepath', '/`([^"]*)`/', regexp=True)


def test_grammar_values(patch, grammar, ebnf):
    patch.many(Grammar, ['number', 'string', 'list', 'objects', 'filepath',
                         'boolean'])
    grammar.values()
    assert Grammar.number.call_count == 1
    assert Grammar.string.call_count == 1
    assert Grammar.boolean.call_count == 1
    assert Grammar.filepath.call_count == 1
    assert Grammar.list.call_count == 1
    assert Grammar.objects.call_count == 1
    definitions = (['number'], ['string'], ['boolean'], ['filepath'], ['list'],
                   ['objects'])
    ebnf.rules.assert_called_with('values', *definitions)


def test_grammar_operator(grammar, ebnf):
    grammar.operator()
    tokens = (('plus', '+'), ('dash', '-'), ('multiplier', '*'),
              ('bslash', '/'))
    ebnf.tokens.assert_called_with(*tokens)
    definitions = (['plus'], ['dash'], ['multiplier'], ['bslash'])
    ebnf.rules.assert_called_with('operator', *definitions)


def test_grammar_operation(patch, grammar, ebnf):
    patch.object(Grammar, 'operator')
    grammar.operation()
    assert Grammar.operator.call_count == 1
    definitions = (('values', 'ws', 'operator', 'ws', 'values'),
                   ('values', 'operator', 'values'))
    ebnf.rules.assert_called_with('operation', *definitions)


def test_grammar_list(grammar, ebnf):
    grammar.list()
    tokens = (('comma', ','), ('osb', '['), ('csb', ']'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)
    definition = '_OSB (values (_COMMA _WS? values)*)? _CSB'
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
    ebnf.token.assert_called_with('name', '/[a-zA-Z-\/]+/', regexp=True)
    Grammar.path_fragment.call_count == 1
    ebnf.rule.assert_called_with('path', 'NAME (path_fragment)*', raw=True)


def test_grammar_assignment_fragment(patch, grammar, ebnf):
    grammar.assignment_fragment()
    ebnf.token.assert_called_with('equals', '=')
    rule = 'EQUALS _WS? (values|path)'
    ebnf.rule.assert_called_with('assignment_fragment', rule, raw=True)


def test_grammar_statement(patch, grammar, ebnf):
    patch.many(Grammar, ['assignment_fragment', 'service_fragment', 'path'])
    grammar.statement()
    assert Grammar.path.call_count == 1
    assert Grammar.assignment_fragment.call_count == 1
    assert Grammar.service_fragment.call_count == 1
    assignment = 'path _WS? assignment_fragment -> assignment'
    service = 'path service_fragment -> service'
    rule = '{}|{}'.format(assignment, service)
    ebnf.rule.assert_called_with('statement', rule, raw=True)


def test_grammar_comparisons(grammar, ebnf):
    grammar.comparisons()
    tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
              ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
    ebnf.tokens.assert_called_with(*tokens)
    definitions = (['greater'], ['greater_equal'], ['lesser'],
                   ['lesser_equal'], ['not'], ['equal'])
    ebnf.rules.assert_called_with('comparisons', *definitions)


def test_grammar_if_statement(grammar, ebnf):
    grammar.if_statement()
    definitions = (('if', 'ws', 'name'),
                   ('if', 'ws', 'name', 'ws', 'comparisons', 'ws', 'name'))
    ebnf.rules.assert_called_with('if_statement', *definitions)
    ebnf.token.assert_called_with('if', 'if')


def test_grammar_else_statement(grammar, ebnf):
    grammar.else_statement()
    ebnf.token.assert_called_with('else', 'else')
    ebnf.rule.assert_called_with('else_statement', ['else'])


def test_grammar_elseif_statement(grammar, ebnf):
    grammar.elseif_statement()
    rule = 'ELSE _WS? IF _WS NAME [_WS comparisons _WS NAME]?'
    ebnf.rule.assert_called_with('elseif_statement', rule, raw=True)


def test_grammar_foreach_statement(grammar, ebnf):
    grammar.foreach_statement()
    definition = ('foreach', 'ws', 'name', 'output')
    ebnf.rule.assert_called_with('foreach_statement', definition)
    tokens = (('foreach', 'foreach'), ('as', 'as'))
    ebnf.tokens.assert_called_with(*tokens, inline=True)


def test_grammar_arguments(grammar, ebnf):
    grammar.arguments()
    rule = '_WS NAME _COLON (values|path)'
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
    rule = 'command? arguments* output?'
    ebnf.rule.assert_called_with('service_fragment', rule, raw=True)


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
    ebnf.rule.assert_called_with('comment', ['comment'])
    ebnf.token.assert_called_with('comment', '/#(.*)/', regexp=True)


def test_grammar_build(patch, grammar):
    patch.many(Grammar, ['line', 'spaces', 'values', 'operation', 'comment',
                         'block', 'comparisons', 'statement', 'types'])
    result = grammar.build()
    grammar.ebnf.start.assert_called_with('_NL? block')
    assert Grammar.line.call_count == 1
    assert Grammar.spaces.call_count == 1
    assert Grammar.values.call_count == 1
    assert Grammar.operation.call_count == 1
    assert Grammar.statement.call_count == 1
    assert Grammar.block.call_count == 1
    assert Grammar.comparisons.call_count == 1
    assert Grammar.types.call_count == 1
    assert Grammar.comment.call_count == 1
    assert result == grammar.ebnf.build()
