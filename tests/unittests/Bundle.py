# -*- coding: utf-8 -*-
import os

import delegator

from pytest import fixture

from storyscript.Bundle import Bundle
from storyscript.Story import Story


@fixture
def bundle(patch):
    return Bundle()


def test_bundle_init(bundle):
    assert bundle.stories == {}
    assert bundle.story_files == {}


def test_bundle_init_files():
    bundle = Bundle(story_files={'one.story': 'hello'})
    assert bundle.story_files == {'one.story': 'hello'}


def test_bundle_gitignores(patch):
    """
    Ensures gitignores uses can produce the list of ignored files.
    """
    patch.object(delegator, 'run')
    result = Bundle.gitignores()
    command = 'git ls-files --others --ignored --exclude-standard'
    delegator.run.assert_called_with(command)
    delegator.run().out.split.assert_called_with('\n')
    assert result == delegator.run().out.split()


def test_bundle_ignores(patch):
    patch.object(os.path, 'isdir')
    patch.object(os, 'walk', return_value=[('root', [], ['one.story', 'two'])])
    result = Bundle.ignores('path')
    os.walk.assert_called_with('path')
    assert result == ['root/one.story']


def test_bundle_ignores_not_dir(patch):
    patch.many(os.path, ['relpath', 'isdir'])
    os.path.isdir.return_value = False
    result = Bundle.ignores('path')
    os.path.relpath.assert_called_with('path')
    assert result == [os.path.relpath()]


def test_bundle_filter_path():
    result = Bundle.filter_path('./root', 'one.story', [])
    assert result == './root/one.story'


def test_bundle_filter_path_ignores():
    result = Bundle.filter_path('./root', 'one.story', ['root/one.story'])
    assert result is None


def test_bundle_parse_directory(patch, bundle):
    """
    Ensures parse_directory can parse a directory
    """
    patch.object(os, 'walk', return_value=[('root', [], ['one.story', 'two'])])
    patch.object(Bundle, 'gitignores')
    result = Bundle.parse_directory('dir')
    assert Bundle.gitignores.call_count == 1
    os.walk.assert_called_with('dir')
    assert result == ['root/one.story']


def test_bundle_parse_directory_gitignored(patch, bundle):
    """
    Ensures parse_directory does not return gitignored files
    """
    patch.object(os, 'walk', return_value=[('./root', [], ['one.story'])])
    patch.object(Bundle, 'gitignores')
    Bundle.gitignores.return_value = ['root/one.story']
    assert Bundle.parse_directory('dir') == []


def test_bundle_parse_directory_ignored_path(patch, bundle):
    patch.object(os, 'walk', return_value=[('./root', [], ['one.story'])])
    patch.object(Bundle, 'gitignores', return_value=[])
    assert Bundle.parse_directory('dir', ignored_path='root/one.story') == []


def test_bundle_from_path(patch):
    """
    Ensures Bundle.from_path can create a Bundle from a filepath
    """
    patch.object(os.path, 'isdir', return_value=False)
    patch.init(Bundle)
    patch.object(Bundle, 'load_story')
    result = Bundle.from_path('path')
    Bundle.load_story.assert_called_with('path')
    assert isinstance(result, Bundle)


def test_bundle_from_path_directory(patch):
    """
    Ensures Bundle.from_path can create a Bundle from a directory path
    """
    patch.object(os.path, 'isdir')
    patch.init(Bundle)
    patch.many(Bundle, ['load_story', 'parse_directory'])
    Bundle.parse_directory.return_value = ['one.story']
    Bundle.from_path('path')
    Bundle.parse_directory.assert_called_with('path', ignored_path=None)
    Bundle.load_story.assert_called_with('one.story')


def test_bundle_from_path_directory_ignored(patch):
    """
    Ensures Bundle.from_path accepts an ignored_path keyword argument
    """
    patch.object(os.path, 'isdir')
    patch.init(Bundle)
    patch.many(Bundle, ['load_story', 'parse_directory'])
    Bundle.from_path('path', ignored_path='ignored')
    Bundle.parse_directory.assert_called_with('path', ignored_path='ignored')


def test_bundle_load_story(patch, bundle):
    """
    Ensures Bundle.load_story can load a story
    """
    patch.init(Story)
    bundle.story_files['one.story'] = 'hello'
    result = bundle.load_story('one.story')
    Story.__init__.assert_called_with('hello')
    assert isinstance(result, Story)


def test_bundle_load_story_not_read(patch, bundle):
    """
    Ensures Bundle.load_story reads a story before loading it
    """
    patch.init(Story)
    patch.object(Story, 'read')
    bundle.story_files = {}
    bundle.load_story('one.story')
    Story.read.assert_called_with('one.story')
    assert bundle.story_files['one.story'] == Story.read()


def test_bundle_find_stories(patch, bundle):
    """
    Ensures Bundle.find_stories returns the list of loaded stories
    """
    bundle.story_files = {'one.story': 'hello'}
    assert bundle.find_stories() == ['one.story']


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
