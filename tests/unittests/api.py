# -*- coding: utf-8 -*-
from storyscript.api import Api
from storyscript.story import Story


def test_api_loads(patch):
    patch.init(Story)
    patch.object(Story, 'process')
    result = Api.loads('string')
    Story.__init__.assert_called_with('string')
    assert result == Story.process()


def test_api_load(patch, magic):
    patch.object(Story, 'from_stream')
    stream = magic()
    result = Api.load(stream)
    Story.from_stream.assert_called_with(stream)
    story = Story.from_stream().process()
    assert result == {stream.name: story, 'services': story['services']}
