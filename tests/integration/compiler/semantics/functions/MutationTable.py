from pytest import mark

from storyscript.compiler.semantics.functions.MutationTable \
    import MutationTable
from storyscript.compiler.semantics.types.Types import BooleanType, IntType


@mark.parametrize('type_,expected', [
    (IntType.instance(), [
        'absolute', 'decrement', 'increment', 'isEven', 'isOdd'
    ]),
    (BooleanType.instance(), []),
])
def test_resolve_by_type(type_, expected):
    muts = MutationTable.instance().resolve_by_type(type_)
    muts_names = [m.name() for m in muts]
    assert sorted(muts_names) == expected
