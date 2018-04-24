# -*- coding: utf-8 -*-
from lark import Lark
from lark.common import UnexpectedToken

from pytest import fixture, raises

from storyscript.parser import CustomIndenter, Grammar, Parser


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


def test_parser_add_rules(patch, magic, grammar, parser):
    parser.rule = magic()
    parser.add_rules(grammar, ['rule'])
    parser.rule.assert_called_with(grammar)


def test_parser_line(grammar, parser):
    parser.line(grammar)
    rules = ['values', 'assignments', 'statements', 'comment', 'block']
    grammar.rule.assert_called_with('line', rules)


def test_parser_spaces(grammar, parser):
    parser.spaces(grammar)
    assert grammar.terminal.call_count == 4


def test_parser_block(grammar, parser):
    parser.block(grammar)
    rules = ['line _NL [_INDENT block+ _DEDENT]']
    grammar.rule.assert_called_with('block', rules)


def test_parser_number(grammar, parser):
    parser.number(grammar)
    grammar.rule.assert_called_with('number', ['FLOAT', 'INT'])
    grammar.loads.assert_called_with(['INT', 'FLOAT'])


def test_parser_string(grammar, parser):
    parser.string(grammar)
    definitions = ['STRING_INNER WORD STRING_INNER',
                   'DOUBLE_QUOTES WORD DOUBLE_QUOTES']
    grammar.rule.assert_called_with('string', definitions)
    grammar.terminal.assert_called_with('DOUBLE_QUOTES', '("\\\""|/[^"]/)')
    grammar.loads.assert_called_with(['WORD', 'STRING_INNER'])


def test_parser_values(patch, grammar, parser):
    patch.object(Parser, 'add_rules')
    parser.values(grammar)
    Parser.add_rules.assert_called_with(grammar, ['number', 'string', 'list'])
    grammar.rule.assert_called_with('values', ['number', 'string', 'list'])


def test_parser_list(grammar, parser):
    parser.list(grammar)
    definitions = ['_OSB (values (COMMA values)*)? _CSB']
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


def test_parser_grammar(patch, parser):
    patch.init(Grammar)
    grammar = parser.grammar()
    assert isinstance(grammar, Grammar)


def test_parser_indenter(patch, parser):
    patch.init(CustomIndenter)
    assert isinstance(parser.indenter(), CustomIndenter)


def test_parser_build_grammar(patch, parser):
    patch.many(Parser, ['grammar', 'add_rules'])
    result = parser.build_grammar()
    assert Parser.grammar.call_count == 1
    Parser.grammar().start.assert_called_with('_NL? block')
    rules = ['line', 'spaces', 'values', 'assignments', 'statements',
             'comment', 'block']
    Parser.add_rules.assert_called_with(Parser.grammar(), rules)
    assert Parser.grammar().build.call_count == 1
    assert result == Parser.grammar().build()


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
