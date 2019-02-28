# -*- coding: utf-8 -*-
import io
import os

from lark.exceptions import UnexpectedInput, UnexpectedToken

from pytest import fixture, mark, raises

from storyscript.Story import Story
from storyscript.compiler import Compiler
from storyscript.exceptions import CompilerError, StoryError, StorySyntaxError
from storyscript.parser import Parser


@fixture
def story():
    return Story('story')


@fixture
def parser(patch):
    patch.init(Parser)
    patch.many(Parser, ['parse', 'lex'])


@fixture
def compiler(patch, story):
    patch.object(Compiler, 'compile')
    story.tree = 'tree'


def test_story_init(story):
    assert story.story == 'story'
    assert story.path is None


def test_story_init_path():
    story = Story('story', path='path')
    assert story.path == 'path'


def test_story_read(patch):
    """
    Ensures Story.read can read a story
    """
    patch.object(io, 'open')
    result = Story.read('hello.story')
    io.open.assert_called_with('hello.story', 'r')
    assert result == io.open().__enter__().read()


def test_story_read_not_found(patch, capsys):
    patch.object(io, 'open', side_effect=FileNotFoundError)
    patch.object(os, 'path')
    with raises(StoryError) as e:
        Story.read('whatever')
    assert 'E0047: File `whatever` not found at ' in e.value.short_message()


def test_story_from_file(patch):
    patch.init(Story)
    patch.object(Story, 'read')
    result = Story.from_file('hello.story')
    Story.read.assert_called_with('hello.story')
    Story.__init__.assert_called_with(Story.read(), path='hello.story')
    assert isinstance(result, Story)


def test_story_from_stream(patch, magic):
    patch.init(Story)
    stream = magic()
    result = Story.from_stream(stream)
    Story.__init__.assert_called_with(stream.read())
    assert isinstance(result, Story)


def test_story_error(patch, story):
    """
    Ensures Story.error creates a StoryError error
    """
    assert isinstance(story.error(StorySyntaxError('error')), StoryError)


def test_story_parse(patch, story, parser):
    story.parse()
    Parser.__init__.assert_called_with(ebnf=None)
    Parser.parse.assert_called_with(story.story)
    assert story.tree == Parser.parse()


def test_story_parse_ebnf(patch, story, parser):
    story.parse(ebnf='ebnf')
    Parser.__init__.assert_called_with(ebnf='ebnf')


def test_story_parse_debug(patch, story, parser):
    story.parse()
    Parser.parse.assert_called_with(story.story)


@mark.parametrize('error', [
    UnexpectedToken('token', 'expected'),
    UnexpectedInput('token', 'expected'),
    StorySyntaxError('test'),
])
def test_story_parse_error(patch, story, parser, error):
    """
    Ensures Story.parse uses Story.error for UnexpectedToken errors.
    """
    Parser.parse.side_effect = error
    patch.object(Story, 'error')
    with raises(Exception):
        story.parse()
    Story.error.assert_called_with(error)


def test_story_modules(magic, story):
    import_tree = magic()
    story.tree = magic()
    story.tree.find_data.return_value = [import_tree]
    result = story.modules()
    assert result == [import_tree.string.child().value[1:-1]]


def test_story_modules_no_extension(magic, story):
    import_tree = magic()
    import_tree.string.child.return_value = magic(value='"hello"')
    story.tree = magic()
    story.tree.find_data.return_value = [import_tree]
    result = story.modules()
    assert result == ['hello.story']


def test_story_compile(patch, story, compiler):
    story.compile()
    Compiler.compile.assert_called_with(story.tree)
    assert story.compiled == Compiler.compile()


@mark.parametrize('error', [StorySyntaxError('error'), CompilerError('error')])
def test_story_compiler_error(patch, story, compiler, error):
    """
    Ensures Story.compiler uses Story.error in case of StorySyntaxError.
    """
    Compiler.compile.side_effect = error
    patch.object(Story, 'error', return_value=Exception('error'))
    with raises(Exception):
        story.compile()
    Story.error.assert_called_with(error)


def test_story_lex(patch, story, parser):
    result = story.lex()
    Parser.__init__.assert_called_with(ebnf=None)
    Parser.lex.assert_called_with(story.story)
    assert result == Parser.lex()


def test_story_lex_ebnf(patch, story, parser):
    story.lex(ebnf='ebnf')
    Parser.__init__.assert_called_with(ebnf='ebnf')


def test_story_process(patch, story):
    patch.many(Story, ['parse', 'compile'])
    story.compiled = 'compiled'
    result = story.process()
    Story.parse.assert_called_with(ebnf=None)
    Story.compile.assert_called_with()
    assert result == story.compiled


def test_story_process_ebnf(patch, story):
    patch.many(Story, ['parse', 'compile'])
    story.compiled = 'compiled'
    story.process(ebnf='ebnf')
    Story.parse.assert_called_with(ebnf='ebnf')
