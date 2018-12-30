# -*- coding: utf-8 -*-
from .Bundle import Bundle
from .Story import Story
from .exceptions import StoryError


class Api:
    """
    Exposes functionalities for external use
    """
    @staticmethod
    def loads(string, debug=False):
        """
        Load story from a string.
        """
        try:
            return Story(string).process()
        except StoryError as e:
            raise e
        except Exception as e:
            if debug:
                raise e
            else:
                raise StoryError.internal_error(e)

    @staticmethod
    def load(stream, debug=False):
        """
        Load story from a file stream.
        """
        try:
            story = Story.from_stream(stream).process()
            return {stream.name: story, 'services': story['services']}
        except StoryError as e:
            raise e
        except Exception as e:
            if debug:
                raise e
            else:
                raise StoryError.internal_error(e)

    @staticmethod
    def load_map(files, debug=False):
        """
        Load multiple stories from a file mapping
        """
        try:
            return Bundle(story_files=files).bundle()
        except StoryError as e:
            raise e
        except Exception as e:
            if debug:
                raise e
            else:
                raise StoryError.internal_error(e)
