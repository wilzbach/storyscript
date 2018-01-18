import os

from ply import yacc

from storyscript.lexer import Lexer
from storyscript.parser import Parser


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
