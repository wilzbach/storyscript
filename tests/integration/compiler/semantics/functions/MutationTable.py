from pytest import mark

from storyscript.compiler.semantics.functions.HubMutations import Hub
from storyscript.compiler.semantics.functions.MutationTable import (
    MutationTable,
)
from storyscript.compiler.semantics.types.Types import BooleanType, IntType


@mark.parametrize(
    "type_,expected",
    [
        (
            IntType.instance(),
            ["absolute", "decrement", "increment", "isEven", "isOdd"],
        ),
        (BooleanType.instance(), []),
    ],
)
def test_resolve_by_type(type_, expected):
    muts = MutationTable.instance().resolve_by_type(type_)
    muts_names = [m.name() for m in muts]
    assert sorted(muts_names) == expected


def test_desc(mocker):
    builtins = [
        {
            "name": "increment",
            "input_type": "int",
            "return_type": "int",
            "desc": "returns the number + 1",
            "args": {"a": {"type": "int", "desc": "Dummy arg"}},
        },
        {
            "name": "decrement",
            "input_type": "int",
            "return_type": "int",
            "desc": "returns the number - 1",
            "args": {"b": {"type": "int", "desc": "Dummy arg"}},
        },
    ]
    hub = Hub(builtins)
    mocker.patch.object(Hub, "instance", return_value=hub)
    mt = MutationTable.init()
    muts = mt.resolve(IntType.instance(), "increment")
    mut = muts.single()
    assert mut.desc() == "returns the number + 1"
    fn = mut.instantiate(IntType.instance())
    arg_a = fn.args()["a"]
    assert arg_a.desc() == "Dummy arg"
