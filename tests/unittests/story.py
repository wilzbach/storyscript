# -*- coding: utf-8 -*-
from pytest import fixture

from storyscript.story import Story


@fixture
def story():
    return Story('source', 'type')


def test_story_init(story):
    assert story.source == 'source'
    assert story.source_type == 'type'
