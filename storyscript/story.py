# -*- coding: utf-8 -*-


class Story:

    def __init__(self, source, source_type):
        self.source = source
        self.source_type = source_type

    @staticmethod
    def from_file(path):
        """
        Creates a story from a file source
        """
        return Story(path, 'file')

    @staticmethod
    def from_stream(stream):
        """
        Creates a story from a stream source
        """
        return Story(stream, 'stream')

    @staticmethod
    def from_string(string):
        """
        Creates a story from a string source
        """
        return Story(string, 'string')
