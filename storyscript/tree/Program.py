from ..version import version


class Program:

    def __init__(self, parser, story):
        parser.program = self
        self.parser = parser
        self.story = story
