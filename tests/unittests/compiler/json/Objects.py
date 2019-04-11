# -*- coding: utf-8 -*-
from lark.lexer import Token

from pytest import fixture, mark

from storyscript.compiler.json.JSONExpressionVisitor import \
        JSONExpressionVisitor
from storyscript.compiler.json.Objects import Objects, split_into_time_parts
from storyscript.parser import Tree


@fixture
def token(magic):
    return magic()


def test_objects_names(tree):
    assert Objects().names(tree) == [tree.child(0).value]


def test_objects_names_many(magic, tree):
    shard = magic()
    shard.child().type = 'NAME'
    tree.children = [magic(), shard]
    assert Objects().names(tree) == [
        tree.child(0).value,
        {'$OBJECT': 'dot', 'dot': shard.child().value},
    ]


def test_objects_names_string(patch, magic, tree):
    """
    Ensures that paths like x['y'] are compiled correctly
    """
    patch.object(Objects, 'string')
    tree.children = [magic(), Tree('fragment', [Tree('string', 'token')])]
    result = Objects().names(tree)
    Objects.string.assert_called_with(Tree('string', 'token'))
    assert result[1] == Objects.string()


def test_objects_names_path(patch, magic, tree):
    """
    Ensures that paths like x[y] are compiled correctly
    """
    patch.object(Objects, 'path')
    subtree = Tree('path', ['token'])
    tree.children = [magic(), Tree('fragment', [subtree])]
    result = Objects().names(tree)
    Objects.path.assert_called_with(subtree)
    assert result[1] == Objects.path()


def test_objects_path(patch):
    patch.object(Objects, 'names')
    result = Objects().path('tree')
    Objects.names.assert_called_with('tree')
    assert result == {'$OBJECT': 'path', 'paths': Objects.names()}


def test_objects_mutation(patch, tree):
    """
    Ensures that mutations objects are compiled correctly.
    """
    patch.object(Objects, 'entity')
    patch.object(Objects, 'mutation_fragment')
    expected = {'method': 'mutation', 'name': [Objects.entity(tree.entity)],
                'args': [Objects.mutation_fragment(tree.mutation_fragment)]}
    assert Objects().mutation(tree) == expected


def test_objects_mutation_fragment(token):
    """
    Ensures that mutations fragments are compiled correctly.
    """
    tree = Tree('mutation', [token])
    expected = {'$OBJECT': 'mutation', 'mutation': token.value,
                'args': []}
    assert Objects().mutation_fragment(tree) == expected


def test_objects_mutation_fragment_from_service(token):
    """
    Ensures that mutations objects from service trees are compiled correctly.
    """
    tree = Tree('service_fragment', [Tree('command', [token])])
    expected = {'$OBJECT': 'mutation', 'mutation': token.value,
                'args': []}
    assert Objects().mutation_fragment(tree) == expected


def test_objects_mutation_fragment_arguments(patch, magic):
    """
    Ensures that mutation fragment objects with arguments are compiled
    correctly.
    """
    patch.object(Objects, 'arguments')
    tree = magic()
    result = Objects().mutation_fragment(tree)
    Objects.arguments.assert_called_with(tree)
    assert result['args'] == Objects.arguments()


def test_objects_path_fragments(magic):
    fragment = magic()
    fragment.child().type = 'NAME'
    tree = Tree('path', [magic(), fragment])
    assert Objects().path(tree)['paths'][1] == {
        '$OBJECT': 'dot', 'dot': fragment.child().value
    }


def test_objects_number():
    """
    Ensures that an int is compiled correctly.
    """
    tree = Tree('number', [Token('INT', '1')])
    assert Objects.number(tree) == {'$OBJECT': 'int', 'int': 1}
    tree = Tree('number', [Token('INT', '+1')])
    assert Objects.number(tree) == {'$OBJECT': 'int', 'int': 1}
    tree = Tree('number', [Token('INT', '-1')])
    assert Objects.number(tree) == {'$OBJECT': 'int', 'int': -1}


def test_objects_number_float():
    """
    Ensures that a float is compiled correctly.
    """
    tree = Tree('number', [Token('FLOAT', '1.2')])
    assert Objects.number(tree) == {'$OBJECT': 'float', 'float': 1.2}
    tree = Tree('number', [Token('FLOAT', '+1.2')])
    assert Objects.number(tree) == {'$OBJECT': 'float', 'float': 1.2}
    tree = Tree('number', [Token('FLOAT', '-1.2')])
    assert Objects.number(tree) == {'$OBJECT': 'float', 'float': -1.2}


def test_objects_name_to_path():
    result = Objects.name_to_path('name')
    assert result == Tree('path', [Token('NAME', 'name')])


def test_objects_name_to_path_dots():
    result = Objects.name_to_path('name.dot')
    fragment = Tree('path_fragment', [Token('NAME', 'dot')])
    children = [Token('NAME', 'name'), fragment]
    assert result == Tree('path', children)


def test_objects_string(patch, tree):
    result = Objects().string(tree)
    assert result == {'$OBJECT': 'string', 'string': tree.child(0).value}


def test_objects_boolean():
    tree = Tree('boolean', [Token('TRUE', 'true')])
    assert Objects.boolean(tree) == {'$OBJECT': 'boolean', 'boolean': True}


def test_objects_boolean_false():
    tree = Tree('boolean', [Token('FALSE', 'false')])
    assert Objects.boolean(tree) == {'$OBJECT': 'boolean', 'boolean': False}


def test_objects_list(patch, tree):
    patch.object(Objects, 'base_expression')
    tree.children = [Tree('value', 'value'), 'token']
    result = Objects().list(tree)
    Objects.base_expression.assert_called_with(Tree('value', 'value'))
    items = [Objects.base_expression()]
    assert result == {'$OBJECT': 'list', 'items': items}


