# -*- coding: utf-8 -*-
import re

from lark.lexer import Token

from pytest import fixture, mark

from storyscript.compiler import Objects
from storyscript.parser import Tree


@fixture
def token(magic):
    return magic()


def test_objects_names(tree):
    assert Objects.names(tree) == [tree.child(0).value]


def test_objects_names_many(magic, tree):
    shard = magic()
    tree.children = [magic(), shard]
    assert Objects.names(tree) == [tree.child(0).value, shard.child().value]


def test_objects_names_string(patch, magic, tree):
    """
    Ensures that paths like x['y'] are compiled correctly
    """
    patch.object(Objects, 'string')
    tree.children = [magic(), Tree('fragment', [Tree('string', 'token')])]
    result = Objects.names(tree)
    Objects.string.assert_called_with(Tree('string', 'token'))
    assert result[1] == Objects.string()


def test_objects_names_path(patch, magic, tree):
    """
    Ensures that paths like x[y] are compiled correctly
    """
    patch.object(Objects, 'path')
    subtree = Tree('path', ['token'])
    tree.children = [magic(), Tree('fragment', [subtree])]
    result = Objects.names(tree)
    Objects.path.assert_called_with(subtree)
    assert result[1] == Objects.path()


def test_objects_path(patch):
    patch.object(Objects, 'names')
    result = Objects.path('tree')
    Objects.names.assert_called_with('tree')
    assert result == {'$OBJECT': 'path', 'paths': Objects.names()}


def test_objects_mutation(token):
    """
    Ensures that mutations objects are compiled correctly.
    """
    tree = Tree('mutation', [token])
    expected = {'$OBJECT': 'mutation', 'mutation': token.value,
                'arguments': []}
    assert Objects.mutation(tree) == expected


def test_objects_mutation_from_service(token):
    """
    Ensures that mutations objects from service trees are compiled correctly.
    """
    tree = Tree('service_fragment', [Tree('command', [token])])
    expected = {'$OBJECT': 'mutation', 'mutation': token.value,
                'arguments': []}
    assert Objects.mutation(tree) == expected


def test_objects_mutation_arguments(patch, magic):
    """
    Ensures that mutations objects with arguments are compiled correctly.
    """
    patch.object(Objects, 'arguments')
    tree = magic()
    result = Objects.mutation(tree)
    Objects.arguments.assert_called_with(tree.arguments)
    assert result['arguments'] == Objects.arguments()


def test_objects_path_fragments(magic):
    fragment = magic()
    tree = Tree('path', [magic(), fragment])
    assert Objects.path(tree)['paths'][1] == fragment.child().value


def test_objects_number():
    """
    Ensures that an int is compiled correctly.
    """
    tree = Tree('number', [Token('INT', '1')])
    assert Objects.number(tree) == 1
    tree = Tree('number', [Token('INT', '+1')])
    assert Objects.number(tree) == 1
    tree = Tree('number', [Token('INT', '-1')])
    assert Objects.number(tree) == -1


def test_objects_number_float():
    """
    Ensures that a float is compiled correctly.
    """
    tree = Tree('number', [Token('FLOAT', '1.2')])
    assert Objects.number(tree) == 1.2
    tree = Tree('number', [Token('FLOAT', '+1.2')])
    assert Objects.number(tree) == 1.2
    tree = Tree('number', [Token('FLOAT', '-1.2')])
    assert Objects.number(tree) == -1.2


def test_objects_replace_fillers():
    result = Objects.replace_fillers('hello, {world}', ['world'])
    assert result == 'hello, {}'


def test_objects_name_to_path():
    result = Objects.name_to_path('name')
    assert result == Tree('path', [Token('NAME', 'name')])


def test_objects_name_to_path_dots():
    result = Objects.name_to_path('name.dot')
    fragment = Tree('path_fragment', [Token('NAME', 'dot')])
    children = [Token('NAME', 'name'), fragment]
    assert result == Tree('path', children)


def test_objects_fillers_values(patch):
    patch.many(Objects, ['path', 'name_to_path'])
    result = Objects.fillers_values(['one'])
    Objects.name_to_path.assert_called_with('one')
    Objects.path.assert_called_with(Objects.name_to_path())
    assert result == [Objects.path()]


