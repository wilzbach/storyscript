# -*- coding: utf-8 -*-
from storyscript.compiler import Compiler


def test_assignments_true(parser):
    """
    Ensures that assignments to true are compiled correctly
    """
    tree = parser.parse('a = true')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [True]


def test_assignments_false(parser):
    """
    Ensures that assignments to false are compiled correctly
    """
    tree = parser.parse('a = false')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [False]


def test_assignments_null(parser):
    """
    Ensures that assignments to null are compiled correctly
    """
    tree = parser.parse('a = null')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [None]


def test_assignments_int(parser):
    """
    Ensures that assignments to integers are compiled correctly
    """
    tree = parser.parse('a = 0')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [0]


def test_assignments_int_positive(parser):
    """
    Ensures that assignments to positive integers are compiled correctly
    """
    tree = parser.parse('a = +3')
    result = Compiler.compile(tree)
    assert result['tree']['1']['args'] == [3]


def test_assignments_float(parser):
    """
    Ensures that assignments to floats are compiled correctly
    """
    tree = parser.parse('a = 3.14')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [3.14]


def test_assignments_string(parser):
    """
    Ensures that assignments to strings are compiled correctly
    """
    tree = parser.parse('a = "cake"')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    expected = [{'$OBJECT': 'string', 'string': 'cake'}]
    assert result['tree']['1']['args'] == expected


def test_assignments_list(parser):
    """
    Ensures that assignments to lists are compiled correctly
    """
    tree = parser.parse('a = [1, 2]')
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'list', 'items': [1, 2]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_assignments_list_empty(parser):
    """
    Ensures that assignments to empty lists are compiled correctly
    """
    tree = parser.parse('a = []')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{'$OBJECT': 'list', 'items': []}]


def test_assignments_list_multiline(parser):
    """
    Ensures that assignments to multiline lists are compiled correctly
    """
    tree = parser.parse('a = [\n\t1,\n\t2\n]')
    result = Compiler.compile(tree)
    args = [{'$OBJECT': 'list', 'items': [1, 2]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_assignments_object(parser):
    """
    Ensures that assignments to objects are compiled correctly
    """
    tree = parser.parse("a = {'x': 1, 'y': 3}")
    result = Compiler.compile(tree)
    items = [[{'$OBJECT': 'string', 'string': 'x'}, 1],
             [{'$OBJECT': 'string', 'string': 'y'}, 3]]
    arg = {'$OBJECT': 'dict', 'items': items}
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [arg]


def test_assignments_object_empty(parser):
    """
    Ensures that assignments to empty objects are compiled correctly
    """
    tree = parser.parse('a = {}')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{'$OBJECT': 'dict', 'items': []}]


def test_assignments_object_multiline(parser):
    """
    Ensures that assignments to multiline objects are compiled correctly
    """
    tree = parser.parse("a = {\n\t'x': 1,\n\t'y': 3\n}")
    result = Compiler.compile(tree)
    items = [[{'$OBJECT': 'string', 'string': 'x'}, 1],
             [{'$OBJECT': 'string', 'string': 'y'}, 3]]
    arg = {'$OBJECT': 'dict', 'items': items}
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [arg]


def test_assignments_regular_expression(parser):
    """
    Ensures regular expressions are compiled correctly
    """
    tree = parser.parse('a = /^foo/')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'regexp'
    assert result['tree']['1']['args'][0]['regexp'] == '/^foo/'


def test_assignments_regular_expression_flags(parser):
    """
    Ensures regular expressions with flags are compiled correctly
    """
    tree = parser.parse('a = /^foo/g')
    result = Compiler.compile(tree)
    assert result['tree']['1']['args'][0]['flags'] == 'g'


def test_assignments_sum(parser):
    """
    Ensures assignments to sums are compiled correctly
    """
    tree = parser.parse('a = 3 + 2')
    result = Compiler.compile(tree)
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [3, 2]


def test_assignments_multiplications(parser):
    """
    Ensures assignments to multiplications are compiled correctly
    """
    tree = parser.parse('a = 3 * 2')
    result = Compiler.compile(tree)
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'multiplication'
    assert result['tree']['1']['args'][0]['values'] == [3, 2]


def test_assignments_service(parser):
    """
    Ensures that service assignments are compiled correctly
    """
    tree = parser.parse('a = alpine echo')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['name'] == ['a']


def test_assignments_inline_expression(parser):
    tree = parser.parse('a = (alpine echo)')
    result = Compiler.compile(tree)
    entry = result['entrypoint']
    path = result['tree'][entry]['name']
    assert result['tree']['1']['args'] == [{'$OBJECT': 'path', 'paths': path}]


def test_assignments_mutation(parser):
    """
    Ensures that assigning a mutation on a value is compiled correctly
    """
    tree = parser.parse('0 increase by:1')
    result = Compiler.compile(tree)
    assert result['services'] == []
    assert result['tree']['1']['method'] == 'mutation'
    assert result['tree']['1']['args'][1]['$OBJECT'] == 'mutation'


def test_assignments_mutation_variable(parser):
    """
    Ensures that applying a mutation on a variable is not compiled as a
    service
    """
    tree = parser.parse('a = 0\na increase by:1')
    result = Compiler.compile(tree)
    assert result['services'] == []
    assert result['tree']['2']['method'] == 'mutation'
    assert result['tree']['2']['args'][1]['$OBJECT'] == 'mutation'


def test_assignments_string_escape_single(parser):
    """
    Ensures that assignments to strings with escaping are compiled correctly
    """
    tree = parser.parse('a = \'b.\\n.\\\\.\\\'.c\'')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    expected = [{'$OBJECT': 'string', 'string': 'b.\n.\\.\'.c'}]
    assert result['tree']['1']['args'] == expected


def test_assignments_string_escape_double(parser):
    """
    Ensures that assignments to strings with escaping are compiled correctly
    """
    tree = parser.parse(r'a = "b.\n.\\.\".c"')
    result = Compiler.compile(tree)
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    expected = [{'$OBJECT': 'string', 'string': 'b.\n.\\.".c'}]
    assert result['tree']['1']['args'] == expected
