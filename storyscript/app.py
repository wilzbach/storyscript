import json
import os

from .lexer import Lexer
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
    def parse(cls, storypath, debug=False, as_json=False):
        """
        Parses a story
        """
        results = {}
        parser = Parser()
        stories = cls.get_stories(storypath)
        for file in stories:
            story = cls.read_story(file)
            result = parser.parse(story, debug=debug, using_cli=True)
            results[file] = result
            if as_json:
                results[file] = json.dumps(result.json(),
                                           indent=2,
                                           separators=(',', ': '))
        return results

    @classmethod
    def lexer(cls, storypath):
        """
        Runs only the lexer
        """
        results = {}
        lexer = Lexer()
        stories = cls.get_stories(storypath)
        for story in stories:
            results[story] = lexer.input(cls.read_story(story))
        return results
