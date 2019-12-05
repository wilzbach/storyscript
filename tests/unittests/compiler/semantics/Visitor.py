# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.compiler.semantics.Visitors import SelectiveVisitor
from storyscript.parser import Tree


def test_a_selective_visitor():
    """
    Tests a selective visitor with a simple example visitor.
    """

    class TestVisitor(SelectiveVisitor):
        def __init__(self):
            self._node = 0

        def node(self, tree):
            self._node = self._node + 1
            self.visit_children(tree)

    tree = Tree(
        "node", [Tree("node", []), Token("TOK", 42), Tree("unknown", [])]
    )
    visitor = TestVisitor()
    visitor.visit(tree)
    assert visitor._node == 2