def test_objects_unescape_string(tree):
    result = Objects.unescape_string(tree)
    string = tree.child().value[1:-1]
    assert result == string.encode().decode().encode().decode()


def test_objects_string(patch, tree):
    patch.object(Objects, 'unescape_string')
    patch.object(re, 'findall', return_value=[])
    result = Objects.string(tree)
    Objects.unescape_string.assert_called_with(tree)
    re.findall.assert_called_with(r'(?<!\\){(.*?)(?<!\\)}',
                                  Objects.unescape_string())
    assert result == {'$OBJECT': 'string', 'string': Objects.unescape_string()}


def test_objects_string_templating(patch):
    patch.many(Objects, ['unescape_string', 'fillers_values',
                         'replace_fillers'])
    patch.object(re, 'findall', return_value=['var'])
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"{var} is \\{notvar\\}"')])
    result = Objects.string(tree)
    Objects.fillers_values.assert_called_with(re.findall())
    Objects.replace_fillers.assert_called_with(Objects.unescape_string(),
                                               re.findall())
    assert result['string'] == Objects.replace_fillers()
    assert result['values'] == Objects.fillers_values()


def test_objects_boolean():
    tree = Tree('boolean', [Token('TRUE', 'true')])
    assert Objects.boolean(tree) is True


def test_objects_boolean_false():
    tree = Tree('boolean', [Token('FALSE', 'false')])
    assert Objects.boolean(tree) is False


def test_objects_list(patch, tree):
    patch.object(Objects, 'expression')
    tree.children = [Tree('value', 'value'), 'token']
    result = Objects.list(tree)
    Objects.expression.assert_called_with(Tree('value', 'value'))
    assert result == {'$OBJECT': 'list', 'items': [Objects.expression()]}


def test_objects_objects(patch, tree):
    patch.many(Objects, ['string', 'expression'])
    subtree = Tree('key_value', [Tree('string', ['key']), 'value'])
    tree.children = [subtree]
    result = Objects.objects(tree)
    Objects.string.assert_called_with(subtree.string)
    Objects.expression.assert_called_with('value')
    expected = {'$OBJECT': 'dict', 'items': [[Objects.string(),
                                              Objects.expression()]]}
    assert result == expected


def test_objects_objects_key_path(patch, tree):
    """
    Ensures that objects like {x: 0} are compiled
    """
    patch.many(Objects, ['path', 'expression'])
    subtree = Tree('key_value', [Tree('path', ['path'])])
    tree.children = [subtree]
    result = Objects.objects(tree)
    assert result['items'][0][0] == Objects.path()


def test_objects_regular_expression():
    """
    Ensures regular expressions are compiled correctly
    """
    tree = Tree('regular_expression', ['regexp'])
    result = Objects.regular_expression(tree)
    assert result == {'$OBJECT': 'regexp', 'regexp': tree.child(0)}


def test_objects_regular_expression_flags():
    tree = Tree('regular_expression', ['regexp', 'flags'])
    result = Objects.regular_expression(tree)
    assert result['flags'] == 'flags'


def test_objects_types(tree):
    token = tree.child(0)
    assert Objects.types(tree) == {'$OBJECT': 'type', 'type': token.value}


def test_objects_entity(patch, tree):
    patch.object(Objects, 'values')
    result = Objects.entity(tree)
    tree.child.assert_called_with(0)
    Objects.values.assert_called_with(tree.child())
    assert result == Objects.values()


@mark.parametrize('value_type', [
    'string', 'boolean', 'list', 'number', 'objects', 'regular_expression',
    'types'
])
def test_objects_values(patch, magic, value_type):
    patch.object(Objects, value_type)
    item = magic(data=value_type)
    tree = magic(child=lambda x: item)
    result = Objects.values(tree)
    getattr(Objects, value_type).assert_called_with(item)
    assert result == getattr(Objects, value_type)()


def test_objects_values_void(patch, magic):
    """
    Ensures Objects.values returns None when given a void value.
    """
    item = magic(data='void')
    tree = magic(child=lambda x: item)
    assert Objects.values(tree) is None


