# -*- coding: utf-8 -*-
class StoryError(SyntaxError):

    """
    Handles story-related errors (reading, parsing, compiling), transforming
    raw errors in nice and helpful messages.
    """

    def __init__(self, error, story, path=None):
        self.error = error
        self.story = story
        self.path = path

    def message(self):
        pass

    def echo(self):
        """
        Prints the message
        """
        print(self.message())
