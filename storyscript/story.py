# -*- coding: utf-8 -*-
import os

from .parser import Parser


class Story:

    def __init__(self, story):
        self.story = story

    @staticmethod
    def read(path):
        """
        Reads a story
        """
        try:
            with open(path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            abspath = os.path.abspath(path)
            print('File "{}" not found at {}'.format(path, abspath))
            exit()

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

    def parse(self):
        self.tree = Parser().parse(self.story)

