# -*- coding: utf-8 -*-
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


def test_storyerror_echo(capsys, patch, storyerror):
    """
    Ensures StoryError.echo prints StoryError.message
    """
    patch.object(StoryError, 'message')
    storyerror.echo()
    output, error = capsys.readouterr()
    assert output == '{}\n'.format(StoryError.message())