def test_objects_values_path(patch, magic):
    patch.object(Objects, 'path')
    item = magic(type='NAME')
    tree = magic(child=lambda x: item)
    result = Objects.values(tree)
    Objects.path.assert_called_with(tree)
    assert result == Objects.path()


def test_objects_argument(patch, tree):
    patch.object(Objects, 'expression')
    result = Objects.argument(tree)
    assert tree.child.call_count == 2
    Objects.expression.assert_called_with(tree.child())
    expected = {'$OBJECT': 'argument', 'name': tree.child().value,
                'argument': Objects.expression()}
    assert result == expected


def test_objects_arguments(patch, tree):
    patch.object(Objects, 'argument')
    tree.find_data.return_value = ['argument']
    result = Objects.arguments(tree)
    tree.find_data.assert_called_with('arguments')
    Objects.argument.assert_called_with('argument')
    assert result == [Objects.argument()]


def test_objects_typed_argument(patch, tree):
    patch.object(Objects, 'values')
    result = Objects.typed_argument(tree)
    Objects.values.assert_called_with(Tree('anon', [tree.child(1)]))
    expected = {'$OBJECT': 'argument', 'name': tree.child().value,
                'argument': Objects.values()}
    assert result == expected


def test_objects_function_arguments(patch, tree):
    patch.object(Objects, 'typed_argument')
    tree.find_data.return_value = ['typed_argument']
    result = Objects.function_arguments(tree)
    tree.find_data.assert_called_with('typed_argument')
    Objects.typed_argument.assert_called_with('typed_argument')
    assert result == [Objects.typed_argument()]


@mark.parametrize('operator, expression', [
    ('PLUS', 'sum'), ('MULTIPLIER', 'multiplication'),
    ('BSLASH', 'division'), ('MODULUS', 'modulus'),
    ('POWER', 'exponential'), ('DASH', 'subtraction'), ('AND', 'and'),
    ('OR', 'or'), ('NOT', 'not'),
    ('EQUAL', 'equals'), ('GREATER', 'greater'),
    ('LESSER', 'less'), ('NOT_EQUAL', 'not_equal'),
    ('GREATER_EQUAL', 'greater_equal'), ('LESSER_EQUAL', 'less_equal'),
])
def test_objects_expression_type(operator, expression, tree):
    assert Objects.expression_type(operator, tree) == expression


def test_objects_expression(patch, tree):
    """
    Ensures Objects.expression calls or_expression
    """
    patch.many(Objects, ['or_expression'])
    tree.child(0).data = 'or_expression'
    Objects.expression(tree)
    Objects.or_expression.assert_called_with(tree.child(0))


def test_objects_assertion_single_entity(patch, tree):
    """
    Ensures that Objects.assertion handles single entities
    """
    patch.many(Objects, ['expression'])
    Objects.expression.return_value = True
    result = Objects.assertion(tree)
    Objects.expression.assert_called_with(tree.expression)
    assert result == [Objects.expression()]


def test_objects_assertion(patch, tree):
    patch.many(Objects, ['expression'])
    result = Objects.assertion(tree)
    Objects.expression.assert_called_with(tree.expression)
    expected = [{
        '$OBJECT': 'assertion',
        'assertion': Objects.expression()['expression'],
        'values': Objects.expression()['values']
    }]
    assert result == expected


def test_objects_absolute_expression(patch, tree):
    """
    Ensures Objects.absolute_expression calls expression
    """
    patch.many(Objects, ['expression'])
    tree.child(0).data = 'expression'
    Objects.absolute_expression(tree)
    Objects.expression.assert_called_with(tree.child(0))


def test_objects_build_unary_expression(patch, tree, magic):
    """
    Ensures Objects.build_unary_expression builds an expression properly
    """
    patch.many(Objects, ['expression_type'])
    op = '.my.op.'
    left = magic()
    result = Objects.build_unary_expression(tree, op, left)
    Objects.expression_type.assert_called_with(op, tree)
    assert result == {
        '$OBJECT': 'expression',
        'expression': Objects.expression_type(),
        'values':  [left],
    }


