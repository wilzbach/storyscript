# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from pytest import fixture, raises

from storyscript.parser import CustomIndenter, Grammar, Parser


@fixture
def parser():
    return Parser('source')


@fixture
def grammar(magic, parser):
    grammar = magic()
    parser.grammar = grammar
    return grammar


def test_parser_init():
    parser = Parser('source')
    assert parser.source == 'source'
    assert parser.algo == 'lalr'


def test_parser_init_algo():
    parser = Parser('source', algo='algo')
    assert parser.algo == 'algo'


def test_parser_line(parser, grammar):
    parser.line()
    defintions = (['values'], ['assignments'], ['operation'], ['statements'],
                  ['comment'], ['command'], ['block'])
    grammar.rules.assert_called_with('line', *defintions)


def test_parser_whitespaces(parser, grammar):
    parser.whitespaces()
    tokens = (('ws', '(" ")+'), ('nl', r'/(\r?\n[\t ]*)+/'))
    grammar.tokens.assert_called_with(*tokens, inline=True, regexp=True)


def test_parser_indentation(parser, grammar):
    parser.indentation()
    tokens = (('indent', '<INDENT>'), ('dedent', '<DEDENT>'))
    grammar.tokens.assert_called_with(*tokens, inline=True)


def test_parser_spaces(patch, parser):
    patch.many(Parser, ['whitespaces', 'indentation'])
    parser.spaces()
    assert Parser.whitespaces.call_count == 1
    assert Parser.indentation.call_count == 1


def test_parser_block(parser, grammar):
    parser.block()
    definition = 'line _NL [_INDENT block+ _DEDENT]'
    grammar.rule.assert_called_with('block', definition, raw=True)


def test_parser_number(parser, grammar):
    parser.number()
    grammar.loads.assert_called_with(['int', 'float'])
    grammar.rules.assert_called_with('number', ['int'], ['float'])


def test_parser_string(parser, grammar):
    parser.string()
    tokens = (('single_quoted', "/'([^']*)'/"),
              ('double_quoted', '/"([^"]*)"/'))
    grammar.tokens.assert_called_with(*tokens, regexp=True)
    definitions = (['single_quoted'], ['double_quoted'])
    grammar.rules.assert_called_with('string', *definitions)


def test_parser_boolean(parser, grammar):
    parser.boolean()
    grammar.tokens.assert_called_with(('true', 'true'), ('false', 'false'))
    grammar.rules.assert_called_with('boolean', ['true'], ['false'])


def test_parser_filepath(parser, grammar):
    parser.filepath()
    grammar.token.assert_called_with('filepath', '/`([^"]*)`/', regexp=True)


def test_parser_values(patch, parser, grammar):
    patch.many(Parser, ['number', 'string', 'list', 'filepath', 'boolean'])
    parser.values()
    assert Parser.number.call_count == 1
    assert Parser.string.call_count == 1
    assert Parser.boolean.call_count == 1
    assert Parser.filepath.call_count == 1
    assert Parser.list.call_count == 1
    definitions = (['number'], ['string'], ['boolean'], ['filepath'], ['list'])
    grammar.rules.assert_called_with('values', *definitions)


def test_parser_operator(parser, grammar):
    parser.operator()
    tokens = (('plus', '+'), ('minus', '-'), ('multiplier', '*'),
              ('division', '/'))
    grammar.tokens.assert_called_with(*tokens)
    definitions = (['plus'], ['minus'], ['multiplier'], ['division'])
    grammar.rules.assert_called_with('operator', *definitions)


def test_parser_operation(patch, parser, grammar):
    patch.object(Parser, 'operator')
    parser.operation()
    assert Parser.operator.call_count == 1
    definitions = (('values', 'ws', 'operator', 'ws', 'values'),
                   ('values', 'operator', 'values'))
    grammar.rules.assert_called_with('operation', *definitions)


def test_parser_list(parser, grammar):
    parser.list()
    tokens = (('comma', ','), ('osb', '['), ('csb', ']'))
    grammar.tokens.assert_called_with(*tokens, inline=True)
    definition ='_OSB (values (_COMMA values)*)? _CSB'
    grammar.rule.assert_called_with('list', definition, raw=True)


def test_parser_key_value(parser, grammar):
    parser.key_value()
    grammar.token.assert_called_with('colon', ':')
    grammar.rule.assert_called_with('key_value', ('string', 'colon', 'values'))


def test_parser_assignments(parser, grammar):
    parser.assignments()
    grammar.load.assert_called_with('word')
    grammar.rule.assert_called_with('assignments', ('word', 'equals',
                                    'values'))
    grammar.token.assert_called_with('equals', '=')


def test_parser_comparisons(parser, grammar):
    parser.comparisons()
    tokens = (('greater', '>'), ('greater_equal', '>='), ('lesser', '<'),
              ('lesser_equal', '<='), ('not', '!='), ('equal', '=='))
    grammar.tokens.assert_called_with(*tokens)
    definitions = (['greater'], ['greater_equal'], ['lesser'], ['lesser_equal'],
                   ['not'], ['equal'])
    grammar.rules.assert_called_with('comparisons', *definitions)


def test_parser_if_statement(parser, grammar):
    parser.if_statement()
    definitions = (('if', 'ws', 'word'),
                   ('if', 'ws', 'word', 'ws', 'comparisons', 'ws', 'word'))
    grammar.rules.assert_called_with('if_statement', *definitions)
    grammar.token.assert_called_with('if', 'if')


