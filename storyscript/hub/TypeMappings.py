# -*- coding: utf-8 -*-
from storyhub.sdk.service.output import (
    OutputAny,
    OutputBase,
    OutputBoolean,
    OutputEnum,
    OutputFloat,
    OutputInt,
    OutputList,
    OutputMap,
    OutputNone,
    OutputObject,
    OutputRegex,
    OutputString,
)

from storyscript.compiler.semantics.symbols.Symbols import StorageClass, Symbol

from storyscript.compiler.semantics.types.Types import (
    AnyType,
    BooleanType,
    FloatType,
    IntType,
    ListType,
    MapType,
    NoneType,
    ObjectType,
    RegExpType,
    StringType,
)


class TypeMappings:
    @classmethod
    def get_type_instance(cls, ty):
        """
        Maps a type class from the hub SDK to its corresponding TypeClass
        in the compiler.
        """
        assert isinstance(ty, OutputBase), ty
        if isinstance(ty, OutputBoolean):
            return BooleanType.instance()
        if isinstance(ty, OutputInt):
            return IntType.instance()
        if isinstance(ty, OutputFloat):
            return FloatType.instance()
        if isinstance(ty, OutputString):
            return StringType.instance()
        if isinstance(ty, OutputAny):
            return AnyType.instance()
        if isinstance(ty, OutputObject):
            return ObjectType(
                {
                    k: Symbol(
                        k,
                        cls.get_type_instance(v),
                        storage_class=StorageClass.read(),
                        desc=v.help(),
                    )
                    for k, v in ty.properties().items()
                }
            )
        if isinstance(ty, OutputList):
            return ListType(cls.get_type_instance(ty.elements()),)
        if isinstance(ty, OutputNone):
            return NoneType.instance()
        if isinstance(ty, OutputRegex):
            return RegExpType.instance()
        if isinstance(ty, OutputEnum):
            return StringType.instance()

        assert isinstance(ty, OutputMap), f"Unknown Hub Type: {ty!r}"
        return MapType(
            cls.get_type_instance(ty.keys()),
            cls.get_type_instance(ty.values()),
        )
