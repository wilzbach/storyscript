from json import dumps

import pytest

from tests.parse import parse


def test_containers():
    """
    owner/repo arg1 arg2
    """
    story = parse(
        test_containers.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'owner/repo'
    assert story['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['arg1']},
        {'$OBJECT': 'path', 'paths': ['arg2']}
    ]


def test_container_comma():
    """
    owner/repo:stable arg1, arg2
    """
    story = parse(
        test_container_comma.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'owner/repo:stable'
    assert story['script']['1']['args'] == [
        {'$OBJECT': 'path', 'paths': ['arg1']},
        {'$OBJECT': 'path', 'paths': ['arg2']}
    ]


def test_containers_long():
    """
    domain.com/owner/repo:latest
    """
    story = parse(
        test_containers_long.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'domain.com/owner/repo:latest'
    assert story['script']['1']['args'] is None


def test_container_suite():
    """
    alpine echo '1'
        alpine echo '2'
    """
    story = parse(
        test_container_suite.__doc__.strip().replace('\n    ', '\n')
    ).json()
    print(dumps(story['script'], indent=2))
    assert story['script']['1']['method'] == 'run'
    assert story['script']['1']['container'] == 'alpine'
    assert story['script']['2']['method'] == 'run'
    assert story['script']['2']['container'] == 'alpine'
    assert story['script']['2']['parent'] == '1'
