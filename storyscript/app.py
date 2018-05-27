import json
import os

from .compiler import Compiler
from .parser import Parser


class App:

    @staticmethod
    def read_story(storypath):
        """
        Reads a story
        """
        with open(storypath, 'r') as file:
            return file.read()

    @staticmethod
    def get_stories(storypath):
        """
        Gets stories from a path
        """
        stories = []
        if os.path.isdir(storypath):
            for root, subdirs, files in os.walk(storypath):
                for file in files:
                    if file.endswith('.story'):
                        stories.append(os.path.join(root, file))
            return stories
        return [storypath]

    @classmethod
    def parse(cls, stories):
        results = {}
        for story in stories:
            tree = Parser().parse(cls.read_story(story))
            results[story] = Compiler.compile(tree)
        return results

    @classmethod
    def compile(cls, path):
        stories = cls.get_stories(path)
        return json.dumps({'stories': cls.parse(stories)}, indent=2)

    @classmethod
    def lex(cls, path):
        parser = Parser()
        stories = cls.get_stories(path)
        results = {}
        for story in stories:
            results[story] = parser.lex(cls.read_story(story))
        return results
