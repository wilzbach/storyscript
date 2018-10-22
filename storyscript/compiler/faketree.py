# -*- coding: utf-8 -*-
import random
import uuid

from lark.lexer import Token

from ..parser import Tree


class FakeTree:
    """
    Creates fake trees that are not in the original story source.
    """
    def __init__(self, block):
        self.block = block
        self.original_line = block.line()
        self.new_lines = []

    def line(self):
        """
        Creates fake line numbers. The numbers are decreasing, so that the
        resulting tree is compiled correctly.
        """
        lower_bound = int(self.original_line) - 1
        upper_bound = int(self.original_line)
        if len(self.new_lines) > 0:
            upper_bound = self.new_lines[-1]
        fake_line = random.uniform(lower_bound, upper_bound)
        self.new_lines.append(fake_line)
        return str(fake_line)

    @staticmethod
    def path(line):
        """
        Creates a fake tree path.
        """
        path = '${}'.format(uuid.uuid4().hex[:8])
        return Tree('path', [Token('NAME', path, line=line)])

    def expression(self, lhs, operator, rhs):
        """
        Creates a fake expression, equivalent to "lhs + rhs"
        """
        lhs.child(0).child(0).line = self.line()
        fragment = Tree('expression_fragment', [operator, rhs])
        return Tree('expression', [lhs, fragment])

    def assignment(self, value):
        """
        Creates a fake assignment tree, equivalent to "$fake = value"
        """
        fake_line = self.line()
        value.child(0).child(0).line = fake_line
        path = self.path(fake_line)
        fragment = Tree('assignment_fragment', [Token('EQUALS', '='), value])
        return Tree('assignment', [path, fragment])

    def add_assignment(self, value):
        """
        Creates an assignments and adds it to the current block
        """
        assignment = self.assignment(value)
        self.block.insert(assignment)
        return assignment
