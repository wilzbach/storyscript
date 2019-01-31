# -*- coding: utf-8 -*-
import os

import click

from lark.exceptions import UnexpectedCharacters, UnexpectedToken

from pytest import fixture, mark

from storyscript.ErrorCodes import ErrorCodes
from storyscript.Intention import Intention
from storyscript.exceptions import CompilerError, StoryError


@fixture
def error(magic):
    return magic()


@fixture
def storyerror(error):
    return StoryError(error, 'story')


def test_storyerror_init(storyerror, error):
    assert storyerror.error == error
    assert storyerror.story == 'story'
    assert storyerror.path is None
    assert storyerror.error_tuple is None
    assert issubclass(StoryError, SyntaxError)


def test_storyerror_init_path():
    storyerror = StoryError('error', 'story', path='hello.story')
    assert storyerror.path == 'hello.story'


def test_storyerror_name(storyerror):
    assert storyerror.name() == 'story'


def test_storyerror_name_path(patch, storyerror):
    patch.object(os, 'getcwd', return_value='/abspath')
    storyerror.path = 'hello.story'
    assert storyerror.name() == 'hello.story'


def test_storyerror_name_reduce_path(patch, storyerror):
    """
    Ensures that paths are simplified for stories in the current working
    directory.
    """
    patch.object(os, 'getcwd', return_value='/abspath')
    storyerror.path = '/abspath/hello.story'
    assert storyerror.name() == 'hello.story'


def test_storyerror_get_line(patch, storyerror, error):
    """
    Ensures get_line returns the error line
    """
    error.line = '1'
    storyerror.story = 'x = 0\ny = 1'
    assert storyerror.get_line() == 'x = 0'


def test_storyerror_header(patch, storyerror, error):
    """
    Ensures StoryError.header returns the correct text.
    """
    patch.object(click, 'style')
    patch.object(StoryError, 'name')
    template = 'Error: syntax error in {} at line {}, column {}'
    result = storyerror.header()
    click.style.assert_called_with(StoryError.name(), bold=True)
    assert result == template.format(click.style(), error.line, error.column)


def test_storyerror_symbols(patch, storyerror, error):
    """
    Ensures StoryError.symbols creates one symbol when there is no end column.
    """
    patch.object(click, 'style')
    del error.end_column
    error.column = '1'
    result = storyerror.symbols()
    click.style.assert_called_with('^', fg='red')
    assert result == click.style()


def test_story_error_symbols_end_column(patch, storyerror, error):
    """
    Ensures StoryError.symbols creates many symbols when there is an end
    column.
    """
    patch.object(click, 'style')
    error.end_column = '4'
    error.column = '1'
    result = storyerror.symbols()
    click.style.assert_called_with('^^^', fg='red')
    assert result == click.style()
    storyerror.with_color = False
    result = storyerror.symbols()
    assert result == '^^^'


def test_storyerror_highlight(patch, storyerror, error):
    """
    Ensures StoryError.highlight produces the correct text.
    """
    patch.many(StoryError, ['get_line', 'symbols'])
    error.column = '1'
    result = storyerror.highlight()
    highlight = '{}{}'.format(' ' * 6, StoryError.symbols())
    args = (error.line, StoryError.get_line(), highlight)
    assert result == '{}|    {}\n{}'.format(*args)


def test_storyerror_error_code(storyerror):
    storyerror.error_tuple = ('code', 'hint')
    assert storyerror.error_code() == 'code'


def test_storyerror_hint(storyerror):
    storyerror.error_tuple = ('code', 'hint')
    assert storyerror.hint() == 'hint'


def test_storyerror_hint_unidentified_error(storyerror):
    storyerror.error_tuple = ErrorCodes.unidentified_error
    storyerror.error = Exception('Custom.Error')
    assert storyerror.hint() == 'Custom.Error'


def test_storyerror_hint_unidentified_compiler_error(storyerror):
    storyerror.error_tuple = ErrorCodes.unidentified_error
    storyerror.error = CompilerError(None, message='Custom.Compiler.Error')
    assert storyerror.hint() == 'Custom.Compiler.Error'


def test_storyerror_hint_invalid_character(patch, storyerror):
    patch.object(storyerror, 'get_line', return_value='x = $')
    storyerror.error = UnexpectedCharacters('seq', 0, line=1, column=5)
    storyerror.error_tuple = ErrorCodes.invalid_character
    assert storyerror.hint() == '`$` is not allowed here'


def test_storyerror_hint_redeclared(patch, storyerror, magic):
    patch.object(storyerror, 'get_line', return_value='foo')
    storyerror.error = UnexpectedCharacters('seq', 0, line=1, column=5)
    storyerror.error = magic()
    storyerror.error.extra.function_name = '.function_name.'
    storyerror.error.extra.previous_line = '.previous.line.'
    storyerror.error_tuple = ErrorCodes.function_already_declared
    assert storyerror.hint() == \
        '`.function_name.` has already been declared at line .previous.line.'


def test_storyerror_hint_unexpected_token(patch, storyerror, ):
    patch.object(storyerror, 'get_line', return_value='if a and b')
    expected = ['a', 'b', 'c']
    storyerror.error = UnexpectedToken(token='and', expected=expected)
    storyerror.error_tuple = ErrorCodes.unexpected_token
    assert storyerror.hint() == ('`and` is not allowed here. '
                                 f'Allowed: {str(expected)}')


