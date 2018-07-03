# -*- coding: utf-8 -*-
import re

from lark.lexer import Token

from pytest import mark

from storyscript.compiler import Objects
from storyscript.parser import Tree


def test_objects_path():
    tree = Tree('path', [Token('WORD', 'var')])
    assert Objects.path(tree) == {'$OBJECT': 'path', 'paths': ['var']}


def test_objects_number():
    tree = Tree('number', [Token('INT', '1')])
    assert Objects.number(tree) == 1


def test_objects_replace_placeholders():
    result = Objects.replace_placeholders('hello, {{world}}', ['world'])
    assert result == 'hello, {}'


def test_objects_string():
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"blue"')])
    assert Objects.string(tree) == {'$OBJECT': 'string', 'string': 'blue'}


def test_objects_string_templating(patch):
    patch.object(Objects, 'path')
    patch.object(re, 'findall', return_value=['color'])
    tree = Tree('string', [Token('DOUBLE_QUOTED', '"{{color}}"')])
    result = Objects.string(tree)
    re.findall.assert_called_with(r'{{([^}]*)}}', '{{color}}')
    Objects.path.assert_called_with(Tree('path', [Token('WORD', 'color')]))
    assert result['string'] == '{}'
    assert result['values'] == [Objects.path()]


def test_objects_boolean():
    tree = Tree('boolean', [Token('TRUE', 'true')])
    assert Objects.boolean(tree) is True


def test_objects_boolean_false():
    tree = Tree('boolean', [Token('FALSE', 'false')])
    assert Objects.boolean(tree) is False


def test_objects_file():
    token = Token('FILEPATH', '`path`')
    assert Objects.file(token) == {'$OBJECT': 'file', 'string': 'path'}


def test_objects_list(patch, tree):
    patch.object(Objects, 'values')
    tree.children = ['value']
    result = Objects.list(tree)
    Objects.values.assert_called_with('value')
    assert result == {'$OBJECT': 'list', 'items': [Objects.values()]}


def test_objects_objects(patch, magic, tree):
    patch.many(Objects, ['string', 'values'])
    subtree = magic()
    tree.children = [subtree]
    result = Objects.objects(tree)
    subtree.node.assert_called_with('string')
    subtree.child.assert_called_with(1)
    Objects.string.assert_called_with(subtree.node())
    Objects.values.assert_called_with(subtree.child())
    expected = {'$OBJECT': 'dict', 'items': [[Objects.string(),
                                              Objects.values()]]}
    assert result == expected


def test_objects_types(tree):
    token = tree.child(0)
    assert Objects.types(tree) == {'$OBJECT': 'type', 'type': token.value}


def test_objects_method(patch, tree):
    patch.object(Objects, 'arguments')
    result = Objects.method(tree)
    Objects.arguments.assert_called_with(tree.node())
    expected = {'$OBJECT': 'method', 'method': 'execute',
                'service': tree.child().child().value,
                'command': tree.node().child().value,
                'output': None, 'args': Objects.arguments()}
    assert result == expected


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


def test_objects_values_method(patch, magic):
    patch.object(Objects, 'method')
    item = magic(data='path')
    tree = magic(child=lambda x: item)
    result = Objects.values(tree)
    Objects.method.assert_called_with(tree)
    assert result == Objects.method()


def test_objects_values_filepath(patch, magic):
    patch.object(Objects, 'file')
    item = magic(type='FILEPATH')
    tree = magic(child=lambda x: item)
    result = Objects.values(tree)
    Objects.file.assert_called_with(item)
    assert result == Objects.file()


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
    tree.find_data.return_value = filter(lambda x: x, ['argument'])
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
    tree.find_data.return_value = filter(lambda x: x, ['function_argument'])
    result = Objects.function_arguments(tree)
    tree.find_data.assert_called_with('function_argument')
    Objects.typed_argument.assert_called_with('function_argument')
    assert result == [Objects.typed_argument()]


def test_objects_expression(patch, tree):
    patch.object(Objects, 'values')
    tree.child.return_value = None
    result = Objects.expression(tree)
    Objects.values.assert_called_with(tree.node().child())
    assert result == [Objects.values()]


def test_objects_expression_comparison(patch, tree):
    patch.object(Objects, 'values')
    result = Objects.expression(tree)
    Objects.values.assert_called_with(tree.child().child())
    expression = '{} {} {}'.format('{}', tree.child().child(), '{}')
    assert result == [{'$OBJECT': 'expression', 'expression': expression,
                      'values': [Objects.values(), Objects.values()]}]
