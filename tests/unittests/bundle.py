# -*- coding: utf-8 -*-
import os

from pytest import fixture

from storyscript.bundle import Bundle


@fixture
def bundle():
    return Bundle('path')


def test_bundle_init(bundle):
    assert bundle.path == 'path'


def test_bundle_find_stories(patch, bundle):
    """
    Ensures Bundle.find_stories returns the original path if it's not a
    directory
    """
    patch.object(os.path, 'isdir', return_value=False)
    bundle.find_stories()
    assert bundle.files == ['path']


def test_bundle_find_stories_directory(patch, bundle):
    """
    Ensures Bundle.find_stories returns stories in a directory
    """
    patch.object(os.path, 'isdir')
    patch.object(os, 'walk', return_value=[('root', [], ['one.story', 'two'])])
    bundle.find_stories()
    assert bundle.files == ['root/one.story']


def test_bundle_services(bundle):
    bundle.stories = {'a': {'services': ['one']}, 'b': {'services': ['two']}}
    result = bundle.services()
    assert result == ['one', 'two']


def test_bundle_services_no_duplicates(bundle):
    bundle.stories = {'a': {'services': ['one']}, 'b': {'services': ['one']}}
    result = bundle.services()
    assert result == ['one']


