# -*- coding: utf-8 -*-
from storyscript.Api import Api
from storyscript.Bundle import Bundle
from storyscript.Story import Story


def test_api_loads(patch):
    """
    Ensures Api.loads can compile a story from a string
    """
    patch.init(Story)
    patch.object(Story, 'process')
    result = Api.loads('string')
    Story.__init__.assert_called_with('string')
    Story.process.assert_called_with(debug=True)
    assert result == Story.process()


def test_api_load(patch, magic):
    """
    Ensures Api.load can compile stories from a file stream
    """
    patch.object(Story, 'from_stream')
    stream = magic()
    result = Api.load(stream)
    Story.from_stream.assert_called_with(stream)
    Story.from_stream().process.assert_called_with(debug=True)
    story = Story.from_stream().process()
    assert result == {stream.name: story, 'services': story['services']}


def test_api_load_map(patch, magic):
    """
    Ensures Api.load_map can compile stories from a map
    """
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    files = {'a.story': "import 'b' as b", 'b.story': 'x = 0'}
    result = Api.load_map(files)
    Bundle.__init__.assert_called_with(story_files=files)
    Bundle.bundle.assert_called_with(debug=True)
    assert result == Bundle.bundle()
