# -*- coding: utf-8 -*-
from storyscript.story import Story


def test_story_init():
    story = Story('source')
    assert story.source == 'source'
