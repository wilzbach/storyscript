from pytest import mark

from storyhub.sdk.service.output import (
    OutputAny,
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

from storyscript.compiler.semantics.types.Types import AnyType, \
    BooleanType, FloatType, IntType, ListType, MapType, \
    NoneType, ObjectType, RegExpType, StringType
from storyscript.hub.TypeMappings import TypeMappings


@mark.parametrize('expected,hub', [
    (BooleanType.instance(), OutputBoolean(data={})),
    (IntType.instance(), OutputInt(data={})),
    (FloatType.instance(), OutputFloat(data={})),
    (NoneType.instance(), OutputNone(data={})),
    (AnyType.instance(), OutputAny(data={})),
    (RegExpType.instance(), OutputRegex(data={})),
    (StringType.instance(), OutputEnum(data={})),
    (ListType(AnyType.instance()), OutputList(OutputAny.create(), data={})),
    (ListType(IntType.instance()), OutputList(OutputInt(data={}), data={})),
    (MapType(IntType.instance(), StringType.instance()),
        OutputMap(OutputInt(data={}), OutputString(data={}), data={})),
    (ObjectType({'i': IntType.instance(), 's': StringType.instance()}),
        OutputObject({'i': OutputInt(data={}), 's': OutputString(data={})},
                     data={})),
    (ObjectType({'p': IntType.instance()}),
        OutputObject({'p': OutputInt(data={})}, data={})),
    (ObjectType({}), OutputObject({}, data={})),
])
def test_types(hub, expected):
    assert TypeMappings.get_type_instance(hub) == expected
