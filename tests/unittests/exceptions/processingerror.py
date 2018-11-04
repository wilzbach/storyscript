# -*- coding: utf-8 -*-
from storyscript.exceptions import ProcessingError


def test_processingerror_init():
    error = ProcessingError('error')
    assert error.error == 'error'
    assert error.line is None
    assert error.column is None
    assert issubclass(ProcessingError, Exception)


def test_processingerror_init_line():
    error = ProcessingError('error', line=1)
    assert error.line == 1


def test_processingerror_init_column():
    error = ProcessingError('error', column=1)
    assert error.column == 1
