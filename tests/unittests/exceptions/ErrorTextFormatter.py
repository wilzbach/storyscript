# -*- coding: utf-8 -*-
from pytest import raises

from storyscript.exceptions.ErrorTextFormatter import ErrorTextFormatter


def test_error_text_formatter():
    formatter = ErrorTextFormatter(None, None)

    with raises(NotImplementedError):
        formatter.process()

    with raises(NotImplementedError):
        formatter.hint()
