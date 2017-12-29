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

    @classmethod
    def parse(cls, storypath, debug=False):
        """
        Parses a story
        """
        story = cls.read_story(storypath)
        parser = Parser()
        return parser.parse(story, debug=debug, using_cli=True)

    @classmethod
    def lexer(cls, storypath):
        """
        Runs only the lexer
        """
        story = cls.read_story(storypath)
        lexer = Lexer()
        return lexer.input(story)
