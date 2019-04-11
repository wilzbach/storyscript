from storyscript.compiler.semantics.FunctionTable import Function
from storyscript.compiler.semantics.symbols.SymbolTypes import AnyType


def test_function__to_str():
    fn = Function('foo', {}, AnyType.instance())
    assert str(fn) == 'Function(foo)'
