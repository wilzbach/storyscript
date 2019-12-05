from storyscript.compiler.semantics.functions.Function import MutationFunction
from storyscript.compiler.semantics.symbols.Symbols import Symbol
from storyscript.compiler.semantics.types.GenericTypes import GenericType, \
    base_type, instantiate


class Mutation:
    """
    A generic mutation for a type.
    The instantiation of a mutation is a function.
    """
    def __init__(self, ti, name, args, output, desc):
        self._ti = ti
        self._name = name
        self._args = args
        self._output = output
        self._base_type = base_type(ti)
        self._arg_names = self.compute_arg_names_hash(args.keys())
        self._cmp_name = name + ','.join(sorted(args.keys()))
        self._desc = desc

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
        for arg_name, arg_payload in self._args.items():
            arguments[arg_name] = Symbol(arg_name,
                                         instantiate(symbols,
                                                     arg_payload['type']),
                                         desc=arg_payload['desc'])
        output = instantiate(symbols, self._output)
        return MutationFunction(self._name, arguments, output, desc=self._desc)

    def name(self):
        """
        The name of this mutation.
        """
        return self._name

    def desc(self):
        """
        A help text description of this mutation.
        """
        return self._desc

    def type(self):
        """
        The type that this mutation can mutation, e.g. List[A] or string
        """
        return self._ti

    def base_type(self):
        """
        The base type that this mutation can mutation, e.g. IntType or ListType
        """
        return self._base_type

    def cmp_name(self):
        """
        Returns a combination of the name and argument names that can be used
        for sorting this mutation.
        """
        return self._cmp_name

    def arg_names_hash(self):
        """
        Returns the hashed argument names of this mutation
        """
        return self._arg_names

    @staticmethod
    def compute_arg_names_hash(keys):
        """
        Converts a list of argument names to a hashable key.
        """
        return hash(tuple(sorted(keys)))
