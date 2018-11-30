# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree


def test_values_true(parser):
    result = parser.parse('true\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.boolean.child(0) == Token('TRUE', 'true')


def test_values_false(parser):
    result = parser.parse('false\n')
    token = Token('FALSE', 'false')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.boolean.child(0) == token


def test_values_null(parser):
    result = parser.parse('null\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.void.child(0) == Token('NULL', 'null')


def test_values_int(parser):
    """
    Ensures that parsing an int produces the expected tree
    """
    result = parser.parse('3\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.number.child(0) == Token('INT', 3)


def test_values_int_negative(parser):
    """
    Ensures that parsing a negative int produces the expected tree
    """
    result = parser.parse('-3\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.number.child(0) == Token('INT', -3)


def test_values_float(parser):
    """
    Ensures that parsing a float produces the expected tree
    """
    result = parser.parse('3.14\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.number.child(0) == Token('FLOAT', 3.14)


def test_values_float_negative(parser):
    """
    Ensures that parsing a negative float produces the expected tree
    """
    result = parser.parse('-3.14\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.number.child(0) == Token('FLOAT', -3.14)


def test_values_single_quoted_string(parser):
    result = parser.parse("'red'\n")
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    expected = entity.values.string.child(0)
    assert expected == Token('SINGLE_QUOTED', "'red'")


def test_values_double_quoted_string(parser):
    result = parser.parse('"red"\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    expected = entity.values.string.child(0)
    assert expected == Token('DOUBLE_QUOTED', '"red"')


def test_values_list(parser):
    result = parser.parse('[3,4]\n')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    list = entity.values.list
    assert list.entity.values.number.child(0) == Token('INT', 3)
    assert list.child(3).values.number.child(0) == Token('INT', 4)


def test_values_list_empty(parser):
    result = parser.parse('[]\n')
    expected = Tree('list', [Token('_OSB', '['), Token('_CSB', ']')])
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.list == expected


def test_values_object(parser):
    result = parser.parse("{'color':'red','shape':1}\n")
    expression = result.block.rules.absolute_expression.expression
    values = expression.multiplication.exponential.factor.entity.values
    key_value = values.objects.key_value
    assert key_value.string.child(0) == Token('SINGLE_QUOTED', "'color'")
    entity = key_value.entity
    assert entity.values.string.child(0) == Token('SINGLE_QUOTED', "'red'")


def test_values_regular_expression(parser):
    """
    Ensures regular expressions are parsed correctly
    """
    result = parser.parse('/^foo/')
    token = Token('REGEXP', '/^foo/')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.regular_expression.child(0) == token


def test_values_regular_expression_flags(parser):
    """
    Ensures regular expressions with flags are parsed correctly
    """
    result = parser.parse('/^foo/i')
    token = Token('NAME', 'i')
    expression = result.block.rules.absolute_expression.expression
    entity = expression.multiplication.exponential.factor.entity
    assert entity.values.regular_expression.child(1) == token
