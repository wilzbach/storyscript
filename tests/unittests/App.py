# -*- coding: utf-8 -*-
import json

from pytest import fixture, raises

import storyscript.App as AppModule
from storyscript.App import App
from storyscript.Bundle import Bundle
from storyscript.compiler.Preprocessor import Preprocessor
from storyscript.exceptions import StoryError
from storyscript.parser import Grammar


@fixture
def bundle(patch):
    patch.many(Bundle, ['from_path', 'bundle_trees', 'bundle', 'lex'])


def test_app_parse(bundle):
    """
    Ensures App.parse returns the parsed bundle
    """
    result = App.parse('path')
    Bundle.from_path.assert_called_with('path', ignored_path=None)
    Bundle.from_path().bundle_trees.assert_called_with(ebnf=None)
    assert result == Bundle.from_path().bundle_trees()


def test_app_parse_ignored_path(bundle):
    App.parse('path', ignored_path='ignored')
    Bundle.from_path.assert_called_with('path', ignored_path='ignored')


def test_app_parse_ebnf(bundle):
    """
    Ensures App.parse supports specifying an ebnf
    """
    App.parse('path', ebnf='ebnf')
    Bundle.from_path().bundle_trees.assert_called_with(ebnf='ebnf')


def test_app_parse_preprocess(patch, bundle, magic):
    """
    Ensures App.parse applies the preprocessor
    """
    patch.object(Preprocessor, 'process')
    story = magic()
    Bundle.from_path().bundle_trees.return_value = {'foo.story': story}
    result = App.parse('path', preprocess=True)
    assert Preprocessor.process.call_count == 1
    Bundle.from_path.assert_called_with('path', ignored_path=None)
    Bundle.from_path().bundle_trees.assert_called_with(ebnf=None)
    assert result == {'foo.story': Preprocessor.process(story)}


def test_app_compile(patch, bundle):
    patch.object(json, 'dumps')
    result = App.compile('path')
    Bundle.from_path.assert_called_with('path', ignored_path=None)
    Bundle.from_path().bundle.assert_called_with(ebnf=None)
    json.dumps.assert_called_with(Bundle.from_path().bundle(), indent=2)
    assert result == json.dumps()


def test_app_compile_concise(patch, bundle):
    patch.object(json, 'dumps')
    patch.object(AppModule, '_clean_dict')
    result = App.compile('path', concise=True)
    Bundle.from_path.assert_called_with('path', ignored_path=None)
    Bundle.from_path().bundle.assert_called_with(ebnf=None)
    AppModule._clean_dict.assert_called_with(Bundle.from_path().bundle())
    json.dumps.assert_called_with(AppModule._clean_dict(), indent=2)
    assert result == json.dumps()


def test_app_compile_ignored_path(patch, bundle):
    patch.object(json, 'dumps')
    App.compile('path', ignored_path='ignored')
    Bundle.from_path.assert_called_with('path', ignored_path='ignored')


def test_app_compile_ebnf(patch, bundle):
    """
    Ensures App.compile supports specifying an ebnf file
    """
    patch.object(json, 'dumps')
    App.compile('path', ebnf='ebnf')
    Bundle.from_path().bundle.assert_called_with(ebnf='ebnf')


def test_app_compile_first(patch, bundle):
    """
    Ensures that the App only returns the first story
    """
    Bundle.from_path().bundle.return_value = {'stories': {'my_story': 42}}
    patch.object(json, 'dumps')
    result = App.compile('path', first=True)
    Bundle.from_path.assert_called_with('path', ignored_path=None)
    Bundle.from_path().bundle.assert_called_with(ebnf=None)
    json.dumps.assert_called_with(42, indent=2)
    assert result == json.dumps()


def test_app_compile_first_error(patch, bundle):
    """
    Ensures that the App throws an error for --first with more than one story
    """
    Bundle.from_path().bundle.return_value = {'stories': {
        'my_story': 42, 'another_story': 43,
    }}
    patch.object(json, 'dumps')
    with raises(StoryError) as e:
        App.compile('path', first=True)
    assert e.value.message() == \
        'The option `--first`/-`f` can only be used if one story is complied.'
    Bundle.from_path.assert_called_with('path', ignored_path=None)
    Bundle.from_path().bundle.assert_called_with(ebnf=None)


def test_app_lex(bundle):
    result = App.lex('/path')
    Bundle.from_path.assert_called_with('/path')
    Bundle.from_path().lex.assert_called_with(ebnf=None)
    assert result == Bundle.from_path().lex()


def test_app_lex_ebnf(bundle):
    App.lex('/path', ebnf='my.ebnf')
    Bundle.from_path().lex.assert_called_with(ebnf='my.ebnf')


def test_app_grammar(patch):
    patch.init(Grammar)
    patch.object(Grammar, 'build')
    assert App.grammar() == Grammar().build()


def test_app_clean_dict():
    assert AppModule._clean_dict(0) == 0
    assert AppModule._clean_dict('a') == 'a'
    assert AppModule._clean_dict('') == ''
    assert AppModule._clean_dict(True) is True
    assert AppModule._clean_dict(False) is False
    assert AppModule._clean_dict([0]) == [0]
    assert AppModule._clean_dict([]) == []
    assert AppModule._clean_dict({}) == {}
    assert AppModule._clean_dict({'a': False}) == {}
    assert AppModule._clean_dict({'a': None}) == {}
    assert AppModule._clean_dict({'a': None, 'b': 1}) == {'b': 1}
