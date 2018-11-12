# -*- coding: utf-8 -*-
from storyscript.exceptions import ProcessingError, StorySyntaxError


def test_storysyntaxerror():
    assert issubclass(StorySyntaxError, ProcessingError)
