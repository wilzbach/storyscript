# -*- coding: utf-8 -*-
from storyscript.parser import Parser


def test_parser_init():
    parser = Parser('source')
    assert parser.source == 'source'
    assert parser.algo == 'lalr'


def test_parser_init_algo():
    parser = Parser('source', algo='algo')
    assert parser.algo == 'algo'


def test_parser_grammar(patch):
    patch.init(Grammar)
    patch.many(Grammar, ['start', 'rule', 'terminal', 'ignore', 'load',
                         'build'])
    result = Parser('source').grammar()
    Grammar.start.assert_called_with('line')
    assert Grammar.build.call_count == 1
    assert result == Grammar.build()
