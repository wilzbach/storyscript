# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from ..version import version


class Tree(LarkTree):

    @staticmethod
    def walk(tree, path):
        for item in tree.children:
            if item.data == path:
                return item

    def node(self, path):
        """
        Finds a subtree or a nested subtree, using path
        """
        shards = path.split('.')
        current = None
        for shard in shards:
            if current is None:
                current = self.walk(self, shard)
            else:
                current = self.walk(current, shard)
        return current

    def child(self, index):
        return self.children[index]
