# -*- coding: utf-8 -*-
from lark.lexer import Token
from lark.tree import Tree as LarkTree

from ..exceptions import CompilerError


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

    def first_child(self):
        """
        Return the first child
        """
        assert len(self.children) > 0
        return self.children[0]

    def last_child(self):
        """
        Return the first child
        """
        assert len(self.children) > 0
        return self.children[-1]

    def child(self, index):
        """
        Returns the child at the position of `index`.
        """
        assert len(self.children) > index
        return self.children[index]

    def find(self, path):
        """
        Wraps LarkTree.find_data, making it easier to use.
        """
        return list(self.find_data(path))

    def extract(self, node_name):
        """
        Extracts only direct children of a tree with the requested name
        """
        children = []
        for child in self.children:
            if child.data == node_name:
                children.append(child)
        return children

    def _find_position(self, position):
        """
        Finds the request positional attribute of a tree, by finding the
        first token its first token and returning the token's positional
        attribute
        """
        token = self.find_first_token()
        if token is not None:
            return str(getattr(token, position))
        return None

    def find_first_token(self):
        """
        Finds the first token in a tree
        """
        for child in self.children:
            if isinstance(child, Token):
                return child
            return child.find_first_token()

    def line(self):
        """
        Finds the line number of a tree using _find_position
        """
        return self._find_position('line')

    def column(self):
        """
        Finds the column number of a tree using _find_position
        """
        return self._find_position('column')

    def end_column(self):
        """
        Finds the end column number of a tree using _find_position
        """
        return self._find_position('end_column')

    def insert(self, item):
        """
        Inserts an item into the current tree.
        """
        self.children.insert(0, item)

    def rename(self, new_name):
        """
        Renames the current tree
        """
        self.data = new_name

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

    def expect(self, cond, error, **kwargs):
        """
        Throws a compiler error with message if the condition is falsy.
        """
        if not cond:
            raise CompilerError(error, tree=self, format=kwargs)

    def follow_node_chain(self, expected_nodes):
        """
        Checks whether all expected nodes can be seen in the tree.
        Returns the lowest expected node if all expected nodes and
        no other nodes have been observed, `None` otherwise.
        """
        if len(self.children) != 1:
            return None
        it = self.iter_subtrees()
        exp = reversed(expected_nodes)
        # save path for efficiency
        path = next(it)
        if path.data != next(exp):
            return None
        while True:
            p = next(it, None)
            e = next(exp, None)
            if p is None and e is None:
                return path
            if p is None or e is None:
                return None
            if p.data != e:
                return None

    def child_token(self, index, name):
        """
        Returns a child and ensures its a Token of type `name`.
        """
        child = self.child(index)
        assert isinstance(child, Token)
        assert child.type == 'NAME'
        return child

    def __getattr__(self, attribute):
        return self.node(attribute)
