# -*- coding: utf-8 -*-
from storyscript.parser.Indenter import CustomIndenter, Indenter


def test_indenter():
    assert issubclass(CustomIndenter, Indenter)
    assert CustomIndenter.NL_type == '_NL'
    assert CustomIndenter.OPEN_PAREN_types == []
    assert CustomIndenter.CLOSE_PAREN_types == []
    assert CustomIndenter.INDENT_type == '_INDENT'
    assert CustomIndenter.DEDENT_type == '_DEDENT'
    assert CustomIndenter.tab_len == 8