def test_parser_else_statement(parser, grammar):
    parser.else_statement()
    grammar.token.assert_called_with('else', 'else')
    grammar.rule.assert_called_with('else_statement', ['else'])


def test_parser_elseif_statement(parser, grammar):
    parser.elseif_statement()
    rule = 'ELSE _WS? IF _WS WORD [_WS comparisons _WS WORD]?'
    grammar.rule.assert_called_with('elseif_statement', rule, raw=True)


def test_parser_for_statement(parser, grammar):
    parser.for_statement()
    definition = ('for', 'ws', 'word', 'ws', 'in', 'ws', 'word')
    grammar.rule.assert_called_with('for_statement', definition)
    grammar.tokens.assert_called_with(('for', 'for'), ('in', 'in'))


def test_parser_foreach_statement(parser, grammar):
    parser.foreach_statement()
    definition = ('foreach', 'ws', 'word', 'ws', 'as', 'ws', 'word')
    grammar.rule.assert_called_with('foreach_statement', definition)
    grammar.tokens.assert_called_with(('foreach', 'foreach'), ('as', 'as'))


def test_parser_wait_statement(parser, grammar):
    parser.wait_statement()
    definitions = (('wait', 'ws', 'word'), ('wait', 'ws', 'string'))
    grammar.rules.assert_called_with('wait_statement', *definitions)
    grammar.token.assert_called_with('wait', 'wait')


def test_parser_next_statement(parser, grammar):
    parser.next_statement()
    grammar.token.assert_called_with('next', 'next')
    definitions = (('next', 'ws', 'word'), ('next', 'ws', 'filepath'))
    grammar.rules.assert_called_with('next_statement', *definitions)


def test_parser_statements(patch, parser, grammar):
    patch.many(Parser, ['if_statement', 'for_statement', 'foreach_statement',
                        'wait_statement', 'next_statement', 'else_statement',
                        'elseif_statement'])
    parser.statements()
    assert Parser.if_statement.call_count == 1
    assert Parser.for_statement.call_count == 1
    assert Parser.foreach_statement.call_count == 1
    assert Parser.wait_statement.call_count == 1
    assert Parser.next_statement.call_count == 1
    assert Parser.else_statement.call_count == 1
    assert Parser.elseif_statement.call_count == 1
    child_rules = (['if_statement'], ['for_statement'], ['foreach_statement'],
                    ['wait_statement'], ['next_statement'], ['else_statement'],
                    ['elseif_statement'])
    grammar.rules.assert_called_with('statements', *child_rules)


def test_parser_options(parser, grammar):
    parser.options()
    definitions = (('dash', 'dash', 'word', 'ws', 'word'),
                   ('dash', 'dash', 'word', 'ws', 'values'))
    grammar.rules.assert_called_with('options', *definitions)


def test_parser_arguments(patch, parser, grammar):
    patch.object(Parser, 'options')
    parser.arguments()
    assert Parser.options.call_count == 1
    definitions = (['ws', 'values'], ['ws', 'word'], ['ws', 'options'])
    grammar.rules.assert_called_with('arguments', *definitions)


def test_parser_command(patch, parser, grammar):
    patch.object(Parser, 'arguments')
    parser.command()
    assert Parser.arguments.call_count == 1
    rule = 'RUN _WS WORD arguments*|WORD arguments*'
    grammar.rule.assert_called_with('command', rule, raw=True)


def test_parser_comment(parser, grammar):
    parser.comment()
    grammar.rule.assert_called_with('comment', ['comment'])
    grammar.token.assert_called_with('comment', '/#(.*)/', regexp=True)


def test_parser_get_grammar(patch, parser):
    patch.init(Grammar)
    assert isinstance(parser.get_grammar(), Grammar)


def test_parser_indenter(patch, parser):
    patch.init(CustomIndenter)
    assert isinstance(parser.indenter(), CustomIndenter)


def test_parser_build_grammar(patch, parser):
    patch.many(Parser, ['line', 'spaces', 'values', 'assignments', 'operation',
                        'statements', 'comment', 'block', 'comparisons',
                        'command', 'get_grammar'])
    result = parser.build_grammar()
    assert parser.grammar == parser.get_grammar()
    parser.grammar.start.assert_called_with('_NL? block')
    assert Parser.line.call_count == 1
    assert Parser.spaces.call_count == 1
    assert Parser.values.call_count == 1
    assert Parser.assignments.call_count == 1
    assert Parser.operation.call_count == 1
    assert Parser.statements.call_count == 1
    assert Parser.comment.call_count == 1
    assert Parser.block.call_count == 1
    assert Parser.comparisons.call_count == 1
    assert Parser.command.call_count == 1
    assert result == parser.grammar.build()


def test_parser_parse(patch, parser):
    """
    Ensures the build method can build the grammar
    """
    patch.init(Lark)
    patch.object(Lark, 'parse')
    patch.many(Parser, ['build_grammar', 'indenter'])
    result = parser.parse()
    Lark.__init__.assert_called_with(Parser.build_grammar(),
                                     parser=parser.algo,
                                     postlex=Parser.indenter())
    Lark.parse.assert_called_with('source')
    assert result == Lark.parse()


def test_parser_parse_unexpected_token(patch, parser):
    patch.init(Lark)
    patch.object(Lark, 'parse', side_effect=UnexpectedToken('', '', '', ''))
    patch.many(Parser, ['build_grammar', 'indenter'])
    assert parser.parse() is None
