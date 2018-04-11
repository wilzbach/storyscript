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
    grammar.rule.assert_called_with('line', ['values', 'assignments'])


def test_parser_values(grammar, parser):
    parser.values(grammar)
    definitions = ['INT', 'STRING_INNER WORD STRING_INNER', 'DQS WORD DQS']
    loads = ['common.INT', 'common.WORD', 'common.STRING_INNER']
    grammar.rule.assert_called_with('values', definitions)
    grammar.loads.assert_called_with(loads)


def test_parser_assignments(grammar, parser):
    parser.assignments(grammar)
    grammar.rule.assert_called_with('assignments', ['WORD EQUALS values'])
    grammar.terminal.assert_called_with('equals', '"="')


def test_parser_grammar(patch, parser):
    patch.init(Grammar)
    patch.many(Grammar, ['start', 'build'])
    patch.many(parser, ['line', 'values', 'assignments'])
    result = parser.grammar()
    Grammar.start.assert_called_with('line')
    assert parser.line.call_count == 1
    assert parser.values.call_count == 1
    assert parser.assignments.call_count == 1
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
