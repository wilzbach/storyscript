from .symbols.SymbolTypes import AnyType, NoneType, SymbolType


class Function:
    """
    An individual function.
    """
    def __init__(self, name, args, output):
        self._name = name
        self._args = args
        self._arg_names = set(args.keys())
        assert isinstance(output, SymbolType)
        self._output = output

    def check_call(self, tree, args):
        arg_names = set(args.keys())
        name_difference = self._arg_names.symmetric_difference(arg_names)
        # check arg names for differences
        for d in name_difference:
            if d in self._arg_names:
                tree.expect(0, 'function_arg_required', name=self._name, arg=d)
            else:
                tree.expect(0, 'function_arg_invalid', name=self._name, arg=d)
        # check types
        for k in args.keys():
            target = self._args[k].type()
            t = args[k].type()
            tree.expect(target.can_be_assigned(t) or t == AnyType.instance(),
                        'function_arg_type_mismatch',
                        name=self._name,
                        arg_name=k,
                        target=target,
                        source=t)

    def output(self):
        return self._output

    def __str__(self):
        return f'Function({self._name})'


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
