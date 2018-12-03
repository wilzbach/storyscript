# -*- coding: utf-8 -*-
from .Story import Story
from .parser import Grammar


class Api:
    """
    Exposes functionalities for external use
    """
    @staticmethod
    def loads(string):
        return Story(string).process(debug=True)

    @staticmethod
    def load(stream):
        story = Story.from_stream(stream).process(debug=True)
        return {stream.name: story, 'services': story['services']}

    @staticmethod
    def grammar():
        """
        Returns the current grammar
        """
        return Grammar().build()
