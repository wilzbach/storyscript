# -*- coding: utf-8 -*-
from .story import Story


class Api:
    """
    Exposes functionalities for external use
    """
    @staticmethod
    def loads(string):
        return Story(string).process()

    @staticmethod
    def load(stream):
        story = Story.from_stream(stream).process()
        return {stream.name: story, 'services': story['services']}
