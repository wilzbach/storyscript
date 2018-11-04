# -*- coding: utf-8 -*-
from storyscript.exceptions import ProcessingError, StorySyntaxError


def test_storysyntaxerror():
    assert issubclass(StorySyntaxError, ProcessingError)


def test_storysyntaxerror_set_position():
    error = StorySyntaxError('error')
    error.set_position(1, 2)
    assert error.line == 1
    assert error.column == 2
