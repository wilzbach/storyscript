# -*- coding: utf-8 -*-
from lark import Lark

from pytest import fixture

from storyscript.grammar import Grammar
from storyscript.parser import Parser


@fixture
def parser():
    return Parser('source')


def test_parser_init():
    parser = Parser('source')
    assert parser.source == 'source'
    assert parser.algo == 'lalr'


def test_parser_init_algo():
    parser = Parser('source', algo='algo')
    assert parser.algo == 'algo'


def test_parser_grammar(patch, parser):
    patch.init(Grammar)
    patch.many(Grammar, ['start', 'rule', 'terminal', 'ignore', 'load',
                         'build'])
    result = parser.grammar()
    Grammar.start.assert_called_with('line')
    assert Grammar.build.call_count == 1
    assert result == Grammar.build()


def test_parser_build(patch, parser):
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
