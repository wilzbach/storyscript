import os

from ply import yacc

from pytest import mark

from storyscript.lexer import Lexer
from storyscript.parser import Parser
from storyscript.tree import Method


def test_parser_init(mocker):
    mocker.patch.object(os, 'getcwd')
    mocker.patch.object(yacc, 'yacc')
    mocker.patch.object(Lexer, '__init__', return_value=None)
    parser = Parser()
    kwargs = {'module': parser, 'start': 'program', 'optimize': True,
              'debug': False, 'outputdir': os.getcwd()}
    yacc.yacc.assert_called_with(**kwargs)
    Lexer.__init__.assert_called_with(True)
    assert isinstance(parser.lexer, Lexer)
    assert parser.tokens == Lexer().tokens
    assert parser.parser == yacc.yacc()


def test_parser_for_item_in_list(mocker):
    mocker.patch.object(os, 'getcwd')
    mocker.patch.object(yacc, 'yacc')
    mocker.patch.object(Lexer, '__init__', return_value=None)
    parser = Parser()
    p = mocker.MagicMock()
    parser.p_stmt_for_item_in_list(p)


def test_parser_p_wait(magic, patch):
    patch.object(yacc, 'yacc')
    patch.object(Lexer, '__init__', return_value=None)
    patch.init(Method)
    p = magic()
    parser = Parser()
    parser.p_wait(p)
    args = ('wait', parser, p.lineno(1))
    kwargs = {'args': (p[2],), 'enter': None, 'exit': None, 'suite': None}
    Method.__init__.assert_called_with(*args, **kwargs)


@mark.skip(reason='I should mock an object that behaves like a list')
def test_parser_p_wait_suite(magic, patch):
    patch.object(yacc, 'yacc')
    patch.object(Lexer, '__init__', return_value=None)
    patch.init(Method)
    p = magic()
    parser = Parser()
    parser.p_wait(p)
    args = ('wait', parser, p.lineno(1))
    kwargs = {'args': (p[2],), 'enter': p[3][0].lineno,
              'exit': p[3][-1].lineno, 'suite': p[3]}
    Method.__init__.assert_called_with(*args, **kwargs)
