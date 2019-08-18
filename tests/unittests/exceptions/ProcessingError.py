# -*- coding: utf-8 -*-
from pytest import fixture, raises

from storyscript.exceptions.ProcessingError import ConstDict, ProcessingError


@fixture
def error():
    return ProcessingError('error')


@fixture
def token(magic):
    return magic()


def test_processingerror_init(patch, error):
    patch.many(ProcessingError, ['token_position', 'tree_position'])
    error = ProcessingError('error')
    assert error.error == 'error'
    ProcessingError.token_position.assert_called_with(None)
    ProcessingError.tree_position.assert_called_with(None)
    assert issubclass(ProcessingError, Exception)


def test_processingerror_init_token(patch):
    patch.many(ProcessingError, ['token_position', 'tree_position'])
    ProcessingError('error', token='token')
    ProcessingError.token_position.assert_called_with('token')


def test_processingerror_init_tree(patch):
    patch.many(ProcessingError, ['token_position', 'tree_position'])
    ProcessingError('error', tree='tree')
    ProcessingError.tree_position.assert_called_with('tree')


def test_processingerror_token_position(error, token):
    """
    Ensures token_position can extract the position from a token
    """
    error.token_position(token)
    assert error.line == token.line
    assert error.column == token.column
    assert error.end_column == token.end_column


def test_processingerror_token_position_none(error):
    """
    Ensures token_position can deal with null values
    """
    error.token_position(None)


def test_processingerror_tree_position(error, tree):
    """
    Ensures tree_position can extract the position from a tree
    """
    error.tree_position(tree)
    assert error.line == tree.line()
    assert error.column == tree.column()
    assert error.end_column == tree.end_column()


def test_processingerror_tree_position_none(error):
    """
    Ensures tree_position can deal with null values
    """
    error.tree_position(None)


def test_const_dict():
    """
    Ensures that the const dictionary provides access
    """
    d = ConstDict({'foo': 'bar', 'f2': 'b2'})
    assert d.foo == 'bar'
    assert d.f2 == 'b2'
    with raises(Exception):
        d.bar


def test_const_dict_str():
    """
    Ensures that the const dictionary can be serialized to string.
    """
    d = ConstDict({'foo': 'bar', 'f2': 'b2'})
    assert str(d) == "{'foo': 'bar', 'f2': 'b2'}"
