import pytest

from tests.parse import parse


def test_if_else():
    """
    if x
      pass
    else
      pass
    """
    story = parse(
        test_if_else.__doc__.strip().replace('\n    ', '\n')
    ).json()
    assert story['script']['1']['method'] == 'if'
    assert story['script']['1']['enter'] == '2'
    assert story['script']['1']['exit'] == '4'
    assert story['script']['3']['method'] == 'else'


def test_if_elif():
    """
    if x
      pass
    else if y
      pass
    """
    story = parse(
        test_if_elif.__doc__.strip().replace('\n    ', '\n')
    ).json()
    assert story['script']['1']['method'] == 'if'
    assert story['script']['1']['enter'] == '2'
    assert story['script']['1']['exit'] == '3'

    assert story['script']['3']['method'] == 'elif'
    assert story['script']['3']['enter'] == '4'
    assert story['script']['3']['exit'] is None


def test_if_elif_elif():
    """
    if x
      pass
    elseif y
      pass
    elif z
      pass
    """
    story = parse(
        test_if_elif_elif.__doc__.strip().replace('\n    ', '\n')
    ).json()
    assert story['script']['1']['method'] == 'if'
    assert story['script']['1']['enter'] == '2'
    assert story['script']['1']['exit'] == '3'

    assert story['script']['3']['method'] == 'elif'
    assert story['script']['3']['enter'] == '4'
    assert story['script']['3']['exit'] == '5'

    assert story['script']['5']['method'] == 'elif'
    assert story['script']['5']['enter'] == '6'
    assert story['script']['5']['exit'] is None


def test_if_elif_elif_else():
    """
    if x
      pass
    else if y
      pass
    else if z
      pass
    else
      pass
    """
    story = parse(
        test_if_elif_elif_else.__doc__.strip().replace('\n    ', '\n')
    ).json()
    assert story['script']['1']['method'] == 'if'
    assert story['script']['1']['enter'] == '2'
    assert story['script']['1']['exit'] == '3'

    assert story['script']['3']['method'] == 'elif'
    assert story['script']['3']['enter'] == '4'
    print(story['script']['3'])
    assert story['script']['3']['exit'] == '5'

    assert story['script']['5']['method'] == 'elif'
    assert story['script']['5']['enter'] == '6'
    assert story['script']['5']['exit'] == '8'

    assert story['script']['7']['method'] == 'else'
