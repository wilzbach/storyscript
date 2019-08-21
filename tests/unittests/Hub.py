# -*- coding: utf-8 -*-
from storyscript.Hub import type_class_mapping
from storyscript.compiler.semantics.types.Types import AnyType, BooleanType, \
    FloatType, IntType, ListType, MapType, ObjectType, StringType


def test_type_class_mapping():
    assert type_class_mapping('float') == FloatType
    assert type_class_mapping('boolean') == BooleanType
    assert type_class_mapping('int') == IntType
    assert type_class_mapping('string') == StringType
    assert type_class_mapping('any') == AnyType
    assert type_class_mapping('object') == ObjectType
    assert type_class_mapping('list') == ListType
    assert type_class_mapping('map') == MapType
