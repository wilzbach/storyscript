# -*- coding: utf-8 -*-
from contextlib import contextmanager

from .Visitors import SelectiveVisitor


class FlowAnalyzer(SelectiveVisitor):
    """
    Checks break and continue statements are inside of a looping construct
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inside_loop = 0
        self.inside_function = 0

    def rules(self, tree):
        self.visit_children(tree)

    def block(self, tree):
        self.visit_children(tree)

    def nested_block(self, tree):
        self.visit_children(tree)

    def when_block(self, tree):
        self.visit_children(tree)

    def service_block(self, tree):
        self.visit_children(tree)

    def if_block(self, tree):
        self.visit_children(tree)

    def elseif_block(self, tree):
        self.visit_children(tree)

    def else_block(self, tree):
        self.visit_children(tree)

    def try_block(self, tree):
        self.visit_children(tree)

    def catch_block(self, tree):
        self.visit_children(tree)

    def finally_block(self, tree):
        self.visit_children(tree)

    def foreach_block(self, tree):
        with self.with_loop():
            self.visit_children(tree)

    def while_block(self, tree):
        with self.with_loop():
            self.visit_children(tree)

    def function_block(self, tree):
        with self.with_function():
            self.visit_children(tree)

    def break_statement(self, tree):
        tree.expect(self.inside_loop > 0, 'break_outside')

    def continue_statement(self, tree):
        tree.expect(self.inside_loop > 0, 'continue_outside')

    def return_statement(self, tree):
        tree.expect(self.inside_function > 0, 'return_outside')

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

    def start(self, tree):
        self.visit_children(tree)
