# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from pytest import fixture, raises

from storyscript.parser import CustomIndenter, Grammar, Parser


@fixture
def parser():
    return Parser('source')


@fixture
def g(magic, parser):
    grammar = magic()
    parser.grammar = grammar
    return grammar


@fixture
def grammar(magic):
    return magic()


def test_parser_init():
    parser = Parser('source')
    assert parser.source == 'source'
    assert parser.algo == 'lalr'


def test_parser_init_algo():
    parser = Parser('source', algo='algo')
    assert parser.algo == 'algo'


def test_parser_add_rules(patch, parser):
    patch.many(Parser, ['line', 'spaces', 'values', 'assignments',
                        'statements', 'comment', 'block', 'comparisons'])
    parser.add_rules()
    assert Parser.line.call_count == 1
    assert Parser.spaces.call_count == 1
    assert Parser.values.call_count == 1
    assert Parser.assignments.call_count == 1
    assert Parser.statements.call_count == 1
    assert Parser.comment.call_count == 1
    assert Parser.block.call_count == 1
    assert Parser.comparisons.call_count == 1


def test_parser_line(parser, g):
    parser.line()
    rules = ['values', 'assignments', 'statements', 'comment', 'block']
    g.rule.assert_called_with('line', rules)


def test_parser_whitespace(parser, g):
    parser.whitespace()
    g.terminal.assert_called_with('WS', '(" ")+', inline=True)


def test_parser_newline(parser, g):
    parser.newline()
    g.terminal.assert_called_with('NL', r'/(\r?\n[\t ]*)+/', inline=True)


def test_parser_indent(parser, g):
    parser.indent()
    g.terminal.assert_called_with('INDENT', '"<INDENT>"', inline=True)


def test_parser_dedent(parser, g):
    parser.dedent()
    g.terminal.assert_called_with('DEDENT', '"<DEDENT>"', inline=True)


def test_parser_spaces(patch, parser):
    patch.many(Parser, ['whitespace', 'newline', 'indent', 'dedent'])
    parser.spaces()
    assert Parser.whitespace.call_count == 1
    assert Parser.newline.call_count == 1
    assert Parser.indent.call_count == 1
    assert Parser.dedent.call_count == 1


def test_parser_block(parser, g):
    parser.block()
    rules = ['line _NL [_INDENT block+ _DEDENT]']
    g.rule.assert_called_with('block', rules)


def test_parser_number(parser, g):
    parser.number()
    g.rule.assert_called_with('number', ['FLOAT', 'INT'])
    g.loads.assert_called_with(['INT', 'FLOAT'])


def test_parser_string(parser, g):
    parser.string()
    definitions = (('single_quotes', 'word', 'single_quotes'),
                   ('double_quotes', 'word', 'double_quotes'))
    tokens = (('single_quotes', """("\\\'"|/[^']/)"""),
              ('double_quotes', '("\\\""|/[^"]/)'))
    g.rules.assert_called_with('string', *definitions)
    g.tokens.assert_called_with(*tokens, inline=True, regexp=True)
    g.load.assert_called_with('WORD')


def test_parser_values(patch, parser, g):
    patch.many(Parser, ['number', 'string', 'list'])
    parser.values()
    assert Parser.number.call_count == 1
    assert Parser.string.call_count == 1
    assert Parser.list.call_count == 1
    g.rules.assert_called_with('values', ('number'), ('string'), ('list'))


def test_parser_list(grammar, parser):
    parser.list(grammar)
    definitions = ['_OSB (values (_COMMA values)*)? _CSB']
    grammar.rule.assert_called_with('list', definitions)
    assert grammar.terminal.call_count == 3


def test_parser_assignments(parser, g):
    parser.assignments()
    g.rule.assert_called_with('assignments', ('word', 'equals', 'values'))
    g.token.assert_called_with('equals', '=')


def test_parser_comparisons(grammar, parser):
    parser.comparisons(grammar)
    assert grammar.terminal.call_count == 6


def test_parser_if_statement(parser, g):
    parser.if_statement()
    g.rule.assert_called_with('if_statement', ('if', 'ws', 'word'))
    g.token.assert_called_with('if', 'if')


def test_parser_for_statement(parser, g):
    parser.for_statement()
    definition = ('for', 'ws', 'word', 'in', 'ws', 'word')
    g.rule.assert_called_with('for_statement', definition)
    g.tokens.assert_called_with(('for', 'for'), ('in', 'in'))


def test_parser_foreach_statement(parser, g):
    parser.foreach_statement()
    definition = ('foreach', 'ws', 'word', 'ws', 'as', 'ws', 'word')
    g.rule.assert_called_with('foreach_statement', definition)
    g.tokens.assert_called_with(('foreach', 'foreach'), ('as', 'as'))


def test_parser_wait_statement(grammar, parser):
    parser.wait_statement(grammar)
    definitions = ['WAIT _WS WORD', 'WAIT _WS string']
    grammar.rule.assert_called_with('wait_statement', definitions)
    grammar.terminal.assert_called_with('WAIT', '"wait"')


def test_parser_statements(patch, grammar, parser):
    patch.object(Parser, 'add_rules')
    parser.statements(grammar)
    definitions = ['if_statement', 'for_statement', 'foreach_statement',
                   'wait_statement']
    Parser.add_rules.assert_called_with(grammar, definitions)
    grammar.rule.assert_called_with('statements', definitions)


def test_parser_comment(grammar, parser):
    parser.comment(grammar)
    grammar.rule.assert_called_with('comment', ['COMMENT'])
    grammar.terminal.assert_called_with('COMMENT', '/#(.*)/')


def test_parser_get_grammar(patch, parser):
    patch.init(Grammar)
    assert isinstance(parser.get_grammar(), Grammar)


def test_parser_indenter(patch, parser):
    patch.init(CustomIndenter)
    assert isinstance(parser.indenter(), CustomIndenter)


def test_parser_build_grammar(patch, parser):
    patch.many(Parser, ['get_grammar', 'add_rules'])
    result = parser.build_grammar()
    assert parser.grammar == parser.get_grammar()
    parser.grammar.start.assert_called_with('_NL? block')
    rules = ['line', 'spaces', 'values', 'assignments', 'statements',
             'comment', 'block', 'comparisons']
    Parser.add_rules.assert_called_with(parser.grammar, rules)
    assert parser.grammar.build.call_count == 1
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
