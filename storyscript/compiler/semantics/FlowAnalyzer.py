# -*- coding: utf-8 -*-
from contextlib import contextmanager

from .Visitors import FullVisitor


class FlowAnalyzer(FullVisitor):
    """
    Checks break and continue statements are inside of a looping construct
    """

    ignore_nodes = [
        "assignment",
        "absolute_expression",
        "concise_when_block",
    ]

    def __init__(self, **kwargs):
        super().__init__(ignore_nodes=self.ignore_nodes, **kwargs)
        self.inside_loop = 0
        self.inside_function = 0
        self.inside_when = 0

    def foreach_block(self, tree):
        with self.with_loop():
            self.visit_children(tree)

    def while_block(self, tree):
        with self.with_loop():
            self.visit_children(tree)

    def function_block(self, tree):
        with self.with_function():
            self.visit_children(tree)

    def when_block(self, tree):
        with self.with_when():
            self.visit_children(tree)

    def break_statement(self, tree):
        tree.expect(self.inside_loop > 0, "break_outside")

    def continue_statement(self, tree):
        tree.expect(self.inside_loop > 0, "continue_outside")

    def return_statement(self, tree):
        tree.expect(
            self.inside_function > 0 or self.inside_when > 0, "return_outside"
        )

    @contextmanager
    def with_loop(self):
        self.inside_loop += 1
        yield
        self.inside_loop -= 1

    @contextmanager
    def with_function(self):
        self.inside_function += 1
        yield
        self.inside_function -= 1

    @contextmanager
    def with_when(self):
        self.inside_when += 1
        yield
        self.inside_when -= 1
