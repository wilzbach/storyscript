# -*- coding: utf-8 -*-
import io
import os

from lark.exceptions import UnexpectedInput, UnexpectedToken
from lark.lexer import Token

from pytest import fixture, mark, raises

import storyscript.Story as StoryModule
from storyscript.Story import Story, StoryContext
from storyscript.compiler import Compiler
from storyscript.compiler.lowering.Lowering import Lowering
from storyscript.compiler.pretty.PrettyPrinter import PrettyPrinter
from storyscript.exceptions import CompilerError, StoryError, StorySyntaxError
from storyscript.parser import Parser
from storyscript.parser.Tree import Tree


@fixture
def story():
    return Story("story", features=None)


@fixture
def storycontext():
    return StoryContext(features=None, hub=None)


@fixture
def parser(patch):
    patch.init(Parser)
    patch.many(Parser, ["parse", "lex"])
    return Parser()


@fixture
def compiler(patch, story):
    patch.object(Compiler, "compile")
    story.tree = "tree"


def test_story_init(story):
    assert story.story == "story"
    assert story.path is None


def test_story_init_path():
    story = Story("story", features=None, path="path")
    assert story.path == "path"


def test_story_name(story):
    assert story.extract_name() == "story"
    assert story.name == "story"


def test_story_name_path(patch, story):
    patch.object(os, "getcwd", return_value="/abspath")
    story.path = "hello.story"
    assert story.extract_name() == "hello.story"


def test_story_name_reduce_path(patch, story):
    """
    Ensures that paths are simplified for stories in the current working
    directory.
    """
    patch.object(os, "getcwd", return_value="/abspath")
    story.path = "/abspath/hello.story"
    assert story.extract_name() == "hello.story"


def test_story_read(patch):
    """
    Ensures Story.read can read a story
    """
    patch.object(StoryModule, "bom_open")
    Story.read("hello.story")
    StoryModule.bom_open.assert_called_with("hello.story", "r")


def test_story_read_not_found(patch, capsys):
    patch.object(io, "open", side_effect=FileNotFoundError)
    patch.object(os, "path")
    with raises(StoryError) as e:
        Story.read("whatever")
    assert "E0047: File `whatever` not found at " in e.value.short_message()


def test_story_from_file(patch):
    patch.init(Story)
    patch.object(Story, "read")
    result = Story.from_file("hello.story", features=None)
    Story.read.assert_called_with("hello.story")
    Story.__init__.assert_called_with(Story.read(), None, path="hello.story")
    assert isinstance(result, Story)


def test_story_from_stream(patch, magic):
    patch.init(Story)
    stream = magic()
    result = Story.from_stream(stream, features=None)
    Story.__init__.assert_called_with(stream.read(), None)
    assert isinstance(result, Story)


def test_story_error(patch, story):
    """
    Ensures Story.error creates a StoryError error
    """
    assert isinstance(story.error(StorySyntaxError("error")), StoryError)


def test_story_parse(patch, story, parser):
    story.parse(parser=parser)
    parser.parse.assert_called_with(story.story, allow_single_quotes=False)
    assert story.tree == Parser.parse()


def test_story_parse_debug(patch, story, parser):
    story.parse(parser=parser)
    parser.parse.assert_called_with(story.story, allow_single_quotes=False)


def test_story_parse_debug_single_quotes(patch, story, parser):
    story.parse(parser=parser, allow_single_quotes=True)
    parser.parse.assert_called_with(story.story, allow_single_quotes=True)


def test_story_parse_lower(patch, story, parser):
    patch.object(Lowering, "process")
    story.parse(parser=parser, lower=True)
    parser.parse.assert_called_with(story.story, allow_single_quotes=False)
    Lowering.process.assert_called_with(Parser.parse())
    assert story.tree == Lowering.process(Lowering.process())


@mark.parametrize(
    "error",
    [
        UnexpectedToken("token", "expected"),
        UnexpectedInput("token", "expected"),
        StorySyntaxError("test"),
    ],
)
def test_story_parse_error(patch, story, parser, error):
    """
    Ensures Story.parse uses Story.error for UnexpectedToken errors.
    """
    parser.parse.side_effect = error
    patch.object(Story, "error")
    with raises(Exception):
        story.parse(parser=parser)
    Story.error.assert_called_with(error)


def test_story_compile(patch, story, compiler):
    story.compile()
    Compiler.compile.assert_called_with(
        story.tree, story=story, scope=None, backend="json"
    )
    assert story.compiled == Compiler.compile()


@mark.parametrize("error", [StorySyntaxError("error"), CompilerError("error")])
def test_story_compiler_error(patch, story, compiler, error):
    """
    Ensures Story.compiler uses Story.error in case of StorySyntaxError.
    """
    Compiler.compile.side_effect = error
    patch.object(Story, "error", return_value=Exception("error"))
    with raises(Exception):
        story.compile()
    Story.error.assert_called_with(error)


def test_story_format(patch, story):
    patch.object(PrettyPrinter, "compile")
    story.tree = "tree"
    r = story.format()
    PrettyPrinter.compile.assert_called_with(story.tree)
    assert r == PrettyPrinter.compile()


@mark.parametrize("error", [StorySyntaxError("error"), CompilerError("error")])
def test_format_story_compiler_error(patch, story, compiler, error):
    """
    Ensures Story.format uses Story.error in case of StorySyntaxError.
    """
    patch.object(PrettyPrinter, "compile")
    PrettyPrinter.compile.side_effect = error
    patch.object(Story, "error", return_value=Exception("error"))
    with raises(Exception):
        story.format()
    Story.error.assert_called_with(error)


def test_story_lex(patch, story, parser):
    result = story.lex(parser=parser)
    parser.lex.assert_called_with(story.story)
    assert result == Parser.lex()


def test_story_lex_parser(patch, story, parser):
    story.lex(parser=parser)
    parser.lex.assert_called_with(story.story)


def test_story_lex_parser_cached(patch, story, magic):
    my_parser = magic()
    patch.object(Story, "_parser", return_value=my_parser)
    story.lex(parser=None)
    my_parser.lex.assert_called_with(story.story)


def test_story_process(patch, story):
    patch.many(Story, ["parse", "compile"])
    story.compiled = "compiled"
    result = story.process()
    assert story.parse.call_args_list[0][0] == ()
    kw_args = story.parse.call_args_list[0][1]
    assert len(kw_args) == 1
    assert isinstance(kw_args["parser"], Parser)
    story.parse.assert_called()
    story.compile.assert_called_with()
    assert result == story.compiled


def test_story_process_parser(patch, story, parser):
    patch.many(Story, ["parse", "compile"])
    story.compiled = "compiled"
    result = story.process(parser=parser)
    story.parse.assert_called_with(parser=parser)
    story.compile.assert_called_with()
    assert result == story.compiled


def test_storycontext_deprecate(patch, storycontext):
    patch.object(StoryModule, "deprecate", side_effect=["d1", "d2"])
    tree = Tree("foo", [])
    storycontext.deprecate(tree, "deprecation_1")
    StoryModule.deprecate.assert_called_with(tree=tree, name="deprecation_1")

    token = Token("NAME", "bar")
    storycontext.deprecate(token, "deprecation_2")
    StoryModule.deprecate.assert_called_with(token=token, name="deprecation_2")

    assert storycontext.deprecations() == ["d1", "d2"]
