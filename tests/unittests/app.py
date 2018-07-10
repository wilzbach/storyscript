# -*- coding: utf-8 -*-
import json
import os

from pytest import fixture, raises

from storyscript.app import App
from storyscript.parser import Grammar
from storyscript.story import Story


def test_app_get_stories(patch):
    """
    Ensures App.get_stories returns the original path if it's not a directory
    """
    patch.object(os.path, 'isdir', return_value=False)
    assert App.get_stories('stories') == ['stories']


def test_app_get_stories_directory(patch):
    """
    Ensures App.get_stories returns stories in a directory
    """
    patch.object(os.path, 'isdir')
    patch.object(os, 'walk', return_value=[('root', [], ['one.story', 'two'])])
    assert App.get_stories('stories') == ['root/one.story']


def test_app_services():
    compiled_stories = {'a': {'services': ['one']}, 'b': {'services': ['two']}}
    result = App.services(compiled_stories)
    assert result == ['one', 'two']


def test_app_services_no_duplicates():
    compiled_stories = {'a': {'services': ['one']}, 'b': {'services': ['one']}}
    result = App.services(compiled_stories)
    assert result == ['one']


def test_app_compile(patch):
    patch.object(json, 'dumps')
    patch.object(Story, 'from_file')
    patch.many(App, ['get_stories', 'services'])
    App.get_stories.return_value = ['one.story']
    result = App.compile('path')
    App.get_stories.assert_called_with('path')
    Story.from_file.assert_called_with('one.story')
    Story.from_file().process.assert_called_with(ebnf_file=None, debug=False)
    App.services.assert_called_with({'one.story': Story.from_file().process()})
    dictionary = {'stories': {'one.story': Story.from_file().process()},
                  'services': App.services()}
    json.dumps.assert_called_with(dictionary, indent=2)
    assert result == json.dumps()


def test_app_compile_ebnf_file(patch):
    patch.object(json, 'dumps')
    patch.object(Story, 'from_file')
    patch.many(App, ['get_stories', 'services'])
    App.get_stories.return_value = ['one.story']
    App.compile('path', ebnf_file='ebnf')
    Story.from_file().process.assert_called_with(ebnf_file='ebnf', debug=False)


def test_app_compile_debug(patch):
    patch.object(json, 'dumps')
    patch.object(Story, 'from_file')
    patch.many(App, ['get_stories', 'services'])
    App.get_stories.return_value = ['one.story']
    App.compile('path', debug='debug')
    Story.from_file().process.assert_called_with(ebnf_file=None, debug='debug')


def test_app_lexer(patch):
    patch.object(Story, 'from_file')
    patch.object(App, 'get_stories', return_value=['one.story'])
    result = App.lex('/path')
    Story.from_file.assert_called_with('one.story')
    assert result == {'one.story': Story.from_file().lex()}


def test_app_grammar(patch):
    patch.init(Grammar)
    patch.object(Grammar, 'build')
    assert App.grammar() == Grammar().build()


def test_app_loads(patch):
    patch.init(Story)
    patch.object(Story, 'process')
    result = App.loads('string')
    Story.__init__.assert_called_with('string')
    assert result == Story.process()


def test_app_load(patch, magic):
    patch.object(Story, 'from_stream')
    stream = magic()
    result = App.load(stream)
    Story.from_stream.assert_called_with(stream)
    story = Story.from_stream().process()
    assert result == {stream.name: story, 'services': story['services']}
