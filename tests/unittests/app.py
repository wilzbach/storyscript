# -*- coding: utf-8 -*-
import json
import os

from pytest import fixture, raises

from storyscript.app import App
from storyscript.compiler import Compiler
from storyscript.parser import Grammar, Parser
from storyscript.story import Story


@fixture
def storypath():
    return 'test.story'


@fixture
def story_teardown(request, storypath):
    def teardown():
        os.remove(storypath)
    request.addfinalizer(teardown)


@fixture
def story(story_teardown, storypath):
    story = 'run\n\tpass'
    with open(storypath, 'w') as file:
        file.write(story)
    return story


@fixture
def read_story(patch):
    patch.object(App, 'read_story')


@fixture
def parser(patch):
    patch.init(Parser)
    patch.object(Parser, 'parse')


def test_app_read_story(story, storypath):
    """
    Ensures App.read_story reads a story
    """
    result = App.read_story(storypath)
    assert result == story


def test_app_read_story_not_found(patch, capsys):
    patch.object(os, 'path')
    with raises(SystemExit):
        App.read_story('whatever')
    out, err = capsys.readouterr()
    assert out == 'File "whatever" not found at {}\n'.format(os.path.abspath())


def test_app_get_stories(mocker):
    """
    Ensures App.get_stories returns the original path if it's not a directory
    """
    mocker.patch.object(os.path, 'isdir', return_value=False)
    assert App.get_stories('stories') == ['stories']


def test_app_get_stories_directory(mocker):
    """
    Ensures App.get_stories returns stories in a directory
    """
    mocker.patch.object(os.path, 'isdir')
    mocker.patch.object(os, 'walk',
                        return_value=[('root', [], ['one.story', 'two'])])
    assert App.get_stories('stories') == ['root/one.story']


def test_app_parse(patch, parser, read_story):
    """
    Ensures App.parse runs Parser.parse
    """
    patch.object(Compiler, 'compile')
    result = App.parse(['test.story'])
    App.read_story.assert_called_with('test.story')
    Parser.__init__.assert_called_with(ebnf_file=None)
    Parser().parse.assert_called_with(App.read_story(), debug=False)
    Compiler.compile.assert_called_with(Parser().parse(), debug=False)
    assert result == {'test.story': Compiler.compile()}


def test_app_parse_ebnf_file(patch, parser, read_story):
    patch.object(Compiler, 'compile')
    App.parse(['test.story'], ebnf_file='test.ebnf')
    Parser.__init__.assert_called_with(ebnf_file='test.ebnf')


def test_app_parse_debug(patch, parser, read_story):
    patch.object(Compiler, 'compile')
    App.parse(['test.story'], debug=True)
    Parser().parse.assert_called_with(App.read_story(), debug=True)
    Compiler.compile.assert_called_with(Parser().parse(), debug=True)


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
    patch.many(App, ['get_stories', 'parse', 'services'])
    result = App.compile('path')
    App.get_stories.assert_called_with('path')
    kwargs = {'ebnf_file': None, 'debug': False}
    App.parse.assert_called_with(App.get_stories(), **kwargs)
    App.services.assert_called_with(App.parse())
    dictionary = {'stories': App.parse(), 'services': App.services()}
    json.dumps.assert_called_with(dictionary, indent=2)
    assert result == json.dumps()


def test_app_compile_ebnf_file(patch):
    patch.object(json, 'dumps')
    patch.many(App, ['get_stories', 'parse', 'services'])
    App.compile('path', ebnf_file='test.ebnf')
    kwargs = {'ebnf_file': 'test.ebnf', 'debug': False}
    App.parse.assert_called_with(App.get_stories(), **kwargs)


def test_app_compile_debug(patch):
    patch.object(json, 'dumps')
    patch.many(App, ['get_stories', 'parse', 'services'])
    App.compile('path', debug='debug')
    kwargs = {'ebnf_file': None, 'debug': 'debug'}
    App.parse.assert_called_with(App.get_stories(), **kwargs)


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
    patch.init(Parser)
    patch.object(Parser, 'parse')
    patch.object(Compiler, 'compile')
    result = App.loads('string')
    Parser.__init__.assert_called_with()
    Parser.parse.assert_called_with('string')
    Compiler.compile.assert_called_with(Parser.parse())
    assert result == Compiler.compile()


def test_app_load(patch, magic):
    patch.many(App, ['loads', 'services'])
    stream = magic()
    result = App.load(stream)
    App.loads.assert_called_with(stream.read())
    assert result == {stream.name: App.loads(), 'services': App.services()}