def test_objects_build_binary_expression(patch, tree, magic):
    """
    Ensures Objects.build_binary_expression builds an expression properly
    """
    patch.many(Objects, ['expression_type'])
    op = magic()
    left = magic()
    right = magic()
    result = Objects.build_binary_expression(tree, op, left, right)
    Objects.expression_type.assert_called_with(op.type, tree)
    assert result == {
        '$OBJECT': 'expression',
        'expression': Objects.expression_type(),
        'values':  [left, right],
    }


def test_objects_primary_expression_entity(patch, tree):
    """
    Ensures Objects.primary_expression works with an entity node
    """
    patch.many(Objects, ['entity'])
    tree.child(0).data = 'entity'
    r = Objects.primary_expression(tree)
    Objects.entity.assert_called_with(tree.entity)
    assert r == Objects.entity()


def test_objects_primary_expression_two(patch, tree):
    """
    Ensures Objects.primary_expression works with a or_expression node
    """
    patch.many(Objects, ['entity', 'or_expression'])
    tree.child(0).data = 'or_expression'
    r = Objects.primary_expression(tree)
    Objects.or_expression.assert_called_with(tree.child(0))
    assert r == Objects.or_expression()


def test_objects_pow_expression_one(patch, tree):
    """
    Ensures Objects.pow_expression works with one node
    """
    patch.many(Objects, ['primary_expression'])
    tree.child(0).data = 'primary_expression'
    tree.children = [1]
    r = Objects.pow_expression(tree)
    Objects.primary_expression.assert_called_with(tree.child(0))
    assert r == Objects.primary_expression()


def test_objects_pow_expression_two(patch, tree):
    """
    Ensures Objects.pow_expression works with two nodes
    """
    patch.many(Objects, ['build_binary_expression', 'primary_expression',
                         'unary_expression'])
    tree.child(1).type = 'POWER'
    tree.children = [1, '+', 2]
    r = Objects.pow_expression(tree)
    Objects.build_binary_expression.assert_called_with(
        tree, tree.child(1),
        Objects.primary_expression(tree.child(0)),
        Objects.unary_expression(tree.child(2)))
    assert r == Objects.build_binary_expression()


def test_objects_unary_expression_one(patch, tree):
    """
    Ensures Objects.unary_expression works with one node
    """
    patch.many(Objects, ['pow_expression'])
    tree.child(0).data = 'pow_expression'
    tree.children = [1]
    r = Objects.unary_expression(tree)
    Objects.pow_expression.assert_called_with(tree.child(0))
    assert r == Objects.pow_expression()


def test_objects_unary_expression_two(patch, tree):
    """
    Ensures Objects.unary_expression works with two nodes
    """
    patch.many(Objects, ['build_unary_expression'])
    tree.child(1).data = 'unary_operator'
    unary_expression = Objects.unary_expression
    patch.object(Objects, 'unary_expression')
    r = unary_expression(tree)
    Objects.build_unary_expression.assert_called_with(
        tree, tree.child(1), Objects.unary_expression(tree.child(0)))
    assert r == Objects.build_unary_expression()


def test_objects_mul_expression_one(patch, tree):
    """
    Ensures Objects.mul_expression works with one node
    """
    patch.many(Objects, ['unary_expression'])
    tree.child(0).data = 'unary_expression'
    tree.children = [1]
    r = Objects.mul_expression(tree)
    Objects.unary_expression.assert_called_with(tree.child(0))
    assert r == Objects.unary_expression()


def test_objects_mul_expression_two(patch, tree):
    """
    Ensures Objects.mul_expression works with two nodes
    """
    patch.many(Objects, ['build_binary_expression', 'unary_expression'])
    tree.child(1).data = 'mul_operator'
    tree.children = [1, '*', 2]
    mul_expression = Objects.mul_expression
    patch.object(Objects, 'mul_expression')
    r = mul_expression(tree)
    Objects.build_binary_expression.assert_called_with(
        tree, tree.child(1).child(0),
        Objects.mul_expression(tree.child(0)),
        Objects.unary_expression(tree.child(2)))
    assert r == Objects.build_binary_expression()


