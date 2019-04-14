from storyscript.compiler.semantics.types.Types import BaseType, ListType, \
    MapType


class TypeSymbol:
    """
    An to-be-resolved symbol of a generic type.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'TypeSymbol({self.name})'

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, o):
        return isinstance(o, TypeSymbol) and self.name == o.name

    def instantiate(self, symbols):
        """
        Given a symbol mapping dict, a symbol can instantiate itself.
        :param symbols:  symbol mapping dictionary
        :return: Instantiated symbol
        """
        return symbols[self]


class GenericType:
    """
    A type that can be instantiated.
    """

    def instantiate(self, symbols):
        """
        Instantiates the generic type with a set of symbols.
        """
        ts = []
        for s in self.symbols:
            if isinstance(s, BaseType):
                # no instantiation required
                ts.append(s)
            elif isinstance(s, GenericType):
                t = s.instantiate(symbols)
                ts.append(t)
            else:
                ts.append(symbols[s])
        return self.base_type()(*ts)

    def base_type(self):
        """
        Returns the base type of the generic type. For example, a
        ListGenericType has ListType has its base types.
        :return: base type
        """
        return self._base_type

    def build_type_mapping(self, l):
        """
        Find the instantiation types and returns a mapping for the generic
        symbol types with their actual base type.
        :param l: base type instance to use
        :return: dict of symbol names (keys) with their matching type (value)
        """
        raise NotImplementedError()


class ListGenericType(GenericType):
    """
    A generic list type.
    """
    def __init__(self, symbols):
        self.symbols = symbols
        self._base_type = ListType

    def build_type_mapping(self, l):
        assert len(self.symbols) == 1
        assert isinstance(l, ListType)
        return {self.symbols[0]: l.inner}


class MapGenericType(GenericType):
    """
    A generic object type.
    """
    def __init__(self, symbols):
        self.symbols = symbols
        self._base_type = MapType

    def build_type_mapping(self, l):
        assert len(self.symbols) == 2
        assert isinstance(l, MapType)
        return {
            self.symbols[0]: l.key,
            self.symbols[1]: l.value,
        }


def instantiate(symbols, t):
    """
    Instantiates a type
    :param symbols: symbols to use for the instantiation
    :param t: type to instantiate
    :return: instantiated type
    """
    if isinstance(t, TypeSymbol):
        return t.instantiate(symbols)
    if isinstance(t, GenericType):
        return t.instantiate(symbols)
    assert isinstance(t, BaseType)
    return t


def base_type(t):
    """
    Returns the base type of a generic type container. For example, a
    ListGenericType has ListType has its base types.
    For BaseTypes, their type is directly returned.

    :param t: type for which the base_type should be calculated
    :return: base type of the container
    """
    if isinstance(t, GenericType):
        return t.base_type()
    assert isinstance(t, BaseType)
    return type(t)
