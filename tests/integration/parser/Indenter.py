# -*- coding: utf-8 -*-

from lark.lexer import Token

import pytest

from storyscript.parser.Indenter import CustomIndenter

A = Token('A', 'A')
B = Token('B', 'B')
C = Token('C', 'C')
NL = Token('_NL', '\n')
WHILE = Token('_WHILE', 'while')
DEDENT = Token('_DEDENT', '')
OPEN_PAREN = Token('(', '(')
CLOSE_PAREN = Token(')', ')')


def indent_token(level, ws_type=' '):
    ws = ''.join(ws_type for _ in range(level))
    return Token('_NL', '\n' + ws), Token('_INDENT', ws)


def indent_token_dedent(level, ws_type=' '):
    ws = ''.join(ws_type for _ in range(level))
    return (Token('_NL', '\n' + ws), Token('_INDENT', ws),
            Token('_DEDENT', ws), Token('_DOUBLE_DEDENT', ws))


def test_indenter_one_level():
    """
    while
        a
    b
    """
    indenter = CustomIndenter()
    nl, indent = indent_token(4)
    r = list(indenter.process([WHILE, nl, A, NL, B]))
    assert r == [WHILE, nl, indent, A, NL, DEDENT, B]


def test_indenter_one_level_multiple_statements():
    """
    while
        a
        b
    c
    """
    indenter = CustomIndenter()
    nl, indent = indent_token(4)
    r = list(indenter.process([NL, WHILE, nl, A, nl, B, NL, C]))
    assert r == [NL, WHILE, nl, indent, A, nl, B, NL, DEDENT, C]


def test_indenter_two_levels():
    """
    while
        a
            b
    c
    """
    indenter = CustomIndenter()
    nl, indent = indent_token(4)
    nl2, indent2 = indent_token(8)
    r = list(indenter.process([WHILE, nl,
                               A, nl2,
                               B,
                               NL, C]))
    assert r == [WHILE, nl,
                 indent, A, nl2,
                 indent2, B, NL,
                 DEDENT, DEDENT, C]


def test_indenter_double_indent():
    """
    while
            a
        b
    c
    """
    indenter = CustomIndenter()
    nl, indent = indent_token(8)
    nl2, indent2, dedent, double_dedent = indent_token_dedent(4)
    r = list(indenter.process([WHILE, nl,
                               A, nl2,
                               B,
                               NL, C]))
    assert r == [WHILE, nl, indent,
                 A, nl2,
                 dedent, double_dedent, B, NL,
                 DEDENT, C]


def test_increment_paren_level():
    indenter = CustomIndenter()
    indenter.OPEN_PAREN_types = ['(']
    assert indenter.paren_level == 0

    nl, indent = indent_token(4)
    list(indenter.process([OPEN_PAREN]))
    assert indenter.paren_level == 1


def test_decrement_paren_level():
    indenter = CustomIndenter()
    indenter.OPEN_PAREN_types = ['(']
    indenter.CLOSE_PAREN_types = [')']
    assert indenter.paren_level == 0

    nl, indent = indent_token(4)
    list(indenter.process([OPEN_PAREN, OPEN_PAREN, CLOSE_PAREN]))
    assert indenter.paren_level == 1


def test_assert_always_zero_or_more_paren_level():
    indenter = CustomIndenter()
    indenter.CLOSE_PAREN_types = [')']
    assert indenter.paren_level == 0

    nl, indent = indent_token(4)
    with pytest.raises(AssertionError):
        list(indenter.process([CLOSE_PAREN]))
