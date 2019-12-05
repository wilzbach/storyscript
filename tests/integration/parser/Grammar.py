# -*- coding: utf-8 -*-
import io
from os import path

from storyscript.parser.Grammar import Grammar

grammar_file = path.join(path.dirname(__file__), "grammar.lark")


def test_grammar():
    """
    Integration test for Lark Grammar file. If you changed the grammar, you
    most likely will need to update it:
    ```
    storyscript grammar > tests/integration/parser/grammar.lark
    ```
    """
    result = Grammar().build().strip()
    expected = None
    with io.open(grammar_file, "r") as f:
        expected = f.read().strip()
    assert result == expected
