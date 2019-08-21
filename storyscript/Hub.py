# -*- coding: utf-8 -*-
from functools import lru_cache

from storyhub.sdk.StoryscriptHub import StoryscriptHub

from storyscript.compiler.semantics.types.Types import AnyType, BooleanType, \
    FloatType, IntType, ListType, MapType, ObjectType, StringType


@lru_cache(maxsize=1)
def _story_hub():
    """
    Cached instance of the hub sdk
    """
    return StoryscriptHub()


def story_hub():
    """
    Returns an instance of StoryscriptHub() from the hub sdk
    """
    return _story_hub()


def type_class_mapping(type_string):
    """
    Maps a given string (holding type information, from hub sdk)
    to its corresponding TypeClass in the compiler
    """
    assert type(type_string) == str
    if type_string == 'boolean':
        return BooleanType
    elif type_string == 'int':
        return IntType
    elif type_string == 'float':
        return FloatType
    elif type_string == 'string':
        return StringType
    elif type_string == 'any':
        return AnyType
    elif type_string == 'object':
        return ObjectType
    elif type_string == 'list':
        return ListType
    else:
        assert type_string == 'map'
        return MapType
