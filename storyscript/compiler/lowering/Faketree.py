# -*- coding: utf-8 -*-
from lark.lexer import Token

from storyscript.parser import Tree


class FakeTree:
    # unique prefix for all compiler-inserted paths
    prefix = '__p-'

    """
    Creates fake trees that are not in the original story source.
    """
    def __init__(self, block):
        self.block = block
        self.original_line = str(block.line())
        self.new_lines = {}
        self._check_existing_fake_lines(block)

    def _check_existing_fake_lines(self, block):
        for child in block.children:
            if child.path:
                tok = child.path.find_first_token()
                if isinstance(tok.line, str) and '.' in tok.line:
                    self.new_lines[tok.value] = False

    def line(self):
        """
        Creates fake line numbers. The strings are decreasingly sorted,
        so that the resulting tree is compiled correctly.
        """
        line = self.original_line
        parts = line.split('.')
        if len(parts) > 1:
            line = '.'.join(parts[:-1])
        # We start at .1, s.t. lines from L1 are called L1.1 and not L1.0
        # to avoid any potential confusion
        new_suffix = len(self.new_lines) + 1
        fake_line = f'{line}.{new_suffix}'
        self.new_lines[fake_line] = None
        return fake_line

    def get_line(self, tree):
        """
        Gets the tree line if it's a new one, otherwise creates it.
        """
        if tree.line() in self.new_lines:
            return tree.line()
        return self.line()

    def path(self, name=None, line=None):
        """
        Creates a fake tree path.
        """
        if line is None:
            line = self.line()
        if name is None:
            name = f'{self.prefix}{line}'
        return Tree('path', [Token('NAME', name, line=line)])

    def mark_line(self, node, line):
        """
        Updates the line for all tokens of a given `node`.
        """
        for child in node.children:
            if isinstance(child, Token):
                child.line = line
            else:
                self.mark_line(child, line)

    def set_line(self, node, line):
        """
        Sets the given `line` on the first token in node's subtree or
        on the node itself if its subtree doesn't contain tokens.
        """
        assert isinstance(node, Tree)
        first_token = node.find_first_token()
        if first_token is not None:
            first_token.line = line
        else:
            node._line = line

    def assignment(self, value):
        """
        Creates a fake assignment tree, equivalent to "$fake = value"
        """
        line = self.get_line(value)
        self.set_line(value, line)
        path = self.path(line=line)
        return self.assignment_path(path, value, line)

    def assignment_path(self, path, value, line, eq_tok=None):
        """
        Adds a new assignment: `path` = `value`
        """
        # updates all tokens
        self.mark_line(value, line)
        equals = Token('EQUALS', '=', line=line)
        if eq_tok:
            # We accept and use the equals token from original expression
            # to copy over the token meta data which helps with error messages.
            equals.column = eq_tok.column
            equals.end_column = eq_tok.end_column
        if value.data == 'base_expression':
            expr = value
        else:
            expr = Tree('base_expression', [value])
        fragment = Tree('assignment_fragment', [equals, expr])
        return Tree('assignment', [path, fragment])

    def find_insert_pos(self, original_line):
        """
        Finds the insert position for a targeted line in the fake tree block.
        """
        for i, n in enumerate(self.block.children):
            line = n.line()
            if line == original_line:
                return i
        # use the last position as insert position by default
        # this inserts the new assignment node _before_ the last node
        return -1

    def insert_node(self, node, line):
        """
        Adds a node to the current block at the target line position
        """
        insert_pos = self.find_insert_pos(line)
        self.block.children = [
            *self.block.children[:insert_pos],
            node,
            *self.block.children[insert_pos:],
        ]

    def add_assignment(self, value, original_line):
        """
        Creates an assignments and adds it to the current block
        Returns a fake path reference to this assignment
        """
        assert len(self.block.children) >= 1

        assignment = self.assignment(value)

        self.insert_node(assignment, original_line)

        # we need a new node, s.t. already inserted
        # fake nodes don't get changed
        path_tok = assignment.path.child(0)
        name = Tree.create_token_from_tok(path_tok, 'NAME', path_tok.value)
        name.line = original_line
        return Tree('path', [name])
