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
        lower_bound = float(self.original_line) - 1.0
        upper_bound = float(self.original_line)
        if len(self.new_lines) > 0:
            lower_bound = self.new_lines[-1]
        fake_line = random.uniform(lower_bound, upper_bound)
        self.new_lines.append(fake_line)
        return str(fake_line)

    def get_line(self, tree):
        """
        Gets the tree line if it's a new one, otherwise creates it.
        """
        if float(tree.line()) in self.new_lines:
            return tree.line()
        return self.line()

    def path(self, name=None, line=None):
        """
        Creates a fake tree path.
        """
        if name is None:
            name = '${}'.format(uuid.uuid4().hex[:8])
        if line is None:
            line = self.line()
        return Tree('path', [Token('NAME', name, line=line)])

    def assignment(self, value):
        """
        Creates a fake assignment tree, equivalent to "$fake = value"
        """
        line = self.get_line(value)
        value.child(0).child(0).line = line
        path = self.path(line=line)
        equals = Token('EQUALS', '=', line=line)
        fragment = Tree('assignment_fragment', [equals, value])
        return Tree('assignment', [path, fragment])

    def add_assignment(self, value):
        """
        Creates an assignments and adds it to the current block
        """
        assignment = self.assignment(value)
        self.block.insert(assignment)
        return assignment
