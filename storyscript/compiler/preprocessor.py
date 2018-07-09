# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from ..parser import Tree


class Preprocessor:

    @staticmethod
    def inline_expression(tree):
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

        return tree

    @classmethod
    def process(cls, tree):
        tree = cls.inline_expression(tree)
        return tree
