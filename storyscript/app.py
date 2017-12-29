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
            for file in os.listdir(storypath):
                if file.endswith('.story'):
                    stories.append(file)
            return stories

        return [storypath]

    @classmethod
    def parse(cls, storypath, debug=False, as_json=False):
        """
        Parses a story
        """
        story = cls.read_story(storypath)
        parser = Parser()
        result = parser.parse(story, debug=debug, using_cli=True)
        if as_json:
            return json.dumps(result.json(), indent=2, separators=(',', ': '))
        return result

    @classmethod
    def lexer(cls, storypath):
        """
        Runs only the lexer
        """
        story = cls.read_story(storypath)
        lexer = Lexer()
        return lexer.input(story)
