# -*- coding: utf-8 -*-
from storyscript.Api import Api


def test_assignments_true():
    """
    Ensures that assignments to true are compiled correctly
    """
    result = Api.loads('a = true')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [True]


def test_assignments_false():
    """
    Ensures that assignments to false are compiled correctly
    """
    result = Api.loads('a = false')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [False]


def test_assignments_null():
    """
    Ensures that assignments to null are compiled correctly
    """
    result = Api.loads('a = null')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [None]


def test_assignments_int():
    """
    Ensures that assignments to integers are compiled correctly
    """
    result = Api.loads('a = 0')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [0]


def test_assignments_int_positive():
    """
    Ensures that assignments to positive integers are compiled correctly
    """
    result = Api.loads('a = +3')
    assert result['tree']['1']['args'] == [3]


def test_assignments_float():
    """
    Ensures that assignments to floats are compiled correctly
    """
    result = Api.loads('a = 3.14')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [3.14]


def test_assignments_string():
    """
    Ensures that assignments to strings are compiled correctly
    """
    result = Api.loads('a = "cake"')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    expected = [{'$OBJECT': 'string', 'string': 'cake'}]
    assert result['tree']['1']['args'] == expected


def test_assignments_list():
    """
    Ensures that assignments to lists are compiled correctly
    """
    result = Api.loads('a = [1, 2]')
    args = [{'$OBJECT': 'list', 'items': [1, 2]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_assignments_list_empty():
    """
    Ensures that assignments to empty lists are compiled correctly
    """
    result = Api.loads('a = []')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{'$OBJECT': 'list', 'items': []}]


def test_assignments_list_multiline():
    """
    Ensures that assignments to multiline lists are compiled correctly
    """
    result = Api.loads('a = [\n\t1,\n\t2\n]')
    args = [{'$OBJECT': 'list', 'items': [1, 2]}]
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == args


def test_assignments_object():
    """
    Ensures that assignments to objects are compiled correctly
    """
    result = Api.loads("a = {'x': 1, 'y': 3}")
    items = [[{'$OBJECT': 'string', 'string': 'x'}, 1],
             [{'$OBJECT': 'string', 'string': 'y'}, 3]]
    arg = {'$OBJECT': 'dict', 'items': items}
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['args'] == [arg]


def test_assignments_object_empty():
    """
    Ensures that assignments to empty objects are compiled correctly
    """
    result = Api.loads('a = {}')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [{'$OBJECT': 'dict', 'items': []}]


def test_assignments_object_multiline():
    """
    Ensures that assignments to multiline objects are compiled correctly
    """
    result = Api.loads("a = {\n\t'x': 1,\n\t'y': 3\n}")
    items = [[{'$OBJECT': 'string', 'string': 'x'}, 1],
             [{'$OBJECT': 'string', 'string': 'y'}, 3]]
    arg = {'$OBJECT': 'dict', 'items': items}
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'] == [arg]


def test_assignments_regular_expression():
    """
    Ensures regular expressions are compiled correctly
    """
    result = Api.loads('a = /^foo/')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'regexp'
    assert result['tree']['1']['args'][0]['regexp'] == '/^foo/'


def test_assignments_regular_expression_flags():
    """
    Ensures regular expressions with flags are compiled correctly
    """
    result = Api.loads('a = /^foo/g')
    assert result['tree']['1']['args'][0]['flags'] == 'g'


def test_assignments_sum():
    """
    Ensures assignments to sums are compiled correctly
    """
    result = Api.loads('a = 3 + 2')
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'sum'
    assert result['tree']['1']['args'][0]['values'] == [3, 2]


def test_assignments_multiplications():
    """
    Ensures assignments to multiplications are compiled correctly
    """
    result = Api.loads('a = 3 * 2')
    assert result['tree']['1']['name'] == ['a']
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['args'][0]['$OBJECT'] == 'expression'
    assert result['tree']['1']['args'][0]['expression'] == 'multiplication'
    assert result['tree']['1']['args'][0]['values'] == [3, 2]


def test_assignments_service():
    """
    Ensures that service assignments are compiled correctly
    """
    result = Api.loads('a = alpine echo')
    assert result['tree']['1']['method'] == 'execute'
    assert result['tree']['1']['name'] == ['a']


def test_assignments_inline_expression():
    result = Api.loads('a = (alpine echo)')
    entry = result['entrypoint']
    path = result['tree'][entry]['name']
    assert result['tree']['1']['args'] == [{'$OBJECT': 'path', 'paths': path}]


def test_assignments_mutation():
    """
    Ensures that assigning a mutation on a value is compiled correctly
    """
    result = Api.loads('0 increase by:1')
    assert result['services'] == []
    assert result['tree']['1']['method'] == 'mutation'
    assert result['tree']['1']['args'][1]['$OBJECT'] == 'mutation'


def test_assignments_mutation_variable():
    """
    Ensures that applying a mutation on a variable is not compiled as a
    service
    """
    result = Api.loads('a = 0\na increase by:1')
    assert result['services'] == []
    assert result['tree']['2']['method'] == 'mutation'
    assert result['tree']['2']['args'][1]['$OBJECT'] == 'mutation'


def test_assignments_string_escape_single():
    """
    Ensures that assignments to strings with escaping are compiled correctly
    """
    result = Api.loads('a = \'b.\\n.\\\\.\\\'.c\'')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    expected = [{'$OBJECT': 'string', 'string': 'b.\n.\\.\'.c'}]
    assert result['tree']['1']['args'] == expected


def test_assignments_string_escape_double():
    """
    Ensures that assignments to strings with escaping are compiled correctly
    """
    result = Api.loads(r'a = "b.\n.\\.\".c"')
    assert result['tree']['1']['method'] == 'expression'
    assert result['tree']['1']['name'] == ['a']
    expected = [{'$OBJECT': 'string', 'string': 'b.\n.\\.".c'}]
    assert result['tree']['1']['args'] == expected
