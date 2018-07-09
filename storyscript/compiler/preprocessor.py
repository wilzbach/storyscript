# -*- coding: utf-8 -*-
import uuid

from lark.lexer import Token

from ..parser import Tree


class Preprocessor:

    @staticmethod
    def inline_expression(tree):
    @staticmethod
    def magic_path(line):
        path = '${}'.format(uuid.uuid4().hex[:8])
        return Tree('path', [Token('NAME', path, line=line)])

        return tree

    @classmethod
    def process(cls, tree):
        tree = cls.inline_expression(tree)
        return tree
