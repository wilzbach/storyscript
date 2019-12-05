from storyscript.compiler.semantics.functions.Function import Function, \
        MutationFunction
from storyscript.compiler.semantics.symbols.Symbols import Symbol
from storyscript.compiler.semantics.types.Types import AnyType, IntType, \
        StringType


def test_function__to_str():
    fn = Function('foo', {}, AnyType.instance())
    assert str(fn) == 'Function(foo)'


def test_function_pretty():
    fn = Function('foo', {}, AnyType.instance())
    assert fn.pretty() == 'foo()'


def test_function_name():
    fn = Function('foo', {}, AnyType.instance())
    assert fn.name() == 'foo'


def test_function_args_empty():
    fn = Function('foo', {}, AnyType.instance())
    assert fn.args() == {}


def test_function_args():
    args = {'a': Symbol('a', IntType.instance())}
    fn = Function('foo', args, AnyType.instance())
    assert fn.args() == args


def test_function_pretty_a():
    args = {'a': Symbol('a', IntType.instance())}
    fn = Function('foo', args, AnyType.instance())
    assert fn.pretty() == 'foo(a:`int`)'


def test_function_pretty_b():
    args = {'a': Symbol('a', IntType.instance()),
            'b': Symbol('b', StringType.instance())}
    fn = Function('foo', args, AnyType.instance())
    assert fn.pretty() == 'foo(a:`int` b:`string`)'


def test_mutation__to_str():
    fn = MutationFunction('foo', {}, AnyType.instance(), desc='')
    assert str(fn) == 'Mutation(foo)'


def test_mutation_desc():
    fn = MutationFunction('foo', {}, AnyType.instance(), desc='.desc.')
    assert fn.desc() == '.desc.'


def test_mutation_pretty():
    fn = MutationFunction('foo', {}, AnyType.instance(), desc='')
    assert fn.pretty() == 'foo()'


def test_mutation_pretty_a():
    args = {'a': Symbol('a', IntType.instance())}
    fn = MutationFunction('foo', args, AnyType.instance(), desc='')
    assert fn.pretty() == 'foo(a:`int`)'


def test_mutation_pretty_b():
    args = {'a': Symbol('a', IntType.instance()),
            'b': Symbol('b', StringType.instance())}
    fn = MutationFunction('foo', args, AnyType.instance(), desc='')
    assert fn.pretty() == 'foo(a:`int` b:`string`)'
