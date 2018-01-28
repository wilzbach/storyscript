from pytest import mark

from tests.parse import parse


@mark.parametrize('conj',
                  ['the', 'a', 'an']
                  )
def test_conj(conj):
    """Hello {} world"""
    story = parse(test_conj.__doc__.format(conj)).json()
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'Hello'
    assert story['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['world']}
    ]