def test_objects_objects(patch, tree):
    patch.many(Objects, ['string', 'base_expression'])
    subtree = Tree('key_value', [Tree('string', ['key']), 'value'])
    tree.children = [subtree]
    result = Objects().objects(tree)
    Objects.string.assert_called_with(subtree.string)
    Objects.base_expression.assert_called_with('value')
    items = [[Objects.string(), Objects.base_expression()]]
    expected = {'$OBJECT': 'dict', 'items': items}
    assert result == expected


def test_objects_objects_key_string(patch, tree):
    """
    Ensures that objects like {x: 0} are compiled
    """
    patch.many(Objects, ['base_expression', 'string'])
    subtree = Tree('key_value', [
        Tree('string', ['string.name']),
        Tree('path', ['value.path']),
    ])
    tree.children = [subtree]
    result = Objects().objects(tree)
    assert result['items'] == [[
        Objects.string(), Objects.base_expression()
    ]]


def test_objects_objects_key_path(patch, tree):
    """
    Ensures that objects like {x: 0} are compiled
    """
    patch.many(Objects, ['base_expression', 'path'])
    subtree = Tree('key_value', [
        Tree('path', ['string.name']),
        Tree('path', ['value.path']),
    ])
    tree.children = [subtree]
    result = Objects().objects(tree)
    assert result['items'] == [[
        Objects.path(), Objects.base_expression()
    ]]


def test_objects_regular_expression():
    """
    Ensures regular expressions are compiled correctly
    """
    tree = Tree('regular_expression', ['regexp'])
    result = Objects().regular_expression(tree)
    assert result == {'$OBJECT': 'regexp', 'regexp': tree.child(0)}


def test_objects_regular_expression_flags():
    tree = Tree('regular_expression', ['regexp', 'flags'])
    result = Objects().regular_expression(tree)
    assert result['flags'] == 'flags'


def test_objects_types(tree):
    token = tree.child(0)
    assert Objects.types(tree) == {'$OBJECT': 'type', 'type': token.value}


def test_objects_entity(patch, tree):
    patch.object(Objects, 'values')
    result = Objects().entity(tree)
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
    result = Objects().values(tree)
    getattr(Objects, value_type).assert_called_with(item)
    assert result == getattr(Objects, value_type)()


def test_objects_values_void(patch, magic):
    """
    Ensures Objects.values returns None when given a void value.
    """
    item = magic(data='void')
    tree = magic(child=lambda x: item)
    assert Objects().values(tree) is None


def test_objects_values_path(patch, magic):
    patch.object(Objects, 'path')
    item = magic(type='NAME')
    tree = magic(child=lambda x: item)
    result = Objects().values(tree)
    Objects.path.assert_called_with(tree)
    assert result == Objects.path()


def test_objects_argument(patch, tree):
    patch.object(Objects, 'expression')
    result = Objects().argument(tree)
    assert tree.child.call_count == 2
    Objects.expression.assert_called_with(tree.child())
    expected = {'$OBJECT': 'arg', 'name': tree.child().value,
                'arg': Objects.expression()}
    assert result == expected


def test_objects_arguments(patch, tree):
    patch.object(Objects, 'argument')
    tree.find_data.return_value = ['argument']
    result = Objects().arguments(tree)
    tree.find_data.assert_called_with('arguments')
    Objects.argument.assert_called_with('argument')
    assert result == [Objects.argument()]


def test_objects_typed_argument(patch, tree):
    patch.object(Objects, 'values')
    result = Objects().typed_argument(tree)
    expected = {'$OBJECT': 'arg', 'name': tree.child().value,
                'arg': {'$OBJECT': 'type', 'type': str(tree.child())}}
    assert result == expected


def test_objects_function_arguments(patch, tree):
    patch.object(Objects, 'typed_argument')
    tree.find_data.return_value = ['typed_argument']
    result = Objects().function_arguments(tree)
    tree.find_data.assert_called_with('typed_argument')
    Objects.typed_argument.assert_called_with('typed_argument')
    assert result == [Objects.typed_argument()]


def test_objects_expression(patch, tree):
    """
    Ensures Objects.expression calls or_expression
    """
    patch.many(JSONExpressionVisitor, ['expression'])
    tree.child(0).data = 'or_expression'
    r = Objects().expression(tree)
    JSONExpressionVisitor.expression.assert_called_with(tree)
    assert r == JSONExpressionVisitor.expression()


def test_objects_absolute_expression(patch, tree):
    """
    Ensures Objects.absolute_expression calls expression
    """
    patch.many(Objects, ['expression'])
    tree.child(0).data = 'expression'
    r = Objects().absolute_expression(tree)
    Objects.expression.assert_called_with(tree.child(0))
    assert r == Objects.expression()


def test_objects_base_expression(patch, tree):
    """
    Ensures Objects.base_expression calls expression
    """
    patch.many(Objects, ['expression'])
    tree.child(0).data = 'expression'
    r = Objects().base_expression(tree)
    Objects.expression.assert_called_with(tree.child(0))
    assert r == Objects.expression()


@mark.parametrize('example,expected', [
    ('1h5s', [(1, 'h'), (5, 's')]),
    ('1s', [(1, 's')]),
    ('001s', [(1, 's')]),
    ('2d3h4s', [(2, 'd'), (3, 'h'), (4, 's')]),
    ('1h5ms', [(1, 'h'), (5, 'ms')]),
    ('2d3s4ms', [(2, 'd'), (3, 's'), (4, 'ms')]),
])
def test_split_by_time(example, expected):
    """
    Test whether time splitting works correctly.
    """
    assert [*split_into_time_parts(example)] == expected
