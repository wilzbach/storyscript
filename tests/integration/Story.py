# -*- coding: utf-8 -*-
from io import StringIO

from storyscript.Story import Story


def test_story_from_stream():
    stream = StringIO('x = 0')
    story = Story.from_stream(stream, features=None)
    assert story.story == 'x = 0'
