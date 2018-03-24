import pytest

from tests.parse import parse


@pytest.mark.parametrize('eq', ('set ab to ', 'ab =', 'ab= ', 'ab is '))
def test_object_equate(eq):
    story = ''.join((eq, '{"c": d}'))
    result = parse(story).json()
    assert result['script']['1']['method'] == 'set'
    assert result['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['ab']},
        {
            '$OBJECT': 'dict',
            'items': [
                [
                    {'$OBJECT': 'string', 'string': 'c'},
                    {'$OBJECT': 'path', 'paths': ['d']},
                ]
            ]
        }
    ], story


@pytest.mark.parametrize('eq,res', (
    ('"s"', {'$OBJECT': 'string', 'string': 's'}),
    ('1', 1),
    ('p', {'$OBJECT': 'path', 'paths': ['p']}),
))
def test_object_variables(eq, res):
    story = 'ab = {"c": %s}' % eq
    result = parse(story).json()
    assert result['script']['1']['method'] == 'set'
    assert result['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['ab']},
        {
            '$OBJECT': 'dict',
            'items': [
                [
                    {'$OBJECT': 'string', 'string': 'c'},
                    res,
                ]
            ]
        }
    ], story


def test_long_obj():
    story = """foo.bar = {
        'a': 'b',
        'c': 'd'
    }
    """
    result = parse(story).json()
    assert result['script']['1']['method'] == 'set'
    assert result['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['foo', 'bar']},
        {
            '$OBJECT': 'dict',
            'items': [
                [{'$OBJECT': 'string', 'string': 'a'}, {'$OBJECT': 'string', 'string': 'b'}],
                [{'$OBJECT': 'string', 'string': 'c'}, {'$OBJECT': 'string', 'string': 'd'}]
            ]
        }
    ], story
