class ScriptError(SyntaxError):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return 'StoryScript Syntax Errors found.'

    def json(self):
        return self.errors