def test_storyerror_unexpected_token_code(patch, call_count, storyerror):
    patch.init(Intention)
    patch.object(Intention, 'assignment', return_value=False)
    patch.object(Intention, 'unnecessary_colon', return_value=False)
    result = storyerror.unexpected_token_code()
    Intention.__init__.assert_called_with(storyerror.get_line())
    call_count(Intention, ['assignment', 'unnecessary_colon'])
    assert result == ErrorCodes.unexpected_token


def test_storyerror_unexpected_token_code_assignment(patch, storyerror):
    patch.init(Intention)
    patch.object(Intention, 'assignment')
    result = storyerror.unexpected_token_code()
    assert result == ErrorCodes.assignment_incomplete


def test_storyerror_unexpected_token_code_colon(patch, storyerror):
    patch.init(Intention)
    patch.object(Intention, 'assignment', return_value=False)
    patch.object(Intention, 'unnecessary_colon')
    assert storyerror.unexpected_token_code() == ErrorCodes.unnecessary_colon


def test_storyerror_unexpected_characters_code(patch, call_count, storyerror):
    patch.init(Intention)
    patch.object(Intention, 'is_function', return_value=False)
    patch.object(Intention, 'unnecessary_colon', return_value=False)
    result = storyerror.unexpected_characters_code()
    Intention.__init__.assert_called_with(storyerror.get_line())
    call_count(Intention, ['is_function', 'unnecessary_colon'])
    assert result == ErrorCodes.invalid_character


def test_storyerror_unexpected_characters_code_function(patch, storyerror):
    patch.init(Intention)
    patch.object(Intention, 'is_function')
    result = storyerror.unexpected_characters_code()
    assert result == ErrorCodes.function_misspell


def test_storyerror_unexpected_characters_code_colon(patch, storyerror):
    patch.init(Intention)
    patch.object(Intention, 'is_function', return_value=False)
    patch.object(Intention, 'unnecessary_colon')
    result = storyerror.unexpected_characters_code()
    assert result == ErrorCodes.unnecessary_colon


def test_storyerror_identify(storyerror):
    storyerror.error.error = 'none'
    assert storyerror.identify() == ErrorCodes.unidentified_error


@mark.parametrize('name', [
    'service_name', 'arguments_noservice', 'return_outside',
    'variables_backslash', 'variables_dash'
])
def test_storyerror_identify_codes(storyerror, error, name):
    error.error = name
    assert storyerror.identify() == getattr(ErrorCodes, name)


def test_storyerror_identify_unexpected_token(patch, storyerror):
    """
    Ensures that StoryError.identify can find the error code for unidentified
    token errors
    """
    patch.init(UnexpectedToken)
    patch.object(StoryError, 'unexpected_token_code')
    storyerror.error = UnexpectedToken('seq', 'lex', 0, 0)
    assert storyerror.identify() == storyerror.unexpected_token_code()


def test_storyerror_identify_unexpected_characters(patch, storyerror):
    patch.init(UnexpectedCharacters)
    patch.object(StoryError, 'unexpected_characters_code')
    storyerror.error = UnexpectedCharacters('seq', 'lex', 0, 0)
    assert storyerror.identify() == storyerror.unexpected_characters_code()


def test_storyerror_process(patch, storyerror):
    patch.object(StoryError, 'identify')
    storyerror.process()
    assert storyerror.error_tuple == storyerror.identify()


def test_storyerror_message(patch, storyerror):
    patch.many(StoryError,
               ['process', 'header', 'highlight', 'error_code', 'hint'])
    result = storyerror.message()
    assert storyerror.process.call_count == 1
    args = (storyerror.header(), storyerror.highlight(),
            storyerror.error_code(), storyerror.hint())
    assert result == '{}\n\n{}\n\n{}: {}'.format(*args)


def test_story_storyerror_short_message(patch, storyerror):
    patch.many(StoryError, ['process', 'error_code', 'hint'])
    result = storyerror.short_message()
    assert result == f'{storyerror.error_code()}: {storyerror.hint()}'


def test_storyerror_echo(patch, storyerror):
    """
    Ensures StoryError.echo prints StoryError.message
    """
    patch.object(click, 'echo')
    patch.object(StoryError, 'message')
    storyerror.echo()
    click.echo.assert_called_with(StoryError.message())


def test_storyerror_internal(patch):
    """
    Ensures that an internal error gets properly constructed
    """
    patch.object(StoryError, 'unnamed_error')
    e = StoryError.internal_error(Exception('ICE happened'))
    msg = (
        'Internal error occured: ICE happened\n'
        'Please report at https://github.com/storyscript/storyscript/issues')
    StoryError.unnamed_error.assert_called_with(msg)
    assert e == StoryError.internal_error(msg)


def test_storyerror_unnamed_error(patch):
    patch.init(StoryError)
    patch.init(CompilerError)
    e = StoryError.unnamed_error('Unknown error happened')
    assert isinstance(e, StoryError)
    assert CompilerError.__init__.call_count == 1
    assert isinstance(StoryError.__init__.call_args[0][0], CompilerError)
    assert StoryError.__init__.call_args[0][1] is None
