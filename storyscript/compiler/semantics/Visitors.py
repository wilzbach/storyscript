# -*- coding: utf-8 -*-

from storyscript.parser import Tree


class BaseVisitor:
    def __init__(self, function_table, mutation_table, features):
        self.function_table = function_table
        self.mutation_table = mutation_table
        self.features = features


class SelectiveVisitor(BaseVisitor):
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


class ScopeSelectiveVisitor(BaseVisitor):
    """
    A selective visitor which only visits defined nodes.
    visit_children must be called explicitly.
    """
    def visit(self, tree, scope=None):
        if hasattr(self, tree.data):
            return getattr(self, tree.data)(tree, scope)

    def visit_children(self, tree, scope):
        for c in tree.children:
            if isinstance(c, Tree):
                self.visit(c, scope)
