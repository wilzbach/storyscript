# -*- coding: utf-8 -*-


class Preprocessor:

    @staticmethod
    def inline_expression(tree):
        return tree

    @classmethod
    def process(cls, tree):
        tree = cls.inline_expression(tree)
        return tree
