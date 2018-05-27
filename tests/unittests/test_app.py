import json
import os

from pytest import fixture

from storyscript.app import App
from storyscript.compiler import Compiler
from storyscript.parser import Parser


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
    Parser().parse.assert_called_with(App.read_story())
    Compiler.compile.assert_called_with(Parser().parse())
    assert result == {'test.story': Compiler.compile()}


def test_app_compile(patch):
    patch.object(Compiler, 'compile')
    patch.object(App, 'parse', return_value={'hello.story': 'tree'})
    result = App.compile('path')
    App.parse.assert_called_with('path')
    Compiler.compile.assert_called_with('tree')
    assert result == {'hello.story': Compiler.compile()}


def test_app_lexer(patch, read_story):
    patch.init(Parser)
    patch.object(Parser, 'lex')
    patch.object(App, 'get_stories', return_value=['one.story'])
    result = App.lex('/path')
    App.read_story.assert_called_with('one.story')
    Parser.lex.assert_called_with(App.read_story())
    assert result == {'one.story': Parser.lex()}
