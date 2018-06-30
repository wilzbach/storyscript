# -*- coding: utf-8 -*-
import os

from lark import Lark
from lark.common import UnexpectedToken

from pytest import fixture, raises

from storyscript.parser import CustomIndenter, Grammar, Parser, Transformer


@fixture
def parser():
    return Parser()


@fixture
def ebnf_file(request):
    with open('test.ebnf', 'w') as f:
        f.write('grammar')

    def teardown():
        os.remove('test.ebnf')
    request.addfinalizer(teardown)


def test_parser_init(parser):
    assert parser.algo == 'lalr'
    assert parser.ebnf_file is None


def test_parser_init_algo():
    parser = Parser(algo='algo')
    assert parser.algo == 'algo'


def test_parser_init_ebnf_file():
    parser = Parser(ebnf_file='grammar.ebnf')
    assert parser.ebnf_file == 'grammar.ebnf'


def test_parser_make_message():
    template = ('Failed reading story because of unexpected "{}" at'
                'line {}, column {}')
    result = Parser.make_message(1, 2, 3)
    assert result == template.format(1, 2, 3)


def test_parser_error_message(patch, magic):
    patch.object(Parser, 'make_message')
    error = magic()
    result = Parser.error_message(error)
    Parser.make_message.assert_called_with(error.token.value, error.line,
                                           error.column)
    assert result == Parser.make_message().encode().decode()


def test_parser_indenter(patch, parser):
    patch.init(CustomIndenter)
    assert isinstance(parser.indenter(), CustomIndenter)


def test_parser_transfomer(patch, parser):
    patch.init(Transformer)
    assert isinstance(parser.transformer(), Transformer)


def test_parser_grammar(patch, parser):
    patch.init(Grammar)
    patch.object(Grammar, 'build')
    result = parser.grammar()
    assert Grammar.__init__.call_count == 1
    assert result == Grammar().build()


def test_parser_grammar_ebnf_file(parser, ebnf_file):
    parser.ebnf_file = 'test.ebnf'
    assert parser.grammar() == 'grammar'


def test_parser_lark(patch, parser):
    patch.init(Lark)
    patch.many(Parser, ['indenter', 'grammar'])
    result = parser.lark()
    Lark.__init__.assert_called_with(parser.grammar(),
                                     parser=parser.algo,
                                     postlex=Parser.indenter())
    assert isinstance(result, Lark)


def test_parser_parse(patch, parser):
    """
    Ensures the build method can build the grammar
    """
    patch.many(Parser, ['lark', 'transformer'])
    result = parser.parse('source')
    Parser.lark().parse.assert_called_with('source\n')
    Parser.transformer().transform.assert_called_with(Parser.lark().parse())
    assert result == Parser.transformer().transform()


def test_parser_parser_unexpected_token(capsys, patch, magic, parser):
    patch.many(Parser, ['lark', 'transformer', 'error_message'])
    Parser.lark().parse.side_effect = UnexpectedToken(magic(), 'exp', 0, 1)
    with raises(SystemExit):
        parser.parse('source', debug=False)
    out, err = capsys.readouterr()
    assert out == '{}\n'.format(Parser.error_message())


def test_parser_parser_unexpected_token_debug(patch, magic, parser):
    patch.many(Parser, ['lark', 'transformer', 'error_message'])
    Parser.lark().parse.side_effect = UnexpectedToken(magic(), 'exp', 0, 1)
    with raises(UnexpectedToken):
        parser.parse('source', debug=True)


def test_parser_lex(patch, parser):
    patch.many(Parser, ['lark', 'indenter'])
    result = parser.lex('source')
    Parser.lark().lex.assert_called_with('source')
    assert result == Parser.lark().lex()
