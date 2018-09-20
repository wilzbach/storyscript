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


def test_objects_number_float():
    """
    Ensures that a float is compiled correctly.
    """
    tree = Tree('number', [Token('FLOAT', '1.2')])
    assert Objects.number(tree) == 1.2


def test_objects_replace_fillers():
    result = Objects.replace_fillers('hello, {world}', ['world'])
    assert result == 'hello, {}'


def test_objects_fillers_values(patch):
    patch.object(Objects, 'path')
    result = Objects.fillers_values(['one'])
    Objects.path.assert_called_with(Tree('path', [Token('WORD', 'one')]))
    assert result == [Objects.path()]


def test_objects_string():
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"blue"')])
    assert Objects.string(tree) == {'$OBJECT': 'string', 'string': 'blue'}


def test_objects_string_templating(patch):
    patch.many(Objects, ['placeholders_values', 'replace_placeholders'])
    patch.object(re, 'findall', return_value=['color'])
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"{color}"')])
    result = Objects.string(tree)
    re.findall.assert_called_with(r'{([^}]*)}', '{color}')
    Objects.placeholders_values.assert_called_with(re.findall())
    Objects.replace_placeholders.assert_called_with('{color}', re.findall())
    assert result['string'] == Objects.replace_placeholders()
    assert result['values'] == Objects.placeholders_values()


def test_objects_boolean():
    tree = Tree('boolean', [Token('TRUE', 'true')])
    assert Objects.boolean(tree) is True


def test_objects_boolean_false():
    tree = Tree('boolean', [Token('FALSE', 'false')])
    assert Objects.boolean(tree) is False


def test_objects_list(patch, tree):
    patch.object(Objects, 'values')
    tree.children = [Tree('value', 'value'), 'token']
    result = Objects.list(tree)
    Objects.values.assert_called_with(Tree('value', 'value'))
    assert result == {'$OBJECT': 'list', 'items': [Objects.values()]}


def test_objects_objects(patch, tree):
    patch.many(Objects, ['string', 'values'])
    subtree = Tree('key_value', [Tree('string', ['key']), 'value'])
    tree.children = [subtree]
    result = Objects.objects(tree)
    Objects.string.assert_called_with(subtree.string)
    Objects.values.assert_called_with('value')
    expected = {'$OBJECT': 'dict', 'items': [[Objects.string(),
                                              Objects.values()]]}
    assert result == expected


def test_objects_objects_key_path(patch, tree):
    """
    Ensures that objects like {x: 0} are compiled
    """
    patch.many(Objects, ['path', 'values'])
    subtree = Tree('key_value', [Tree('path', ['path'])])
    tree.children = [subtree]
    result = Objects.objects(tree)
    assert result['items'][0][0] == Objects.path()


def test_objects_types(tree):
    token = tree.child(0)
    assert Objects.types(tree) == {'$OBJECT': 'type', 'type': token.value}


@mark.parametrize('value_type', [
    'string', 'boolean', 'list', 'number', 'objects', 'types'
])
def test_objects_values(patch, magic, value_type):
    patch.object(Objects, value_type)
    item = magic(data=value_type)
    tree = magic(child=lambda x: item)
    result = Objects.values(tree)
    getattr(Objects, value_type).assert_called_with(item)
    assert result == getattr(Objects, value_type)()


def test_objects_values_path(patch, magic):
    patch.object(Objects, 'path')
    item = magic(type='NAME')
    tree = magic(child=lambda x: item)
    result = Objects.values(tree)
    Objects.path.assert_called_with(tree)
    assert result == Objects.path()


def test_objects_argument(patch, tree):
    patch.object(Objects, 'values')
    result = Objects.argument(tree)
    assert tree.child.call_count == 2
    Objects.values.assert_called_with(tree.child())
    expected = {'$OBJECT': 'argument', 'name': tree.child().value,
                'argument': Objects.values()}
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
    expected = {'$OBJECT': 'argument', 'name': tree.node().child().value,
                'argument': Objects.values()}
    assert result == expected


def test_objects_function_arguments(patch, tree):
    patch.object(Objects, 'typed_argument')
    tree.find_data.return_value = ['function_argument']
    result = Objects.function_arguments(tree)
    tree.find_data.assert_called_with('function_argument')
    Objects.typed_argument.assert_called_with('function_argument')
    assert result == [Objects.typed_argument()]


def test_fill_expression():
    assert Objects.fill_expression('one', 'two', 'three') == 'one two three'


def test_objects_expression(patch, tree):
    patch.object(Objects, 'values')
    tree.child.return_value = None
    tree.values = None
    result = Objects.expression(tree)
    Objects.values.assert_called_with(tree.path_value.child())
    assert result == [Objects.values()]


def test_objects_expression_absolute(patch, tree):
    patch.many(Objects, ['values', 'fill_expression'])
    result = Objects.expression(tree)
    Objects.fill_expression.assert_called_with('{}',
                                               tree.operator.child(0).value,
                                               '{}')
    assert result == {'$OBJECT': 'expression',
                      'expression': Objects.fill_expression(),
                      'values': [Objects.values(), Objects.values()]}


def test_objects_expression_comparison(patch, tree):
    patch.many(Objects, ['values', 'fill_expression'])
    tree.values = None
    result = Objects.expression(tree)
    Objects.values.assert_called_with(tree.child().child())
    Objects.fill_expression.assert_called_with('{}', tree.child().child(),
                                               '{}')
    expected = [{'$OBJECT': 'expression',
                 'expression': Objects.fill_expression(),
                 'values': [Objects.values(), Objects.values()]}]
    assert result == expected
