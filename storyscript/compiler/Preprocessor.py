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
    def replace_expression(cls, node, fake_tree, insert_point):
        """
        Inserts `node` as a new like with a fake path reference.
        Then, replaces the first child of the insert_point
        with this path reference.
        """
        line = insert_point.line()
        # generate a new assignment line
        # insert it above this statement in the current block
        # return a path reference
        child_node = None
        if node.service is not None:
            child_node = node.service
        elif node.call_expression is not None:
            assert node.call_expression is not None
            child_node = node.call_expression
        else:
            assert node.mutation is not None
            child_node = node.mutation

        fake_path = fake_tree.add_assignment(child_node, original_line=line)

        # Replace the inline expression with a fake_path reference
        insert_point.replace(0, fake_path.child(0))

    @classmethod
    def visit(cls, node, block, entity, pred, fun, parent):
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

        # create fake lines for base_expressions too, but only when required:
        # 1) `expressions` are already allowed to be nested
        # 2) `assignment_fragments` are ignored to avoid two lines for simple
        #    service/mutation assignments (`a = my_service command`)
        if node.data == 'base_expression' and \
                node.child(0).data != 'expression' and \
                parent.data != 'assignment_fragment':
            # replace base_expression too
            fun(node, block, node)
            node.children = [Tree('path', node.children)]

        for c in node.children:
            cls.visit(c, block, entity, pred, fun, parent=node)

        if pred(node):
            assert entity is not None
            assert block is not None
            fake_tree = block
            if not isinstance(fake_tree, FakeTree):
                fake_tree = cls.fake_tree(block)

            # Evaluate from leaf to the top
            fun(node, fake_tree, entity.path)

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
        cls.visit(tree, None, None, pred, cls.replace_expression, parent=None)
        return tree
