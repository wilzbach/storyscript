from storyscript.compiler.semantics.functions.Function import Function, \
        MutationFunction
from storyscript.compiler.semantics.types.Types import AnyType


def test_function__to_str():
    fn = Function('foo', {}, AnyType.instance())
    assert str(fn) == 'Function(foo)'


def test_mutation__to_str():
    fn = MutationFunction('foo', {}, AnyType.instance())
    assert str(fn) == 'Mutation(foo)'
