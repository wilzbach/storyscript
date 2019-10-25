from storyscript.compiler.semantics.functions.FunctionTable import \
        FunctionTable
from storyscript.compiler.semantics.types.Types import AnyType


def test_function_insert():
    fn = FunctionTable()
    fn.insert('foo', {}, AnyType.instance())

    fn_b = FunctionTable()
    fn_b.insert('bar', {}, AnyType.instance())
    fn_b.insert_fn_table(fn)

    assert list(fn_b.functions.keys()) == ['bar', 'foo']
