# -*- coding: utf-8 -*-
from .Faketree import FakeTree
from ..parser.Tree import Tree


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
            # only generate a fake_block once for every line
            # node: block in which the fake assignments should be inserted
            block = cls.fake_tree(node)
        elif node.data == 'entity':
            # set the parent where the inline_expression path should be
            # inserted
            entity = node
        elif node.data == 'service' and node.child(0).data == 'path':
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

            # split services into service calls and mutations
            if entity.data == 'service':
                entity.data = 'mutation'
                entity.entity = Tree('entity', [entity.path])
                entity.service_fragment.data = 'mutation_fragment'

    @staticmethod
    def is_inline_expression(n):
        return hasattr(n, 'data') and n.data == 'inline_expression'

    @classmethod
    def process(cls, tree):
        pred = Preprocessor.is_inline_expression
        cls.visit(tree, None, None, pred, cls.replace_expression)
        return tree
