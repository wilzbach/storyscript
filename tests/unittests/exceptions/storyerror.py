# -*- coding: utf-8 -*-
import os

from pytest import fixture

from storyscript.exceptions import StoryError


@fixture
def error(magic):
    return magic()


@fixture
def storyerror(error):
    return StoryError(error, 'story')


def test_storyerror_init(storyerror, error):
    assert storyerror.error == error
    assert storyerror.story == 'story'
    assert storyerror.path is None
    assert issubclass(StoryError, SyntaxError)


def test_storyerror_init_path():
    storyerror = StoryError('error', 'story', path='hello.story')
    assert storyerror.path == 'hello.story'


def test_storyerror_name(storyerror):
    assert storyerror.name() == 'story'


def test_storyerror_name_path(patch, storyerror):
    """
    Ensures that paths are simplified for stories in the current working
    directory.
    """
    patch.object(os, 'getcwd', return_value='/abspath')
    storyerror.path = '/abspath/hello.story'
    assert storyerror.name() == 'hello.story'


def test_storyerror_get_line(patch, storyerror, error):
    """
    Ensures get_line returns the error line
    """
    error.line = '1'
    storyerror.story = 'x = 0\ny = 1'
    assert storyerror.get_line() == 'x = 0'


def test_storyerror_header(patch, storyerror, error):
    """
    Ensures header returns the correct text.
    """
    patch.object(StoryError, 'name')
    template = 'Error: **syntax error** in {} at line {}, column {}'
    args = (StoryError.name(), error.line, error.column)
    assert storyerror.header() == template.format(*args)


def test_storyerror_echo(capsys, patch, storyerror):
    """
    Ensures StoryError.echo prints StoryError.message
    """
    patch.object(StoryError, 'message')
    storyerror.echo()
    output, error = capsys.readouterr()
    assert output == '{}\n'.format(StoryError.message())
