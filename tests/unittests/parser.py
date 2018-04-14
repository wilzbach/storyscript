# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from pytest import fixture, raises

from storyscript.grammar import Grammar
from storyscript.parser import Parser


@fixture
def parser():
    return Parser('source')


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


def test_parser_line(grammar, parser):
    parser.line(grammar)
    grammar.rule.assert_called_with('line', ['values', 'assignments',
                                             'statements', 'comment'])


def test_parser_string(grammar, parser):
    parser.string(grammar)
    definitions = ['STRING_INNER WORD STRING_INNER',
                   'DOUBLE_QUOTES WORD DOUBLE_QUOTES']
    grammar.rule.assert_called_with('string', definitions)
    grammar.terminal.assert_called_with('DOUBLE_QUOTES', '("\\\""|/[^"]/)')
    grammar.loads.assert_called_with(['common.WORD', 'common.STRING_INNER'])


def test_parser_values(grammar, parser):
    parser.values(grammar)
    grammar.rule.assert_called_with('values', ['INT', 'string', 'list'])
    grammar.loads.assert_called_with(['common.INT'])


def test_parser_list(grammar, parser):
    parser.list(grammar)
    definitions = ['OSB (values (COMMA values)*)? CSB']
    grammar.rule.assert_called_with('list', definitions)
    assert grammar.terminal.call_count == 3


def test_parser_assignments(grammar, parser):
    parser.assignments(grammar)
    grammar.rule.assert_called_with('assignments', ['WORD EQUALS values'])
    grammar.terminal.assert_called_with('equals', '"="')


def test_parser_if_statement(grammar, parser):
    parser.if_statement(grammar)
    grammar.rule.assert_called_with('if_statement', ['IF WS WORD'])
    grammar.terminal.assert_called_with('IF', '"if"')
    grammar.load.assert_called_with('common.WS')


def test_parser_for_statement(grammar, parser):
    parser.for_statement(grammar)
    definitions = ['FOR WS WORD WS IN WS WORD']
    grammar.rule.assert_called_with('for_statement', definitions)
    assert grammar.terminal.call_count == 2


def test_parser_foreach_statement(grammar, parser):
    parser.foreach_statement(grammar)
    definitions = ['FOREACH WS WORD WS AS WS WORD']
    grammar.rule.assert_called_with('foreach_statement', definitions)
    assert grammar.terminal.call_count == 2


def test_parser_wait_statement(grammar, parser):
    parser.wait_statement(grammar)
    definitions = ['WAIT WS WORD', 'WAIT WS string']
    grammar.rule.assert_called_with('wait_statement', definitions)
    grammar.terminal.assert_called_with('WAIT', '"wait"')


def test_parser_statements(grammar, parser):
    parser.statements(grammar)
    definitions = ['if_statement', 'for_statement', 'foreach_statement',
                   'wait_statement']
    grammar.rule.assert_called_with('statements', definitions)


def test_parser_comment(grammar, parser):
    parser.comment(grammar)
    grammar.rule.assert_called_with('comment', ['COMMENT WS?'])
    grammar.terminal.assert_called_with('COMMENT', '/#(.*)/')
def test_parser_grammar(patch, parser):
    patch.init(Grammar)
    patch.many(Grammar, ['start', 'build'])
    patch.many(parser, ['line', 'string', 'values', 'list', 'assignments',
                        'if_statement', 'for_statement', 'foreach_statement',
                        'wait_statement', 'statements', 'comment'])
    result = parser.grammar()
    Grammar.start.assert_called_with('line')
    assert parser.line.call_count == 1
    assert parser.string.call_count == 1
    assert parser.values.call_count == 1
    assert parser.list.call_count == 1
    assert parser.assignments.call_count == 1
    assert parser.if_statement.call_count == 1
    assert parser.for_statement.call_count == 1
    assert parser.foreach_statement.call_count == 1
    assert parser.wait_statement.call_count == 1
    assert parser.statements.call_count == 1
    assert parser.comment.call_count == 1
    assert Grammar.build.call_count == 1
    assert result == Grammar.build()


def test_parser_parse(patch, parser):
    """
    Ensures the build method can build the grammar
    """
    patch.init(Lark)
    patch.object(Lark, 'parse')
    patch.object(Parser, 'grammar')
    result = parser.parse()
    Lark.__init__.assert_called_with(Parser.grammar(), parser=parser.algo)
    Lark.parse.assert_called_with('source')
    assert result == Lark.parse()


def test_parser_parse_unexpected_token(patch, parser):
    patch.init(Lark)
    patch.object(Lark, 'parse', side_effect=UnexpectedToken('', '', '', ''))
    patch.object(Parser, 'grammar')
    assert parser.parse() is None
