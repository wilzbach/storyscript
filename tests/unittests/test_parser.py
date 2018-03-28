import os

from ply import yacc

from pytest import mark

from storyscript.lexer import Lexer
from storyscript.parser import Parser
from storyscript.tree import File, Method


def test_parser_init(patch):
    patch.object(os, 'getcwd')
    patch.object(yacc, 'yacc')
    patch.init(Lexer)
    parser = Parser()
    kwargs = {'module': parser, 'start': 'program', 'optimize': True,
              'debug': False, 'outputdir': os.getcwd()}
    yacc.yacc.assert_called_with(**kwargs)
    Lexer.__init__.assert_called_with(True)
    assert isinstance(parser.lexer, Lexer)
    assert parser.tokens == Lexer().tokens
    assert parser.parser == yacc.yacc()


def test_parser_for_item_in_list(patch, magic):
    patch.object(yacc, 'yacc')
    patch.init(Lexer)
    patch.init(Method)
    parser = Parser()
    p = magic()
    parser.p_stmt_for_item_in_list(p)
    args = ('for', parser, p.lineno())
    kwargs = {'args': [p[2], p[4]], 'suite': p[5], 'enter': p[5][0].lineno}
    Method.__init__.assert_called_with(*args, **kwargs)


def test_parser_p_wait(magic, patch):
    patch.object(yacc, 'yacc')
    patch.init(Lexer)
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
    patch.init(Lexer)
    patch.init(Method)
    p = magic()
    parser = Parser()
    parser.p_wait(p)
    args = ('wait', parser, p.lineno(1))
    kwargs = {'args': (p[2],), 'enter': p[3][0].lineno,
              'exit': p[3][-1].lineno, 'suite': p[3]}
    Method.__init__.assert_called_with(*args, **kwargs)


def test_parser_p_file_inner(patch, magic):
    patch.object(yacc, 'yacc')
    patch.init(Lexer)
    patch.init(File)
    p = magic()
    parser = Parser()
    parser.p_file_inner(p)
    File.__init__.assert_called_with(p[1])


def test_parser_p_file(patch, magic):
    patch.object(yacc, 'yacc')
    patch.init(Lexer)
    p = magic()
    parser = Parser()
    parser.p_file(p)
    assert p[0] == p[2]
