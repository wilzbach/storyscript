# -*- coding: utf-8 -*-
from .Faketree import FakeTree


class Preprocessor:
    """
    Performs additional transformations that can't be performed, or would be
    too complicated for the Transformer, before the tree is compiled.
    """

    @staticmethod
    def fake_tree(block):
        """
        Get a fake tree
        """
        return FakeTree(block)

    @classmethod
    def replace_expression(cls, node, fake_tree, entity):
        """
        Replaces an inline expression with a fake assignment
        """
        line = entity.line()
        assignment = fake_tree.add_assignment(node.service)

        # find parent node to replace
        entity.path.replace(0, assignment.path.child(0))
        # fix-up the line
        entity.path.children[0].line = line

    @classmethod
    def visit(cls, node, block, entity, pred, fun):
        if not hasattr(node, 'children') or len(node.children) == 0:
            return

        if node.data == 'block':
            # the block in which the fake assignments should be inserted
            block = node
            # only generate a fake_block once for every line
            block = cls.fake_tree(block)
        elif node.data == 'entity':
            # set the parent where the inline_expression path should be
            # inserted
            entity = node

        for c in node.children:
            cls.visit(c, block, entity, pred, fun)

        if pred(node):
            assert entity is not None
            assert block is not None
            fake_tree = block
            if not isinstance(fake_tree, FakeTree):
                fake_tree = cls.fake_tree(block)

            # Evaluate from leaf to the top
            fun(node, fake_tree, entity)

    @staticmethod
    def is_inline_expression(n):
        return hasattr(n, 'data') and n.data == 'inline_expression'

    @classmethod
    def process(cls, tree):
        pred = Preprocessor.is_inline_expression
        cls.visit(tree, None, None, pred, cls.replace_expression)
        return tree
