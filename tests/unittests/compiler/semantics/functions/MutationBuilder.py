from pytest import mark, raises

from storyscript.compiler.semantics.functions.MutationBuilder import (
    parse_type,
    parse_type_inner,
)
from storyscript.compiler.semantics.types.GenericTypes import (
    ListGenericType,
    MapGenericType,
    TypeSymbol,
)
from storyscript.compiler.semantics.types.Types import (
    AnyType,
    BooleanType,
    FloatType,
    IntType,
    NoneType,
    StringType,
    TimeType,
)


@mark.parametrize(
    "text,expected",
    [
        ("foo[abc]", "abc"),
        ("foo[a,b]", "a,b"),
        ("foo[bar[abc]]", "bar[abc]"),
        ("List[List[any]]", "List[any]"),
        ("List[any]", "any"),
    ],
)
def test_parse_end(text, expected):
    assert parse_type_inner(text) == expected


def test_parse_end_error():
    with raises(AssertionError):
        parse_type_inner("foo[bar")


@mark.parametrize(
    "text,expected",
    [
        ("any", AnyType.instance()),
        ("boolean", BooleanType.instance()),
        ("float", FloatType.instance()),
        ("int", IntType.instance()),
        ("none", NoneType.instance()),
        ("string", StringType.instance()),
        ("time", TimeType.instance()),
        ("A", TypeSymbol("A")),
    ],
)
def test_parse_type_base(text, expected):
    t = parse_type(text)
    assert str(t) == str(expected)


@mark.parametrize(
    "text,expected_type,expected_symbols",
    [
        ("List[int]", ListGenericType, [IntType.instance()]),
        ("List[float]", ListGenericType, [FloatType.instance()]),
        (
            "Map[int,string]",
            MapGenericType,
            [IntType.instance(), StringType.instance()],
        ),
        ("List[A]", ListGenericType, [TypeSymbol("A")]),
        ("Map[A,B]", MapGenericType, [TypeSymbol("A"), TypeSymbol("B")]),
    ],
)
def test_parse_type(text, expected_type, expected_symbols):
    t = parse_type(text)
    assert isinstance(t, expected_type)
    assert t.symbols == expected_symbols


def test_parse_type_error_empty():
    with raises(AssertionError):
        parse_type("")


def test_parse_type_error():
    with raises(AssertionError):
        parse_type("foobar]")
