# -*- coding: utf-8 -*-
import json
import os

from pytest import fixture

from storyscript.app import App
from storyscript.bundle import Bundle
from storyscript.parser import Grammar
from storyscript.story import Story


@fixture
def bundle(patch):
    patch.init(Bundle)
    patch.many(Bundle, ['bundle_trees', 'bundle', 'lex'])


def test_app_parse(bundle):
    """
    Ensures App.parse returns the parsed bundle
    """
    result = App.parse('path')
    Bundle.__init__.assert_called_with('path')
    Bundle.bundle_trees.assert_called_with(ebnf=None, debug=None)
    assert result == Bundle.bundle_trees()


def test_app_parse_ebnf(bundle):
    """
    Ensures App.parse supports specifying an ebnf
    """
    App.parse('path', ebnf='ebnf')
    Bundle.bundle_trees.assert_called_with(ebnf='ebnf', debug=None)


def test_app_parse_debug(bundle):
    """
    Ensures App.parse can run in debug mode
    """
    App.parse('path', debug=True)
    Bundle.bundle_trees.assert_called_with(ebnf=None, debug=True)


def test_app_compile(patch, bundle):
    patch.object(json, 'dumps')
    result = App.compile('path')
    Bundle.__init__.assert_called_with('path')
    Bundle.bundle.assert_called_with(ebnf=None, debug=False)
    json.dumps.assert_called_with(Bundle.bundle(), indent=2)
    assert result == json.dumps()


def test_app_compile_ebnf(patch, bundle):
    """
    Ensures App.compile supports specifying an ebnf file
    """
    patch.object(json, 'dumps')
    App.compile('path', ebnf='ebnf')
    Bundle.bundle.assert_called_with(ebnf='ebnf', debug=False)


def test_app_compile_debug(patch, bundle):
    patch.object(json, 'dumps')
    App.compile('path', debug='debug')
    Bundle.bundle.assert_called_with(ebnf=None, debug='debug')


def test_app_lex(bundle):
    result = App.lex('/path')
    Bundle.__init__.assert_called_with('/path')
    Bundle.lex.assert_called_with(ebnf=None)
    assert result == Bundle.lex()


def test_app_lex_ebnf(bundle):
    App.lex('/path', ebnf='my.ebnf')
    Bundle.lex.assert_called_with(ebnf='my.ebnf')


def test_app_grammar(patch):
    patch.init(Grammar)
    patch.object(Grammar, 'build')
    assert App.grammar() == Grammar().build()
