# -*- coding: utf-8 -*-
from storyscript.Api import Api
from storyscript.Bundle import Bundle
from storyscript.Story import Story


def test_api_loads(patch):
    patch.init(Story)
    patch.object(Story, 'process')
    result = Api.loads('string')
    Story.__init__.assert_called_with('string')
    Story.process.assert_called_with(debug=True)
    assert result == Story.process()


def test_api_load(patch, magic):
    patch.object(Story, 'from_stream')
    stream = magic()
    result = Api.load(stream)
    Story.from_stream.assert_called_with(stream)
    Story.from_stream().process.assert_called_with(debug=True)
    story = Story.from_stream().process()
    assert result == {stream.name: story, 'services': story['services']}


def test_api_load_map(patch, magic):
    patch.object(Bundle, 'load_story')
    result = Api.load_map({'a.story': "import 'b' as b", 'b.story': 'string'})
    Bundle.load_story().parse.assert_called_with(debug=True, ebnf=None)
    Bundle.load_story().compile.assert_called_with(debug=True)
    assert result == {
        'services': [],
        'entrypoint': ['a.story', 'b.story'],
        'stories': {
            'a.story': Bundle.load_story().compiled,
            'b.story': Bundle.load_story().compiled,
        }
    }
