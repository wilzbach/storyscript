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
