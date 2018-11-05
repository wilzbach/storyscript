# -*- coding: utf-8 -*-
import io
import os
import re

from lark.exceptions import UnexpectedInput, UnexpectedToken

from pytest import fixture, raises

from storyscript.compiler import Compiler
from storyscript.exceptions import StoryError, StorySyntaxError
from storyscript.parser import Parser
from storyscript.story import Story


@fixture
def story():
    return Story('story')


@fixture
def parser(patch):
    patch.init(Parser)
    patch.many(Parser, ['parse', 'lex'])


def test_story_init(story):
    assert story.story == 'story'
    assert story.path is None


def test_story_init_path():
    story = Story('story', path='path')
    assert story.path == 'path'


def test_story_clean_source(patch):
    """
    Ensures that a story is cleaned correctly
    """
    patch.object(re, 'sub')
    result = Story.clean_source('source')
    expression = r'(?<=###)\s(.*|\\n)+(?=\s###)|#(.*)'
    re.sub.assert_called_with(expression, '', 'source')
    assert result == re.sub()


def test_story_read(patch):
    """
    Ensures Story.read can read a story
    """
    patch.object(io, 'open')
    patch.object(Story, 'clean_source')
    result = Story.read('hello.story')
    io.open.assert_called_with('hello.story', 'r')
    Story.clean_source.assert_called_with(io.open().__enter__().read())
    assert result == Story.clean_source()


def test_story_read_not_found(patch, capsys):
    patch.object(io, 'open', side_effect=FileNotFoundError)
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
    Ensures Story.error handles errors correctly.
    """
    patch.init(StoryError)
    patch.object(StoryError, 'echo')
    with raises(SystemExit):
        story.error('error')
    StoryError.__init__.assert_called_with('error', story.path, story.story)
    assert StoryError.echo.call_count == 1


def test_story_error_debug(patch, story):
    """
    Ensures Story.error raises the error in debug mode
    """
    with raises(StorySyntaxError):
        story.error(StorySyntaxError('error'), debug=True)


def test_story_parse(patch, story, parser):
    story.parse()
    Parser.__init__.assert_called_with(ebnf=None)
    Parser.parse.assert_called_with(story.story, debug=False)
    assert story.tree == Parser.parse()


def test_story_parse_ebnf(patch, story, parser):
    story.parse(ebnf='ebnf')
    Parser.__init__.assert_called_with(ebnf='ebnf')


def test_story_parse_debug(patch, story, parser):
    story.parse(debug='debug')
    Parser.parse.assert_called_with(story.story, debug='debug')


def test_story_parse_unexpected_token(patch, story, parser):
    """
    Ensures Story.parse uses Story.error for UnexpectedToken errors.
    """
    error = UnexpectedToken('token', 'expected')
    Parser.parse.side_effect = error
    patch.object(Story, 'error')
    story.parse()
    Story.error.assert_called_with(error, debug=False)


def test_story_parse_unexpected_input(patch, story, parser):
    """
    Ensures Story.parse uses Story.error for UnexpectedInput errors.
    """
    error = UnexpectedInput('token', 'expected')
    Parser.parse.side_effect = error
    patch.object(Story, 'error')
    story.parse()
    Story.error.assert_called_with(error, debug=False)


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


def test_story_compile(patch, story):
    patch.object(Compiler, 'compile')
    story.tree = 'tree'
    story.compile()
    Compiler.compile.assert_called_with(story.tree, debug=False)
    assert story.compiled == Compiler.compile()


def test_story_compile_debug(patch, story):
    patch.object(Compiler, 'compile')
    story.tree = 'tree'
    story.compile(debug=True)
    Compiler.compile.assert_called_with(story.tree, debug=True)


def test_story_compiler_syntax_error(patch, story):
    """
    Ensures Story.compiler uses Story.error in case of StorySyntaxError.
    """
    error = StorySyntaxError('error')
    patch.object(Compiler, 'compile', side_effect=error)
    patch.object(Story, 'error')
    story.tree = 'tree'
    story.compile()
    Story.error.assert_called_with(error, debug=False)


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
    Story.parse.assert_called_with(ebnf=None, debug=False)
    Story.compile.assert_called_with(debug=False)
    assert result == story.compiled


def test_story_process_debug(patch, story):
    patch.many(Story, ['parse', 'compile'])
    story.compiled = 'compiled'
    story.process(debug='debug')
    Story.parse.assert_called_with(ebnf=None, debug='debug')
    Story.compile.assert_called_with(debug='debug')


def test_story_process_ebnf(patch, story):
    patch.many(Story, ['parse', 'compile'])
    story.compiled = 'compiled'
    story.process(ebnf='ebnf')
    Story.parse.assert_called_with(ebnf='ebnf', debug=False)
