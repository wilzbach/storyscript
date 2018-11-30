# -*- coding: utf-8 -*-
import os

import delegator

from pytest import fixture

from storyscript.Bundle import Bundle
from storyscript.Story import Story


@fixture
def bundle(patch):
    patch.object(Story, 'read')
    return Bundle.from_path('path')


def test_bundle_init(bundle):
    assert 'path' in bundle.story_files
    assert bundle.stories == {}


def test_bundle_gitignores(patch, bundle):
    """
    Ensures gitignores uses can produce the list of ignored files.
    """
    patch.object(delegator, 'run')
    result = bundle.gitignores()
    command = 'git ls-files --others --ignored --exclude-standard'
    delegator.run.assert_called_with(command)
    delegator.run().out.split.assert_called_with('\n')
    assert result == delegator.run().out.split()


def test_bundle_parse_directory(patch, bundle):
    """
    Ensures parse_directory can parse a directory
    """
    patch.object(os, 'walk', return_value=[('root', [], ['one.story', 'two'])])
    patch.object(Bundle, 'gitignores')
    result = bundle.parse_directory('dir')
    assert Bundle.gitignores.call_count == 1
    os.walk.assert_called_with('dir')
    assert result == ['root/one.story']


def test_bundle_parse_directory_ignored(patch, bundle):
    """
    Ensures parse_directory does not return ignored files
    """
    patch.object(os, 'walk', return_value=[('./root', [], ['one.story'])])
    patch.object(Bundle, 'gitignores', return_value=['root/one.story'])
    result = bundle.parse_directory('dir')
    assert result == []


def test_bundle_find_stories(patch, bundle):
    """
    Ensures Bundle.find_stories returns the original path if it's not a
    directory
    """
    patch.object(os.path, 'isdir', return_value=False)
    assert bundle.find_stories() == ['path']


def test_bundle_find_stories_directory(patch):
    """
    Ensures Bundle.find_stories uses Bundle.parse_directory
    """
    patch.object(Story, 'read')
    patch.object(Bundle, 'parse_directory')
    patch.object(os.path, 'isdir')
    os.path.isdir.return_value = True
    path = 'path'
    bundle = Bundle.from_path(path)
    result = bundle.find_stories()
    Bundle.parse_directory.assert_called_with(path)
    assert result == []


def test_bundle_services(bundle):
    bundle.stories = {'a': {'services': ['one']}, 'b': {'services': ['two']}}
    result = bundle.services()
    assert result == ['one', 'two']


def test_bundle_services_no_duplicates(bundle):
    bundle.stories = {'a': {'services': ['one']}, 'b': {'services': ['one']}}
    result = bundle.services()
    assert result == ['one']


def test_bundle_compile_modules(patch, bundle):
    patch.object(Bundle, 'compile')
    bundle.compile_modules(['stories'], 'ebnf', 'debug')
    Bundle.compile.assert_called_with(['stories'], 'ebnf', 'debug')


def test_bundle_parse_modules(patch, bundle):
    patch.object(Bundle, 'parse')
    bundle.parse_modules(['stories'], 'ebnf', 'debug')
    Bundle.parse.assert_called_with(['stories'], 'ebnf', 'debug')


def test_bundle_parse(patch, bundle):
    patch.many(Bundle, ['parse_modules', 'load_story'])
    bundle.parse(['one.story'], None, False)
    Bundle.load_story.assert_called_with('one.story')
    story = Bundle.load_story()
    Bundle.parse_modules.assert_called_with(story.modules(), None, False)
    assert bundle.stories['one.story'] == story.tree


def test_bundle_compile(mocker, patch, bundle):
    patch.many(Bundle, ['compile_modules', 'load_story'])
    patch.many(Story, ['parse'])

    bundle.compile(['one.story'], None, False)
    Bundle.load_story.assert_called_with('one.story')

    story = Bundle.load_story()
    Bundle.compile_modules.assert_called_with(story.modules(), None, False)
    story.compile.assert_called_with(debug=False)
    assert bundle.stories['one.story'] == story.compiled


def test_bundle_bundle(patch, bundle):
    patch.many(Bundle, ['find_stories', 'services', 'compile'])
    result = bundle.bundle()
    Bundle.compile.assert_called_with(Bundle.find_stories(), None, False)
    expected = {'stories': bundle.stories, 'services': Bundle.services(),
                'entrypoint': Bundle.find_stories()}
    assert result == expected


def test_bundle_bundle_ebnf(patch, bundle):
    patch.many(Bundle, ['find_stories', 'services', 'compile'])
    bundle.bundle(ebnf='ebnf')
    Bundle.compile.assert_called_with(Bundle.find_stories(), 'ebnf', False)


def test_bundle_bundle_debug(patch, bundle):
    patch.many(Bundle, ['find_stories', 'services', 'compile'])
    bundle.bundle(debug=True)
    Bundle.compile.assert_called_with(Bundle.find_stories(), None, True)


def test_bundle_bundle_trees(patch, bundle):
    patch.many(Bundle, ['find_stories', 'parse'])
    result = bundle.bundle_trees()
    Bundle.parse.assert_called_with(Bundle.find_stories(), None, None)
    assert result == bundle.stories


def test_bundle_bundle_trees_ebnf(patch, bundle):
    patch.many(Bundle, ['find_stories', 'parse'])
    bundle.bundle_trees(ebnf='ebnf')
    Bundle.parse.assert_called_with(Bundle.find_stories(), 'ebnf', None)


def test_bundle_bundle_trees_debug(patch, bundle):
    patch.many(Bundle, ['find_stories', 'parse'])
    bundle.bundle_trees(debug=True)
    Bundle.parse.assert_called_with(Bundle.find_stories(), None, True)


def test_bundle_lex(patch, bundle):
    """
    Ensures Bundle.lex can lex a bundle
    """
    patch.object(Story, 'from_file')
    patch.object(Bundle, 'find_stories', return_value=['story'])
    result = bundle.lex()
    Story.from_file.assert_called_with('story')
    Story.from_file().lex.assert_called_with(ebnf=None)
    assert result['story'] == Story.from_file().lex()


def test_bundle_lex_ebnf(patch, bundle):
    """
    Ensures Bundle.lex supports specifying an ebnf file
    """
    patch.object(Story, 'from_file')
    patch.object(Bundle, 'find_stories', return_value=['story'])
    bundle.lex(ebnf='ebnf')
    Story.from_file().lex.assert_called_with(ebnf='ebnf')


def test_bundle_load_story_twice(patch, bundle):
    patch.object(Story, 'read')
    mocked_file = 'x = 2'
    Story.read.return_value = mocked_file

    story = bundle.load_story('one.story')
    Story.read.assert_called_with('one.story')

    # don't reread the story
    Story.read.reset_mock()
    assert bundle.load_story('one.story').story == story.story
    Story.read.assert_not_called()
