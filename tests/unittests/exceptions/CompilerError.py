# -*- coding: utf-8 -*-
from storyscript.exceptions import CompilerError, ProcessingError


def test_compilererror():
    assert issubclass(CompilerError, ProcessingError)
