# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from ..version import version


class Tree(LarkTree):
    """
    Wraps the original Tree class from lark, providing many useful
    enhancements.
    """

    @staticmethod
    def walk(tree, path):
        for item in tree.children:
            if isinstance(item, Tree):
                if item.data == path:
                    return item

    @staticmethod
    def from_name(tree_name, subtree):
        """
        Creates a tree from a name
        """
        tree = None
        shards = tree_name.split('.')
        for shard in shards[::-1]:
            if tree:
                tree = Tree(shard, [tree])
            else:
                tree = Tree(shard, [])
                inner_tree = tree
        inner_tree.children = [subtree]
        return tree

    @classmethod
    def from_value(cls, value):
        """
        Creates a tree from value, or returns the value when not possible
        """
        if isinstance(value, dict):
            return cls.from_dict(value)
        return value

    @classmethod
    def from_dict(cls, dictionary):
        """
        Create a tree from a dictionary
        """
        for key, value in dictionary.items():
            subtree = cls.from_value(value)
            return cls.from_name(key, subtree)

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
        if len(self.children) > index:
            return self.children[index]

    def find(self, path):
        """
        Wraps LarkTree.find_data, making it easier to use.
        """
        return list(self.find_data(path))

    def line(self):
        """
        Finds the line number of a tree, by finding the first token in the tree
        and returning its line
        """
        for child in self.children:
            if isinstance(child, Token):
                return str(child.line)
            return child.line()

    def insert(self, item):
        """
        Inserts an item into the current tree.
        """
        self.children.insert(0, item)

    def replace(self, index, item):
        """
        Replaces a child at the given index
        """
        self.children[index] = item

    def extract_path(self):
        """
        Extracts the path name from a path tree
        """
        string = ''
        for child in self.children:
            if isinstance(child, Tree):
                string = '{}.{}'.format(string, child.child(0).value)
            else:
                string += child.value
        return string

    def __getattr__(self, attribute):
        return self.node(attribute)
