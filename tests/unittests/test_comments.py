from pytest import mark

from tests.parse import parse


def test_single():
    story = parse(
        '# hello world\n'
        'container arg1'
    ).json()
    assert story['script']['2']['method'] == 'run'
    assert story['script']['2']['container'] == 'container'


def test_block():
    story = parse(
        '### hello world\n'
        'still commenting\n'
        '###\n'
        'container arg1'
    ).json()
    assert story['script']['4']['method'] == 'run'
    assert story['script']['4']['container'] == 'container'
