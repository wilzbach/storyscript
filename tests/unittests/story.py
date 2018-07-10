# -*- coding: utf-8 -*-
import os

from pytest import fixture, raises

from storyscript.compiler import Compiler
from storyscript.parser import Parser
from storyscript.story import Story


@fixture
def storypath():
    return 'source'


@fixture
def story_teardown(request, storypath):
    def teardown():
        os.remove(storypath)
    request.addfinalizer(teardown)


@fixture
def story_file(story_teardown, storypath):
    story = 'run\n\tpass'
    with open(storypath, 'w') as file:
        file.write(story)
    return story


@fixture
def story():
    return Story('story')


def test_story_init(story):
    assert story.story == 'story'


def test_story_read(story_file, storypath):
    """
    Ensures Story.read can read a story
    """
    result = Story.read(storypath)
    assert result == story_file


def test_story_read_not_found(patch, capsys):
    patch.object(os, 'path')
    with raises(SystemExit):
        Story.read('whatever')
    out, err = capsys.readouterr()
    assert out == 'File "whatever" not found at {}\n'.format(os.path.abspath())


def test_story_from_file(patch):
    patch.init(Story)
    patch.object(Story, 'read')
    result = Story.from_file('hello.story')
    Story.read.assert_called_with('hello.story')
    Story.__init__.assert_called_with(Story.read())
    assert isinstance(result, Story)


def test_story_from_stream(patch, magic):
    patch.init(Story)
    stream = magic()
    result = Story.from_stream(stream)
    Story.__init__.assert_called_with(stream.read())
    assert isinstance(result, Story)


def test_story_parse(patch, story):
    patch.init(Parser)
    patch.object(Parser, 'parse')
    story.parse()
    Parser.__init__.assert_called_with(ebnf_file=None)
    Parser.parse.assert_called_with(story.story, debug=False)
    assert story.tree == Parser.parse()


def test_story_parse_ebnf_file(patch, story):
    patch.init(Parser)
    patch.object(Parser, 'parse')
    story.parse(ebnf_file='ebnf')
    Parser.__init__.assert_called_with(ebnf_file='ebnf')


def test_story_debug(patch, story):
    patch.init(Parser)
    patch.object(Parser, 'parse')
    story.parse(debug='debug')
    Parser.parse.assert_called_with(story.story, debug='debug')


def test_story_compile(patch, story):
    patch.object(Compiler, 'compile')
    story.tree = 'tree'
    story.compile()
    Compiler.compile.assert_called_with(story.tree, debug=False)
    assert story.compiled == Compiler.compile()


def test_story_compile_debug(patch, story):
    patch.object(Compiler, 'compile')
    story.tree = 'tree'
    story.compile(debug='debug')
    Compiler.compile.assert_called_with(story.tree, debug='debug')
