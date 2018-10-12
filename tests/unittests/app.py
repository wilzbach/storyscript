# -*- coding: utf-8 -*-
import json
import os

from storyscript.app import App
from storyscript.bundle import Bundle
from storyscript.parser import Grammar
from storyscript.story import Story


def test_app_compile(patch):
    patch.object(json, 'dumps')
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    result = App.compile('path')
    Bundle.__init__.assert_called_with('path')
    Bundle.bundle.assert_called_with(ebnf=None, debug=False)
    json.dumps.assert_called_with(Bundle.bundle(), indent=2)
    assert result == json.dumps()


def test_app_compile_ebnf(patch):
    """
    Ensures App.compile supports specifying an ebnf file
    """
    patch.object(json, 'dumps')
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    App.compile('path', ebnf='ebnf')
    Bundle.bundle.assert_called_with(ebnf='ebnf', debug=False)


def test_app_compile_debug(patch):
    patch.object(json, 'dumps')
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    App.compile('path', debug='debug')
    Bundle.bundle.assert_called_with(ebnf=None, debug='debug')


def test_app_lex(patch):
    patch.init(Bundle)
    patch.object(Bundle, 'lex')
    result = App.lex('/path')
    Bundle.__init__.assert_called_with('/path')
    Bundle.lex.assert_called_with(ebnf=None)
    assert result == Bundle.lex()


def test_app_lex_ebnf(patch):
    patch.init(Bundle)
    patch.object(Bundle, 'lex')
    App.lex('/path', ebnf='my.ebnf')
    Bundle.lex.assert_called_with(ebnf='my.ebnf')


def test_app_grammar(patch):
    patch.init(Grammar)
    patch.object(Grammar, 'build')
    assert App.grammar() == Grammar().build()
