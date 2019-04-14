from storyscript.compiler.semantics.functions.Function import MutationFunction
from storyscript.compiler.semantics.symbols.Symbols import Symbol
from storyscript.compiler.semantics.types.GenericTypes import GenericType, \
    base_type, instantiate


class Mutation:
    """
    A generic mutation for a type.
    The instantiation of a mutation is a function.
    """
    def __init__(self, ti, name, args, output):
        self._ti = ti
        self._name = name
        self._args = args
        self._output = output
        self._base_type = base_type(ti)

    def instantiate(self, type_):
        """
        Instantiate a mutation and resolve all symbols with their actual types.
        Returns an instantiated function.
        """
        # resolve all input symbols
        if not isinstance(self._ti, GenericType):
            symbols = {}
        else:
            symbols = self._ti.build_type_mapping(type_)

        # instantiate all types
        arguments = {}
        for arg_name, arg_type in self._args.items():
            arguments[arg_name] = Symbol(arg_name, instantiate(symbols,
                                                               arg_type))
        output = instantiate(symbols, self._output)
        return MutationFunction(self._name, arguments, output)

    def name(self):
        """
        The name of this mutation.
        """
        return self._name

    def base_type(self):
        """
        The base type that this mutation can mutation, e.g. IntType or ListType
        """
        return self._base_type
