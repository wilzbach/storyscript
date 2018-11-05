# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from pytest import fixture, mark, raises

from storyscript.exceptions import StorySyntaxError
from storyscript.parser import Transformer, Tree


@fixture
def transformer():
    return Transformer()


def test_transformer(transformer):
    assert issubclass(Transformer, LarkTransformer)


def test_transformer_arguments(transformer):
    assert transformer.arguments('matches') == Tree('arguments', 'matches')


def test_transformer_arguments_short(transformer):
    matches = [Tree('path', ['token'])]
    expected = ['token', Tree('path', ['token'])]
    assert transformer.arguments(matches) == Tree('arguments', expected)


def test_transformer_assignment(magic, transformer):
    matches = [magic()]
    assert transformer.assignment(matches) == Tree('assignment', matches)


def test_transformer_assignment_error_backslash(patch, magic, transformer):
    patch.init(StorySyntaxError)
    token = magic(value='/')
    matches = [magic(children=[token])]
    with raises(StorySyntaxError):
        transformer.assignment(matches)
    error = 'variables-backslash'
    kwargs = {'line': token.line, 'column': token.column}
    StorySyntaxError.__init__.assert_called_with(error, **kwargs)


def test_transformer_assignment_error_dash(patch, magic, transformer):
    patch.init(StorySyntaxError)
    token = magic(value='-')
    matches = [magic(children=[token])]
    with raises(StorySyntaxError):
        transformer.assignment(matches)
    kwargs = {'line': token.line, 'column': token.column}
    StorySyntaxError.__init__.assert_called_with('variables-dash', **kwargs)


def test_transformer_service_block(transformer):
    """
    Ensures service_block nodes are transformed correctly
    """
    assert transformer.service_block([]) == Tree('service_block', [])


def test_transformer_service_block_when(tree, transformer):
    """
    Ensures service_block nodes with a when block are transformed correctly
    """
    tree.block.rules = None
    matches = ['service_block', tree]
    result = transformer.service_block(matches)
    assert result == Tree('service_block', matches)


def test_transformer_service_block_indented_args(tree, magic, transformer):
    """
    Ensures service_block with indented arguments are transformed correctly.
    """
    tree.find_data.return_value = ['argument']
    block = magic()
    matches = [block, tree]
    result = transformer.service_block(matches)
    block.service_fragment.children.append.assert_called_with('argument')
    assert result == Tree('service_block', [block])


@mark.parametrize('rule', ['start', 'line', 'block', 'command', 'statement'])
def test_transformer_rules(rule, transformer):
    result = getattr(transformer, rule)(['matches'])
    assert isinstance(result, Tree)
    assert result.data == rule
    assert result.children == ['matches']
