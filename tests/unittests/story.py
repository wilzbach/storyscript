# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.story import Story


@fixture
def story():
    return Story('source', 'type')


def test_story_init(story):
    assert story.source == 'source'
    assert story.source_type == 'type'


def test_story_from_file(patch):
    patch.init(Story)
    result = Story.from_file('hello.story')
    Story.__init__.assert_called_with('hello.story', 'file')
    assert isinstance(result, Story)
