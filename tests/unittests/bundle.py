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
    patch.many(Bundle, ['find_stories', 'services', 'compile'])
    result = bundle.bundle()
    Bundle.compile.assert_called_with(Bundle.find_stories(), None, False)
    assert result == {'stories': bundle.stories, 'services': Bundle.services()}


def test_bundle_bundle_ebnf_file(patch, bundle):
    patch.many(Bundle, ['find_stories', 'services', 'compile'])
    bundle.bundle(ebnf_file='ebnf')
    Bundle.compile.assert_called_with(Bundle.find_stories(), 'ebnf', False)


def test_bundle_bundle_debug(patch, bundle):
    patch.many(Bundle, ['find_stories', 'services', 'compile'])
    bundle.bundle(debug=True)
    Bundle.compile.assert_called_with(Bundle.find_stories(), None, True)
