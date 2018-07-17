# -*- coding: utf-8 -*-
import os

from pytest import fixture

from storyscript.bundle import Bundle
from storyscript.story import Story


@fixture
def bundle():
    return Bundle('path')


def test_bundle_init(bundle):
    assert bundle.path == 'path'
    assert bundle.stories == {}


def test_bundle_find_stories(patch, bundle):
    """
    Ensures Bundle.find_stories returns the original path if it's not a
    directory
    """
    patch.object(os.path, 'isdir', return_value=False)
    assert bundle.find_stories() == ['path']


def test_bundle_find_stories_directory(patch, bundle):
    """
    Ensures Bundle.find_stories returns stories in a directory
    """
    patch.object(os.path, 'isdir')
    patch.object(os, 'walk', return_value=[('root', [], ['one.story', 'two'])])
    assert bundle.find_stories() == ['root/one.story']


def test_bundle_services(bundle):
    bundle.stories = {'a': {'services': ['one']}, 'b': {'services': ['two']}}
    result = bundle.services()
    assert result == ['one', 'two']


def test_bundle_services_no_duplicates(bundle):
    bundle.stories = {'a': {'services': ['one']}, 'b': {'services': ['one']}}
    result = bundle.services()
    assert result == ['one']


def test_bundle_bundle(patch, bundle):
    patch.object(Story, 'from_file')
    patch.many(Bundle, ['find_stories', 'services'])
    Bundle.find_stories.return_value = ['one.story']
    result = bundle.bundle()
    Bundle.find_stories.call_count = 1
    Story.from_file.assert_called_with('one.story')
    Story.from_file().process.assert_called_with(ebnf_file=None, debug=False)
    assert result == {'stories': {'one.story': Story.from_file().process()},
                      'services': Bundle.services()}


def test_bundle_bundle_ebnf_file(patch, bundle):
    patch.object(Story, 'from_file')
    patch.many(Bundle, ['find_stories', 'services'])
    Bundle.find_stories.return_value = ['one.story']
    bundle.bundle(ebnf_file='ebnf')
    Story.from_file().process.assert_called_with(ebnf_file='ebnf', debug=False)


def test_bundle_bundle_debug(patch, bundle):
    patch.object(Story, 'from_file')
    patch.many(Bundle, ['find_stories', 'services'])
    Bundle.find_stories.return_value = ['one.story']
    bundle.bundle(debug=True)
    Story.from_file().process.assert_called_with(ebnf_file=None, debug=True)
