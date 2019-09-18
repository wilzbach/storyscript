# -*- coding: utf-8 -*-
from storyscript.compiler.semantics.types.Types import AnyType, BooleanType, \
    FloatType, IntType, ListType, MapType, ObjectType, StringType


class TypeMappings:
    @staticmethod
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

    @staticmethod
    def get_type_instance(var, obj=None):
        """
        Returns the correctly mapped type class instance of the given type
        Params:
            var: A Symbol from which type could be retrieved.
            object: In case the Symbol is of type Object, the object that
                should be wrapped inside the ObjectType instance.
        """
        type_class = TypeMappings.type_class_mapping(var.type())
        if type_class == ObjectType:
            output_type = ObjectType(object=obj)
        elif type_class == ListType:
            output_type = ListType(AnyType.instance())
        elif type_class == MapType:
            output_type = MapType(AnyType.instance(), AnyType.instance())
        else:
            assert type_class in (
                AnyType, BooleanType, FloatType, IntType, StringType)
            output_type = type_class.instance()
        return output_type
