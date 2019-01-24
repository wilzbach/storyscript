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
    patch.object(Objects, 'entity')
    tree.children = [Tree('value', 'value'), 'token']
    result = Objects.list(tree)
    Objects.entity.assert_called_with(Tree('value', 'value'))
    assert result == {'$OBJECT': 'list', 'items': [Objects.entity()]}


def test_objects_objects(patch, tree):
    patch.many(Objects, ['string', 'entity'])
    subtree = Tree('key_value', [Tree('string', ['key']), 'value'])
    tree.children = [subtree]
    result = Objects.objects(tree)
    Objects.string.assert_called_with(subtree.string)
    Objects.entity.assert_called_with('value')
    expected = {'$OBJECT': 'dict', 'items': [[Objects.string(),
                                              Objects.entity()]]}
    assert result == expected


def test_objects_objects_key_path(patch, tree):
    """
    Ensures that objects like {x: 0} are compiled
    """
    patch.many(Objects, ['path', 'entity'])
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
    patch.object(Objects, 'entity')
    result = Objects.argument(tree)
    assert tree.child.call_count == 2
    Objects.entity.assert_called_with(tree.child())
    expected = {'$OBJECT': 'argument', 'name': tree.child().value,
                'argument': Objects.entity()}
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
    ('+', 'sum'), ('*', 'multiplication'), ('/', 'division'), ('%', 'modulus'),
    ('^', 'exponential'), ('-', 'subtraction'), ('and', 'and'),
    ('or', 'or'), ('not', 'not'), ('==', 'equals'), ('>', 'greater'),
    ('<', 'less'), ('!=', 'not_equal'), ('>=', 'greater_equal'),
    ('<=', 'less_equal')
])
def test_objects_expression_type(operator, expression, tree):
    assert Objects.expression_type(operator, tree) == expression


def test_objects_resolve_operand(patch, tree):
    """
    Ensures resolve_operand can resolve a simple operand.
    """
    patch.object(Objects, 'entity')
    tree.exponential = None
    tree.entity = None
    tree.factor.expression = None
    result = Objects.resolve_operand(tree)
    Objects.entity.assert_called_with(tree.factor.entity)
    assert result == Objects.entity()


def test_objects_resolve_operand_children(patch, tree):
    """
    Ensures resolve_operand can resolve nested operands.
    """
    patch.object(Objects, 'expression')
    tree.children = [1, 2]
    result = Objects.resolve_operand(tree)
    Objects.expression.assert_called_with(tree)
    assert result == Objects.expression()


def test_objects_resolve_operand_number(patch, tree):
    """
    Ensures resolve_operand can resolve a number.
    """
    patch.object(Objects, 'number')
    tree.data = 'number'
    result = Objects.resolve_operand(tree)
    Objects.number.assert_called_with(tree)
    assert result == Objects.number()


def test_objects_resolve_operand_sum_to_parenthesis(patch, tree):
    """
    Ensures resolve_operand can resolve a parenthesis operand
    """
    patch.object(Objects, 'expression')
    result = Objects.resolve_operand(tree)
    Objects.expression.assert_called_with(tree.exponential.factor.expression)
    assert result == Objects.expression()


def test_objects_resolve_operand_multiplication(patch, tree):
    """
    Ensures resolve_operand can resolve a multiplication tree.
    """
    patch.object(Objects, 'entity')
    tree.exponential.factor.expression = None
    result = Objects.resolve_operand(tree)
    Objects.entity.assert_called_with(tree.exponential.factor.entity)
    assert result == Objects.entity()


def test_objects_resolve_operand_multiplication_to_parenthesis(patch, tree):
    """
    Ensures resolve_operand can resolve a multiplication to a parenthesis.
    """
    patch.object(Objects, 'expression')
    tree.exponential = None
    result = Objects.resolve_operand(tree)
    Objects.expression.assert_called_with(tree.factor.expression)
    assert result == Objects.expression()


def test_objects_resolve_operand_exponential(patch, magic, tree):
    """
    Ensures resolve_operand can resolve an exponential tree
    """
    patch.object(Objects, 'expression')
    tree.exponential.children = [1, 2]
    result = Objects.resolve_operand(tree)
    Objects.expression.assert_called_with(tree.exponential)
    assert result == Objects.expression()


def test_objects_resolve_operand_factor(patch, tree):
    """
    Ensures resolve_operand can resolve a factor tree.
    """
    patch.object(Objects, 'entity')
    tree.exponential = None
    tree.factor = None
    result = Objects.resolve_operand(tree)
    Objects.entity.assert_called_with(tree.entity)
    assert result == Objects.entity()


def test_objects_expression_values(patch):
    patch.object(Objects, 'resolve_operand')
    tree = Tree('test', [])
    result = Objects.expression_values([tree, 'not_a_tree'])
    Objects.resolve_operand.assert_called_with(tree)
    assert result == [Objects.resolve_operand()]


def test_objects_expression(patch, tree):
    """
    Ensures Objects.expression can compile expressions
    """
    patch.many(Objects, ['expression_type', 'expression_values'])
    tree.number = None
    result = Objects.expression(tree)
    Objects.expression_values.assert_called_with(tree.children)
    Objects.expression_type.assert_called_with(tree.find_operator(), tree)
    expected = {'$OBJECT': 'expression',
                'values': Objects.expression_values(),
                'expression': Objects.expression_type()}
    assert result == expected


def test_objects_expression_one_child(patch, tree):
    """
    Ensures Objects.expression can compile expressions with one child tree
    """
    patch.many(Objects, ['expression_type', 'expression_values'])
    tree.number = None
    tree.children = [1]
    Objects.expression(tree)
    Objects.expression_values.assert_called_with(tree.child().children)
    Objects.expression_type.assert_called_with(tree.find_operator(), tree)


def test_objects_assertion(patch, tree):
    patch.many(Objects, ['entity', 'values', 'expression_type'])
    result = Objects.assertion(tree)
    Objects.entity.assert_called_with(tree.entity)
    Objects.values.assert_called_with(tree.child().child())
    Objects.expression_type.assert_called_with(tree.child().child(), tree)
    expected = [
        {'$OBJECT': 'assertion', 'assertion': Objects.expression_type(),
         'values': [Objects.entity(), Objects.values()]}
    ]
    assert result == expected
