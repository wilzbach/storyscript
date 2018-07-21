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
    Bundle.bundle.assert_called_with(ebnf_file=None, debug=False)
    json.dumps.assert_called_with(Bundle.bundle(), indent=2)
    assert result == json.dumps()


def test_app_compile_ebnf_file(patch):
    patch.object(json, 'dumps')
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    App.compile('path', ebnf_file='ebnf')
    Bundle.bundle.assert_called_with(ebnf_file='ebnf', debug=False)


def test_app_compile_debug(patch):
    patch.object(json, 'dumps')
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    App.compile('path', debug='debug')
    Bundle.bundle.assert_called_with(ebnf_file=None, debug='debug')


def test_app_lexer(patch):
    patch.object(Story, 'from_file')
    patch.init(Bundle)
    patch.object(Bundle, 'find_stories', return_value=['one.story'])
    result = App.lex('/path')
    Story.from_file.assert_called_with('one.story')
    assert result == {'one.story': Story.from_file().lex()}


def test_app_grammar(patch):
    patch.init(Grammar)
    patch.object(Grammar, 'build')
    assert App.grammar() == Grammar().build()
