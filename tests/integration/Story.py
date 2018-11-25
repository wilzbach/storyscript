# -*- coding: utf-8 -*-
from io import StringIO

from storyscript.Story import Story


def test_story_from_stream():
    stream = StringIO('x = 0')
    story = Story.from_stream(stream)
    assert story.story == 'x = 0'


def test_story_comments():
    stream = StringIO('# comment')
    story = Story.from_stream(stream)
    assert story.story == ''


def test_story_comments_indented():
    stream = StringIO('function test\n\t# comment\n\tx = 0')
    story = Story.from_stream(stream)
    assert story.story == 'function test\n\t\n\tx = 0'


def test_story_comments_multiline():
    stream = StringIO('###\nmultiline\n###')
    story = Story.from_stream(stream)
    assert story.story == ''


def test_story_comments_multiline_idented():
    stream = StringIO('function test\n\t###\nmultiline\n\t###\n\tx = 0')
    story = Story.from_stream(stream)
    assert story.story == 'function test\n\t\n\tx = 0'


def test_story_comments_multiline_catastrophic():
    """
    Certain regular expressions will work correctly on short comments, but
    fail on longer ones because of backtracking.
    """
    stream = StringIO('###\nFiller filler filler filler\n\n###\nx = 0')
    story = Story.from_stream(stream)
    assert story.story == '\nx = 0'


def test_story_comments_nested():
    stream = StringIO('###\nmultiline\n# nested\n###')
    story = Story.from_stream(stream)
    assert story.story == ''
