import json
import os

from storyscript.app import App
from storyscript.lexer import Lexer
from storyscript.parser import Parser

from pytest import fixture


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
def read_story(mocker):
    mocker.patch.object(App, 'read_story')


@fixture
def parser(mocker):
    mocker.patch.object(Parser, '__init__', return_value=None)
    mocker.patch.object(Parser, 'parse')


def test_app_read_story(story, storypath):
    """
    Ensures App.read_story reads a story
    """
    result = App.read_story(storypath)
    assert result == story


def test_app_parse(parser, read_story):
    """
    Ensures App.parse runs the parser
    """
    result = App.parse('/path/to/story')
    kwargs = {'debug': False, 'using_cli': True}
    Parser().parse.assert_called_with(App.read_story(), **kwargs)
    assert result == Parser().parse()


def test_app_parse_json(mocker, parser, read_story):
    """
    Ensures App.parse runs the parser
    """
    mocker.patch.object(json, 'dumps')
    result = App.parse('/path/to/story', as_json=True)
    kwargs = {'indent': 2, 'separators': (',', ': ')}
    json.dumps.assert_called_with(Parser.parse().json(), **kwargs)
    assert result == json.dumps()


def test_app_lexer(mocker, read_story):
    """
    Ensures App.lexer runs the lexer
    """
    mocker.patch.object(Lexer, '__init__', return_value=None)
    mocker.patch.object(Lexer, 'input')
    result = App.lexer('path')
    Lexer.input.assert_called_with(App.read_story())
    assert result == Lexer().input()
