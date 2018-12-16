# -*- coding: utf-8 -*-
from .Bundle import Bundle
from .Story import Story


class Api:
    """
    Exposes functionalities for external use
    """
    @staticmethod
    def loads(string):
        """
        Load story from a string.
        """
        return Story(string).process(debug=True)

    @staticmethod
    def load(stream):
        """
        Load story from a file stream.
        """
        story = Story.from_stream(stream).process(debug=True)
        return {stream.name: story, 'services': story['services']}

    @staticmethod
    def load_map(files):
        """
        Load multiple stories from a file mapping
        """
        return Bundle(files).bundle(debug=True)
