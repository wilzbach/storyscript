# -*- coding: utf-8 -*-


class Story:

    def __init__(self, story):
        self.story = story

    @staticmethod
    @classmethod
    def from_file(cls, path):
        """
        Creates a story from a file source
        """
        return Story(cls.read(path))

    @staticmethod
    def from_stream(stream):
        """
        Creates a story from a stream source
        """
        return Story(stream.read())

