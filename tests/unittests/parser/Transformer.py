# -*- coding: utf-8 -*-
from lark import Transformer as LarkTransformer

from pytest import fixture, mark, raises

from storyscript.exceptions import StorySyntaxError
from storyscript.parser import Transformer, Tree


@fixture
def syntax_error(patch):
    patch.init(StorySyntaxError)
    return StorySyntaxError.__init__


def test_transformer():
    keywords = ['function', 'if', 'else', 'foreach', 'return', 'returns',
                'try', 'catch', 'finally', 'when', 'as', 'import', 'while']
    assert Transformer.reserved_keywords == keywords
    assert issubclass(Transformer, LarkTransformer)


def test_transformer_arguments():
    assert Transformer.arguments('matches') == Tree('arguments', 'matches')


def test_transformer_arguments_short():
    matches = [Tree('path', ['token'])]
    expected = ['token', Tree('path', ['token'])]
    assert Transformer.arguments(matches) == Tree('arguments', expected)


def test_transformer_assignment(magic):
    matches = [magic()]
    assert Transformer.assignment(matches) == Tree('assignment', matches)


def test_transformer_assignment_error_backslash(syntax_error, magic):
    token = magic(value='/')
    matches = [magic(children=[token])]
    with raises(StorySyntaxError):
        Transformer.assignment(matches)
    syntax_error.assert_called_with('variables_backslash', token=token)


def test_transformer_assignment_error_dash(syntax_error, magic):
    token = magic(value='-')
    matches = [magic(children=[token])]
    with raises(StorySyntaxError):
        Transformer.assignment(matches)
    syntax_error.assert_called_with('variables_dash', token=token)


def test_transformer_command(patch, magic):
    matches = [magic()]
    assert Transformer.command(matches) == Tree('command', matches)


@mark.parametrize('keyword', [
    'function', 'if', 'else', 'foreach', 'return', 'returns', 'try', 'catch',
    'finally', 'when', 'as', 'import', 'while'
])
def test_transformer_command_keyword_error(syntax_error, magic, keyword):
    token = magic(value=keyword)
    matches = [token]
    with raises(StorySyntaxError):
        Transformer.command(matches)
    error_name = 'reserved_keyword_{}'.format(keyword)
    syntax_error.assert_called_with(error_name, token=token)


def test_transformer_path(patch, magic):
    matches = [magic()]
    assert Transformer.path(matches) == Tree('path', matches)


@mark.parametrize('keyword', [
    'function', 'if', 'else', 'foreach', 'return', 'returns', 'try', 'catch',
    'finally', 'when', 'as', 'import', 'while'
])
def test_transformer_path_keyword_error(syntax_error, magic, keyword):
    token = magic(value=keyword)
    matches = [token]
    with raises(StorySyntaxError):
        Transformer.path(matches)
    error_name = 'reserved_keyword_{}'.format(keyword)
    syntax_error.assert_called_with(error_name, token=token)


def test_transformer_service_block():
    """
    Ensures service_block nodes are transformed correctly
    """
    assert Transformer.service_block([]) == Tree('service_block', [])


def test_transformer_service_block_when(tree):
    """
    Ensures service_block nodes with a when block are transformed correctly
    """
    tree.block.rules = None
    matches = ['service_block', tree]
    result = Transformer.service_block(matches)
    assert result == Tree('service_block', matches)


def test_transformer_service_block_indented_args(tree, magic):
    """
    Ensures service_block with indented arguments are transformed correctly.
    """
    tree.find_data.return_value = ['argument']
    block = magic()
    matches = [block, tree]
    result = Transformer.service_block(matches)
    block.service_fragment.children.append.assert_called_with('argument')
    assert result == Tree('service_block', [block])


@mark.parametrize('rule', ['start', 'line', 'block', 'statement'])
def test_transformer_rules(rule):
    result = getattr(Transformer(), rule)(['matches'])
    assert isinstance(result, Tree)
    assert result.data == rule
    assert result.children == ['matches']
