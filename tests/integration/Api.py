# -*- coding: utf-8 -*-
from unittest.mock import patch

from pytest import raises

from storyscript.Api import Api
from storyscript.Bundle import Bundle
from storyscript.Story import Story
from storyscript.exceptions import StoryError


def test_api_load_map_compiling_try_block():
    """
    Ensures Api.load functions return errors
    """
    files = {'asd': 'foo ='}
    with raises(StoryError) as e:
        Api.load_map(files).check_success()
    assert e.value.short_message() == 'E0007: Missing value after `=`'


def test_api_load_map_compiling_try_block_loads():
    """
    Ensures Api.load functions return errors
    """
    s = Api.loads('foo =')
    assert len(s.deprecations()) == 0
    assert len(s.warnings()) == 0
    e = s.errors()[0]
    assert e.short_message() == 'E0007: Missing value after `=`'
    e.with_color = False
    assert e.message() == \
        """Error: syntax error in story at line 1, column 6

1|    foo =
           ^

E0007: Missing value after `=`"""


def test_api_load_map_syntax_error():
    """
    Ensures Api.load functions return errors
    """
    files = {'asd': 'foo ='}
    s = Api.load_map(files)
    e = s.errors()[0]
    assert e.short_message() == 'E0007: Missing value after `=`'
    e.with_color = False
    assert e.message() == \
        """Error: syntax error in story at line 1, column 6

1|    foo =
           ^

E0007: Missing value after `=`"""


def test_api_load_map_ice():
    """
    Simulate an ICE during load_map
    """
    with patch.object(Bundle, 'bundle') as p:
        p.side_effect = Exception('ICE')
        s = Api.load_map({})
        e = s.errors()[0]
        assert e.message() == \
            """E0001: Internal error occured: ICE
Please report at https://github.com/storyscript/storyscript/issues"""


def test_api_loads_ice():
    """
    Simulate an ICE during loads
    """
    with patch.object(Story, 'process') as p:
        p.side_effect = Exception('ICE')
        with raises(StoryError) as e:
            Api.loads('foo').check_success()
        assert e.value.message() == \
            """E0001: Internal error occured: ICE
Please report at https://github.com/storyscript/storyscript/issues"""


def test_api_load_ice():
    """
    Simulate an ICE during load
    """
    with patch.object(Story, 'from_stream') as p:
        p.side_effect = Exception('ICE')
        s = Api.load('foo')
        e = s.errors()[0]
        assert e.message() == \
            """E0001: Internal error occured: ICE
Please report at https://github.com/storyscript/storyscript/issues"""


def test_compiler_only_comments():
    api_result = Api.load_map({'a.story': '# foo\n'}).result()
    result = api_result['stories']['a.story']
    assert result['tree'] == {}
    assert result['entrypoint'] is None
