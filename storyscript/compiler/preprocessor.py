# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from ..parser import Tree


class Preprocessor:
    """
    Performs additional transformations before the tree is compiled.
    """

    @staticmethod
    def magic_line(block):
        """
        Creates a virtual line number.
        """
        base = int(block.line()) - 1
        extension = str(uuid.uuid4().int)[:8]
        return '{}.{}'.format(base, extension)

    @staticmethod
    def magic_path(line):
        """
        Creates a virtual path tree.
        """
        path = '${}'.format(uuid.uuid4().hex[:8])
        return Tree('path', [Token('NAME', path, line=line)])

    @classmethod
    def magic_assignment(cls, line, value):
        """
        Creates a magic assignment tree, equivalent to: "$magic = value"
        """
        path = cls.magic_path(line)
        fragment = Tree('assignment_fragment', [Token('EQUALS', '='), value])
        return Tree('assignment', [path, fragment])

    @classmethod
    def inline_expression(cls, tree):
        """
        Processes an inline expression, removing it from the tree and replacing
        it with an equivalent virtual assignment.
        """
        for block in tree.find_data('block'):
            target_path = 'service_block.service.service_fragment.arguments'
            target = block.node(target_path)
            if target:
                if target.inline_expression:
                    line = cls.magic_line(block)
                    value = target.inline_expression.service
                    assignment = cls.magic_assignment(line, value)
                    block.insert(assignment)
                    target.replace(1, assignment.path)
        return tree

    @classmethod
    def process(cls, tree):
        tree = cls.inline_expression(tree)
        return tree
