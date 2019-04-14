from storyscript.compiler.semantics.types.Types import NoneType

from .Function import Function


class FunctionTable:
    """
    A table of all available functions inside a story.
    """
    def __init__(self):
        self.functions = {}

    def insert(self, name, args, output=None):
        """
        Insert a new function into the function table.
        """
        assert name not in self.functions
        if output is None:
            output = NoneType.instance()
        fn = Function(name, args, output)
        self.functions[name] = fn

    def resolve(self, name):
        """
        Returns the function `name` or `None`.
        """
        return self.functions.get(name, None)
