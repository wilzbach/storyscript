# -*- coding: utf-8 -*-
from pytest import raises

from storyscript.Api import Api
from storyscript.Bundle import Bundle
from storyscript.Story import Story
from storyscript.exceptions import StoryError


def test_api_loads(patch):
    """
    Ensures Api.loads can compile a story from a string
    """
    patch.init(Story)
    patch.object(Story, 'process')
    result = Api.loads('string').result()
    Story.__init__.assert_called_with('string')
    Story.process.assert_called_with()
    assert result == Story.process()


def test_api_load(patch, magic):
    """
    Ensures Api.load can compile stories from a file stream
    """
    patch.object(Story, 'from_stream')
    stream = magic()
    result = Api.load(stream).result()
    Story.from_stream.assert_called_with(stream)
    Story.from_stream().process.assert_called()
    story = Story.from_stream().process()
    assert result == {stream.name: story, 'services': story['services']}


def test_api_load_map(patch, magic):
    """
    Ensures Api.load_map can compile stories from a map
    """
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    files = {'a.story': "import 'b' as b", 'b.story': 'x = 0'}
    result = Api.load_map(files).result()
    Bundle.__init__.assert_called_with(story_files=files)
    Bundle.bundle.assert_called()
    assert result == Bundle.bundle()


def test_api_loads_internal_error(patch):
    """
    Ensures Api.loads handles unknown errors
    """
    patch.init(Story)
    patch.object(Story, 'process')
    patch.object(StoryError, 'internal_error')
    StoryError.internal_error.return_value = Exception('ICE')
    Story.process.side_effect = Exception('An unknown error.')
    s = Api.loads('string')
    e = s.errors()[0]

    assert str(e) == 'ICE'


def test_api_loads_internal_error_debug(patch):
    """
    Ensures Api.loads handles unknown errors with debug=True
    """
    patch.init(Story)
    patch.object(Story, 'process')
    patch.object(StoryError, 'internal_error')
    StoryError.internal_error.return_value = Exception('ICE')
    Story.process.side_effect = Exception('An unknown error.')
    with raises(Exception) as e:
        Api.loads('string', debug=True).check_success()

    assert str(e.value) == 'An unknown error.'


def test_api_load_internal_error(patch, magic):
    """
    Ensures Api.loads handles unknown errors
    """
    patch.init(Story)
    patch.object(Story, 'from_stream')
    patch.object(StoryError, 'internal_error')
    StoryError.internal_error.return_value = Exception('ICE')
    Story.from_stream.side_effect = Exception('An unknown error.')
    stream = magic()
    s = Api.load(stream)
    e = s.errors()[0]

    assert str(e) == 'ICE'


def test_api_load_story_error(patch, magic):
    """
    Ensures Api.loads handles unknown errors
    """
    patch.init(Story)
    patch.object(Story, 'from_stream')
    Story.from_stream.side_effect = StoryError.internal_error('.error.')
    stream = magic()
    s = Api.load(stream)
    e = s.errors()[0]

    assert e.message().startswith('Internal error occured: .error.')


def test_api_load_internal_error_debug(patch, magic):
    """
    Ensures Api.load handles unknown errors with debug=True
    """
    patch.init(Story)
    patch.object(Story, 'from_stream')
    patch.object(StoryError, 'internal_error')
    StoryError.internal_error.return_value = Exception('ICE')
    Story.from_stream.side_effect = Exception('An unknown error.')
    stream = magic()
    with raises(Exception) as e:
        Api.load(stream, debug=True).check_success()

    assert str(e.value) == 'An unknown error.'


def test_api_load_map_internal_error(patch):
    """
    Ensures Api.loads handles unknown errors
    """
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    patch.object(StoryError, 'internal_error')
    StoryError.internal_error.return_value = Exception('ICE')
    Bundle.bundle.side_effect = Exception('An unknown error.')
    s = Api.load_map({})
    e = s.errors()[0]

    assert str(e) == 'ICE'


def test_api_load_map_internal_error_debug(patch):
    """
    Ensures Api.loads handles unknown errors with debug=True
    """
    patch.init(Bundle)
    patch.object(Bundle, 'bundle')
    patch.object(StoryError, 'internal_error')
    StoryError.internal_error.return_value = Exception('ICE')
    Bundle.bundle.side_effect = Exception('An unknown error.')
    with raises(Exception) as e:
        Api.load_map({}, debug=True).check_success()

    assert str(e.value) == 'An unknown error.'