def test_objects_arith_expression_one(patch, tree):
    """
    Ensures Objects.arith_expression works with one node
    """
    patch.many(Objects, ['mul_expression'])
    tree.child(0).data = 'mul_expression'
    tree.children = [1]
    r = Objects.arith_expression(tree)
    Objects.mul_expression.assert_called_with(tree.child(0))
    assert r == Objects.mul_expression()


def test_objects_arith_expression_two(patch, tree):
    """
    Ensures Objects.arith_expression works with two nodes
    """
    patch.many(Objects, ['build_binary_expression', 'mul_expression'])
    tree.child(1).data = 'arith_operator'
    tree.children = [1, '+', 2]
    arith_expression = Objects.arith_expression
    patch.object(Objects, 'arith_expression')
    r = arith_expression(tree)
    Objects.build_binary_expression.assert_called_with(
        tree, tree.child(1).child(0),
        Objects.arith_expression(tree.child(0)),
        Objects.mul_expression(tree.child(2)))
    assert r == Objects.build_binary_expression()


def test_objects_or_expression_one(patch, tree):
    """
    Ensures Objects.or_expression works with one node
    """
    patch.many(Objects, ['and_expression'])
    tree.child(0).data = 'and_expression'
    tree.children = [1]
    r = Objects.or_expression(tree)
    Objects.and_expression.assert_called_with(tree.child(0))
    assert r == Objects.and_expression()


def test_objects_or_expression_two(patch, tree):
    """
    Ensures Objects.or_expression works with two nodes
    """
    patch.many(Objects, ['build_binary_expression', 'and_expression'])
    tree.child(1).type = 'OR'
    tree.children = [1, 'or', 2]
    or_expression = Objects.or_expression
    patch.object(Objects, 'or_expression')
    r = or_expression(tree)
    Objects.build_binary_expression.assert_called_with(
        tree, tree.child(1),
        Objects.or_expression(tree.child(0)),
        Objects.and_expression(tree.child(2)))
    assert r == Objects.build_binary_expression()


def test_objects_and_expression_one(patch, tree):
    """
    Ensures Objects.and_expression works with one node
    """
    patch.many(Objects, ['cmp_expression'])
    tree.child(0).data = 'cmp_expression'
    tree.children = [1]
    r = Objects.and_expression(tree)
    Objects.cmp_expression.assert_called_with(tree.child(0))
    assert r == Objects.cmp_expression()


def test_objects_and_expression_two(patch, tree):
    """
    Ensures Objects.and_expression works with two nodes
    """
    patch.many(Objects, ['build_binary_expression', 'cmp_expression'])
    tree.child(1).type = 'AND'
    tree.children = [1, 'and', 2]
    and_expression = Objects.and_expression
    patch.object(Objects, 'and_expression')
    r = and_expression(tree)
    Objects.build_binary_expression.assert_called_with(
        tree, tree.child(1),
        Objects.and_expression(tree.child(0)),
        Objects.cmp_expression(tree.child(2)))
    assert r == Objects.build_binary_expression()


def test_objects_cmp_expression_one(patch, tree):
    """
    Ensures Objects.and_expression works with one node
    """
    patch.many(Objects, ['arith_expression'])
    tree.child(0).data = 'arith_expression'
    tree.children = [1]
    r = Objects.cmp_expression(tree)
    Objects.arith_expression.assert_called_with(tree.child(0))
    assert r == Objects.arith_expression()


def test_objects_cmp_expression_two(patch, tree):
    """
    Ensures Objects.and_expression works with two nodes
    """
    patch.many(Objects, ['build_binary_expression', 'arith_expression'])
    tree.child(1).data = 'cmp_operator'
    tree.children = [1, '==', 2]
    cmp_expression = Objects.cmp_expression
    patch.object(Objects, 'cmp_expression')
    r = cmp_expression(tree)
    Objects.build_binary_expression.assert_called_with(
        tree, tree.child(1).child(0),
        Objects.cmp_expression(tree.child(0)),
        Objects.arith_expression(tree.child(2)))
    assert r == Objects.build_binary_expression()
