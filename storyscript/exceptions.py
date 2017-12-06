class ScriptError(SyntaxError):
    def __init__(self, errors):
        self.errors = errors
 
    def __str__(self):
        return "storyscript Syntax Errors found while compiling"
 
    def json(self):
        return self.errors
