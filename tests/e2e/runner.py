# -*- coding: utf-8 -*-

import io
import json
from glob import glob
from os import path

from pytest import mark

from storyscript.compiler import Compiler
from storyscript.parser import Parser

test_dir = path.dirname(path.realpath(__file__))
# make the test_file paths relative, s.t. the tests are nice to read
test_files = list(map(lambda e: path.relpath(e, test_dir),
                  glob(path.join(test_dir, '*.story'))))


# compile a story and compare its tree with the expected tree
def run_test_story(source, expected_story):
    result = Compiler.compile(Parser().parse(source))
    del result['version']
    del expected_story['version']
    assert result == expected_story


# load a story from the file system and load its expected result file (.json)
def run_test(story_path):
    story_string = None
    expected_story = None
    with io.open(story_path, 'r') as f:
        story_string = f.read()

    expected_path = path.splitext(story_path)[0] + '.json'
    with io.open(expected_path, 'r') as f:
        expected_story = f.read()

    # deserialize the expected story
    expected_story = json.loads(expected_story)

    # take the first story (at the moment only the runner supports single
    # StoryScript files)
    expected_story = next(iter(expected_story['stories'].values()))

    run_test_story(story_string, expected_story)


@mark.parametrize('test_file', test_files)
def test_story(test_file):
    test_file = path.join(test_dir, test_file)
    run_test(test_file)
