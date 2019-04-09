# -*- coding: utf-8 -*-


def singleton(fn):
    """
    Lazily instantiate a type
    """
    _instance = None

    def wrapped():
        nonlocal _instance
        if _instance is None:
            _instance = fn()
        return _instance
    return wrapped


class SymbolType:
    """
    Base class of a type.
    """

    def op(self, other, op):
        # always support upcasting to string
        if op and op.type == 'PLUS':
            if isinstance(self, StringType):
                return self
            if isinstance(other, StringType):
                return other
        if self == other:
            return self
        if isinstance(other, AnyType):
            return other
        return None

    def output(self, n):
        """
        Output types of this type.
        """
        return None


class BooleanType(SymbolType):
    """
    Represents an boolean.
    """

    def __str__(self):
        return 'boolean'

    def __eq__(self, other):
        return isinstance(other, BooleanType)

    def can_be_assigned(self, other):
        return self == other

    @singleton
    def instance():
        """
        Returns a static instance of the BooleanType.
        """
        return BooleanType()


class NoneType(SymbolType):
    """
    Represents an none-representable type
    """

    def __str__(self):
        return 'none'

    def __eq__(self, other):
        return isinstance(other, NoneType)

    def can_be_assigned(self, other):
        return False

    def op(self, other, op):
        ret = super().op(other, op)
        if self == other:
            return None
        if ret:
            return ret
        return None

    @singleton
    def instance():
        """
        Returns a static instance of the NoneType.
        """
        return NoneType()


class IntType(SymbolType):
    """
    Represents an integer.
    """

    def __str__(self):
        return 'int'

    def __eq__(self, other):
        return isinstance(other, IntType)

    def can_be_assigned(self, other):
        return self == other or isinstance(other, BooleanType)

    def op(self, other, op):
        ret = super().op(other, op)
        if ret is not None:
            return ret
        if isinstance(other, FloatType):
            return other
        return None

    def index(self, other):
        return None

    @singleton
    def instance():
        """
        Returns a static instance of the IntType.
        """
        return IntType()


class FloatType(SymbolType):
    """
    Represents a float.
    """

    def __str__(self):
        return 'float'

    def __eq__(self, other):
        return isinstance(other, FloatType)

    def can_be_assigned(self, other):
        return self == other or isinstance(other, IntType) or \
                isinstance(other, BooleanType)

    def op(self, other, op):
        ret = super().op(other, op)
        if ret is not None:
            return ret
        if isinstance(other, IntType):
            return self
        return None

    @singleton
    def instance():
        """
        Returns a static instance of the FloatType.
        """
        return FloatType()


class StringType(SymbolType):
    """
    Represents a string.
    """

    def __str__(self):
        return 'string'

    def __eq__(self, other):
        return isinstance(other, StringType)

    def can_be_assigned(self, other):
        return self == other

    @singleton
    def instance():
        """
        Returns a static instance of the StringType.
        """
        return StringType()


class ListType(SymbolType):
    """
    Represents a list.
    """
    def __init__(self, inner):
        assert isinstance(inner, SymbolType)
        self.inner = inner

    def __str__(self):
        return f'{self.inner}[]'

    def __eq__(self, other):
        return isinstance(other, ListType) and \
            self.inner == other.inner

    def can_be_assigned(self, other):
        if not isinstance(other, ListType):
            return False
        return self.inner.can_be_assigned(other.inner)

    def index(self, other):
        # only numeric indices
        if isinstance(other, IntType):
            return self.inner
        return None

    def output(self, n):
        """
        Output types of the ListType.
        """
        if n == 1:
            return self.inner,
        return IntType.instance(), self.inner


class ObjectType(SymbolType):
    """
    Represents an object
    """
    def __init__(self, key, value):
        assert isinstance(key, SymbolType)
        assert isinstance(value, SymbolType)
        self.key = key
        self.value = value

    def __str__(self):
        return f'{{{self.key}:{self.value}}}'

    def __eq__(self, other):
        return isinstance(other, ObjectType) and \
            self.key == other.key and \
            self.value == other.value

    def can_be_assigned(self, other):
        if not isinstance(other, ObjectType):
            return False
        key_res = self.key.can_be_assigned(other.key)
        val_res = self.key.can_be_assigned(other.value)
        return key_res and val_res

    def index(self, other):
        if self.key.op(other, op=None):
            return self.value
        return None

    def output(self, n):
        """
        Output types of the ObjectType.
        """
        if n == 1:
            return self.key,
        return self.key, self.value


class AnyType(SymbolType):
    """
    Represents any possible type.
    """

    def __str__(self):
        return 'any'

    def __eq__(self, other):
        return isinstance(other, AnyType)

    def can_be_assigned(self, other):
        return True

    def op(self, other, op):
        # always support upcasting to string
        if op and op.type == 'PLUS' and isinstance(other, StringType):
            return other
        # we don't anything about the type, so the operation
        # could be valid
        return self

    def index(self, other):
        return self

    @singleton
    def instance():
        """
        Returns a static instance of the AnyType.
        """
        return AnyType()

    def output(self, n):
        """
        Output types of the AnyType.
        """
        if n == 1:
            return AnyType.instance(),
        return AnyType.instance(), AnyType.instance()
