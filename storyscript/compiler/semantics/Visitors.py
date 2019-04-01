# -*- coding: utf-8 -*-

from storyscript.parser import Tree


class SelectiveVisitor:
    """
    A selective visitor which only visits defined nodes.
    visit_children must be called explicitly.
    """
    def visit(self, tree):
        if hasattr(self, tree.data):
            return getattr(self, tree.data)(tree)

    def visit_children(self, tree):
        for c in tree.children:
            if isinstance(c, Tree):
                self.visit(c)
