import pytest

from tests.parse import parse


@pytest.mark.parametrize('quotes', ['"""', "'''"])
def test_long_string(quotes):
    story = """phrase = %s
        The {{quick}} "{{brown}}" fox 'jumps' '{{over}}' the "lazy" dog
    %s""" % (quotes, quotes)
    result = parse(story).json()
    assert result['script']['1']['method'] == 'set'
    assert result['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['phrase']},
        {
            '$OBJECT': 'string',
            'string': 'The {} "{}" fox \'jumps\' \'{}\' the "lazy" dog',
            'values': [
                {'$OBJECT': 'path', 'paths': ['quick']},
                {'$OBJECT': 'path', 'paths': ['brown']},
                {'$OBJECT': 'path', 'paths': ['over']}
            ]
        }
    ], story
