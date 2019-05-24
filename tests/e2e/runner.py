# -*- coding: utf-8 -*-

import io
import json
from glob import glob
from os import path

from click import unstyle

from pytest import mark

from storyscript.Api import Api
from storyscript.App import _clean_dict

from utils import parse_features

test_dir = path.dirname(path.realpath(__file__))
# make the test_file paths relative, s.t. test paths are nice to read
test_files = list(map(lambda e: path.relpath(e, test_dir),
                  glob(path.join(test_dir, '**', '*.story'), recursive=True)))

features = {'globals': True}


# compile a story and compare its tree with the expected tree
def run_test_story(source, expected_story, features):
    s = Api.loads(source, features)
    s.check_success()
    result = _clean_dict(s.result())
    del result['version']
    assert expected_story == result


# compile a story which should fail and compare its output text with the
# expectation
def run_fail_story(source, expected_output, features):
    s = Api.loads(source, features)
    errors = s.errors()
    if len(errors) > 0:
        assert len(errors) == 1, 'Only one error supported for now'
        result = unstyle(errors[0].message())
        assert expected_output == result
        return

    assert 0, 'The story was expected to fail, but did not fail.'


# load a story from the file system and load its expected result file (.json)
def run_test(story_path):
    story_string = None
    with io.open(story_path, 'r') as f:
        story_string = f.read()

    expected_path = path.splitext(story_path)[0]
    parsed_features = parse_features(features, story_string)
    if path.isfile(expected_path + '.json'):
        expected_story = None
        with io.open(expected_path + '.json', 'r') as f:
            expected_story = f.read()

        # deserialize the expected story
        expected_story = json.loads(expected_story)
        return run_test_story(story_string, expected_story, parsed_features)

    if path.isfile(expected_path + '.error'):
        expected_output = None
        with io.open(expected_path + '.error', 'r') as f:
            expected_output = f.read().strip()

        # deserialize the expected story
        return run_fail_story(story_string, expected_output, parsed_features)

    # If no expected file has been found, print the current output to the user
    # (for handy copy&paste)
    e = Api.loads(story_string, features)
    if e.result():
        print(e.result())
    else:
        e.errors()[0].echo()
    assert 0, f'{story_path} has no expected result file.'


@mark.parametrize('test_file', test_files)
def test_story(test_file):
    test_file = path.join(test_dir, test_file)
    run_test(test_file)
